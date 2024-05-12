import json
from urllib import request
import uuid
from pathlib import Path
import time
import logging

try:
    import websocket
except ImportError as e:
    print(
        "Please install the websocket-client package using",
        "'pip install websocket-client'",
        "or 'python3 -m pip install websocket-client'",
    )
    raise e


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
      websock_url (str): The WebSocket URL of the Comfy server.
      client_id (str): The unique identifier for the client.
      logfile_path (str): The path to the log file.

    Methods:
      connect: Connects to the Comfy server using a WebSocket connection.
      disconnect: Disconnects from the Comfy server by closing the WebSocket connection.
      queue_workflow: Queues a workflow by sending a request to the Comfy API server and waits for it to complete.
    """

    def __init__(
        self,
        workflow,
        server_url: str = "http://localhost",
        max_connect_attempts: int = 10,
        port: int = 8188,
        log_level: int = logging.DEBUG,
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
        self.client_id_truncated = self.client_id.split("-")[0]
        self.__websocket = None

        self.logger = logging.getLogger("Client")
        self.logger.setLevel(log_level)
        self.__setup_logging()
        self.logger.info(
            f"New Comfy Client Created at {time.strftime('%Y-%m-%d_%H:%M:%S')}\n"
        )

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
                    f"{self.websock_url}/ws?clientId={self.client_id}",
                )
            except ConnectionRefusedError:
                self.logger.debug(
                    f"Connection Attempt {attempt + 1}/{self.max_connect_attempts}: Failed - Connection Refused"
                )
                time.sleep(1)
                continue

            if self.__websocket.connected:
                self.logger.info(
                    f"Connection Attempt {attempt + 1}/{self.max_connect_attempts}: Succeeded - Connection Established\n"
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
            self.logger.info("Disconnecting Client from Comfy server\n")
            self.__websocket.close()
        else:
            self.logger.info(
                "Disconnect Client Attempt: Client is already disconnected\n"
            )

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
            self.logger.info(f"Queueing Workflow at: {time.strftime('%I:%M%p')}")

            self.__send_request()
            self.__listen_until_complete()

            time_diff_formatted = time.strftime(
                "%Mmin, %Ssec", time.gmtime(time.time() - start_time_epoch)
            )
            self.logger.info(
                f"ComfyUI Server finished processing request at: {time.strftime('%I:%M%p')} (Time elapsed - {time_diff_formatted})"
            )

        except Exception as e:
            self.logger.error(f"Error with Comfy API Client process: {e}")
            raise e
        finally:
            self.__websocket.close()

    def __get_request_data(self):
        return json.dumps(
            {"prompt": self.workflow.get_workflow_dict(), "client_id": self.client_id}
        ).encode("utf-8")

    def __send_request(self):
        req = request.Request(
            str(self.server_url) + "/prompt", data=self.__get_request_data()
        )
        resp = json.loads(request.urlopen(req).read())
        self.response_prompt_id = resp["prompt_id"]

    def __handle_response_message(self, message):
        if message["type"] == "status":
            self.logger.debug(message["data"]["status"])
        elif message["type"] == "progress":
            # Can add progress bar printing here
            pass
        elif message["type"] == "executing":
            cur_node_name = self.workflow.parse_node_name(message["data"])
            self.logger.info(f"Executing Node: {cur_node_name}")

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

    def __setup_logging(self):
        self.logfile_path = (
            (Path(__file__).parent.parent)
            / "logs"
            / f"comfy_client_{time.strftime('%Y-%m-%d_%H:%M:%S')}.log"
        )
        self.logfile_path.parent.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s]"
            + f" [Client {self.client_id_truncated}] "
            + "%(message)s",
            datefmt="%H:%M:%S",
        )
        filehandler = logging.FileHandler(self.logfile_path)
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)

        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)
        self.logger.addHandler(streamhandler)
