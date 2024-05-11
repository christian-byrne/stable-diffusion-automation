import json
from urllib import request
import websocket
import uuid
from pathlib import Path
import time


class ComfyClient:
    """
    Represents a client for interacting with the Comfy server using a WebSocket connection.

    See: https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/websockets_api_example.py

    Args:
      workflow (Workflow): The workflow object representing the desired workflow to be executed. Required methods are get_workflow_dict() for returning the workflow json data as a dict and parse_node_name().
      server_url (str): The URL of the Comfy server. Defaults to "http://localhost".
      max_connect_attempts (int, optional): The maximum number of connection attempts to the Comfy server. Defaults to 10.
      port (int, optional): The port number to connect to the Comfy server. Defaults to 8188.

    Attributes:
      workflow (Workflow): The workflow object representing the desired workflow to be executed.
      port (int): The port number to connect to the Comfy server.
      server_url (str): The URL of the Comfy server.
      websock_url (str): The WebSocket URL of the Comfy server.
      client_id (str): The unique identifier for the client.
      __websocket (WebSocket): The WebSocket connection object.
      logfile_path (str): The path to the log file.

    Methods:
      log: Logs a message and writes it to the log file.
      is_connected: Checks if the client is currently connected to the server.
      connect: Connects to the Comfy server using a WebSocket connection.
      disconnect: Disconnects from the Comfy server by closing the WebSocket connection.
      queue_workflow: Queues a workflow by sending a request to the Comfy API server and waits for it to complete.
      __get_request_data: Returns the request data as a JSON-encoded string.
      __send_request: Sends a request to the Comfy API server.
      __handle_response_message: Handles the response message received from the server.
      __listen_until_complete: Listens for response messages until the workflow execution is complete.
    """

    def __init__(
        self,
        workflow,
        server_url: str = "http://localhost",
        max_connect_attempts: int = 10,
        port: int = 8188,
    ):
        self.workflow = workflow
        self.port = port
        self.max_connect_attempts = max_connect_attempts

        self.server_url = f"{server_url}:{port}"
        if "https" in self.server_url:
            self.websock_url = self.server_url.replace("https", "ws")
        elif "http" in self.server_url:
            self.websock_url = self.server_url.replace("http", "ws")
        else:
            self.websock_url = f"ws://{self.server_url}"

        self.client_id = str(uuid.uuid4())
        self.__websocket = None

        self.logfile_path = None

    def log(self, *args, **kwargs):
        # Add your own logging logic
        print(*args, **kwargs)

        if not self.logfile_path:
            self.logfile_path = (
                (Path(__file__).parent.parent)
                / "logs"
                / f"comfy_client_{time.strftime('%Y-%m-%d_%H:%M:%S')}.log"
            )
            with open(self.logfile_path, "w") as f:
                f.write(f"New Comfy Client Created with ID: {self.client_id}\n")

        with open(self.logfile_path, "a") as f:
            print(*args, **kwargs, file=f)

    def is_connected(self):
        """
        Check if the client is currently connected to the server.

        Returns:
            bool: True if the client is connected.
        """
        return self.__websocket is not None and self.__websocket.connected

    def connect(self):
        """
        Connects to the Comfy server using a WebSocket connection.
        Attempts to connect to the server every second, MAX_CONNECT_ATTEMPTS
        times.

        This is done because Comfy may take a long time to start up, but
        we don't want to wait any longer than necessary.

        Raises:
            ConnectionError: If the connection to the Comfy server fails.
        """
        self.__websocket = websocket.WebSocket()

        for attempt in range(self.max_connect_attempts):
            try:
                self.__websocket.connect(
                    f"{self.server_url.replace('https', 'ws')}:{self.port}/ws?clientId={self.client_id}",
                )
            except ConnectionRefusedError:
                self.log(
                    f"Connection Attempt {attempt + 1}/{self.max_connect_attempts}: Failed - Connection Refused"
                )
                time.sleep(1)
                continue

            if self.__websocket.connected:
                self.log(
                    "Comfy server connection attempt",
                    f"{attempt + 1}/{self.max_connect_attempts}:",
                    "Succeeded - connection established",
                )
                break

        if not self.__websocket.connected:
            raise ConnectionError("Failed to connect to Comfy server")

    def disconnect(self):
        """
        Disconnects from the Comfy server by closing the WebSocket connection.

        Returns:
            None
        """
        if self.is_connected():
            self.log("Disconnecting Client from Comfy server")
            self.__websocket.close()
        else:
            self.log("Disconnect Client Attempt: Client is already disconnected")

    def queue_workflow(self):
        """
        Queues a workflow by sending a request to the Comfy API server and waits for it to complete.

        If the client is not connected, it will establish a connection before queuing the workflow.

        Raises:
            Exception: If there is an error with the Comfy API Client process.

        Returns:
            None
        """
        if not self.is_connected():
            self.connect()

        try:
            start_time_epoch = time.time()
            self.log(f"Queueing Workflow at: {time.strftime('%I:%M%p')}")

            self.__send_request()
            self.__listen_until_complete()

            time_diff_formatted = time.strftime(
                "%Mmin, %Ssec", time.gmtime(time.time() - start_time_epoch)
            )
            self.log(
                f"Comfy server finished processing request at: {time.strftime('%I:%M%p')} (Time elapsed - {time_diff_formatted})"
            )

        except Exception as e:
            self.log(f"Error with Comfy API Client process: {e}")
            raise e
        finally:
            self.__websocket.close()

    def __get_request_data(self):
        return json.dumps(
            {"prompt": self.workflow.get_workflow_dict(), "client_id": self.client_id}
        ).encode("utf-8")

    def __send_request(self):
        req = request.Request(
            self.server_url + "/prompt", data=self.__get_request_data()
        )
        resp = json.loads(request.urlopen(req).read())
        self.response_prompt_id = resp["prompt_id"]

    def __handle_response_message(self, message):
        if message["type"] == "status":
            self.log(message["data"]["status"])
        elif message["type"] == "progress":
            # Can add progress bar printing here
            pass
        elif message["type"] == "executing":
            cur_node_name = self.workflow.parse_node_name(message["data"])
            self.log(f"Executing Node: {cur_node_name}")

            if (
                message["data"]["node"] is None
                and message["data"]["prompt_id"] == self.response_prompt_id
            ):
                return True  # Execution is done
        return False  # Previews are binary data

    def __listen_until_complete(self):
        while True:
            out = self.__websocket.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if self.__handle_response_message(message):
                    break
