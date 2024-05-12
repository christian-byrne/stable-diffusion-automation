import subprocess
from urllib import request, error
from pathlib import Path
import time
import logging


class ComfyServer:
    """
    Represents an instance of ComfyUI, which acts as a server with an API that clients can interact with and queue workflows through.

    Args:
      output_directory (Path): The path to the output directory where generated images are saved.
      input_directory (Path): The path to the input directory where input images are taken from (e.g., for a Load Image node or img2img workflow).
      comfy_path (Path): The path to the ComfyUI installation directory.
      python_path (Path): The path to the Python executable.
      server_url (str): The URL of the server. Set to http://localhost if running on the same machine.
      port (int): The port number to run the server on. Iterate if running multiple server processes. Defaults to 8188.

    Attributes:
      comfy_launcher_target (Path): The path to the Comfy launcher target.
      logfile_path (Path): The path to the log file.
      log_stream (File): The log file stream.
      server_process (subprocess.Popen): The server process.
      pid (int): The process ID of the server process.

    Methods:
      log: Logs a message.
      start: Starts the Comfy server.
      kill: Stops the Comfy server.
    """

    def __init__(
        self,
        output_directory: Path,
        input_directory: Path,
        comfy_path: Path,
        python_path: Path,
        server_url: str,
        port: int = 8188,
    ):
        self.output_directory = output_directory
        self.input_directory = input_directory
        self.comfy_path = comfy_path
        self.python_path = python_path
        self.port = port

        self.server_url = f"{server_url}:{port}"
        self.server_process = None
        self.log_stream = None
        self.pid = None
        self.comfy_launcher_target = comfy_path / "main.py"

        self.__setup_logging()
        self.log(
            "This is the command that will be used to start the ComfyUI server process:\n"
            + f"{' '.join(self.__get_comfy_cli_args())}\n"
        )

    def log(self, *args, **kwargs):
        """
        Logs a message to the log file.

        Args:
          *args: The message to log.
          **kwargs: Additional keyword arguments to pass to the logging function.

        Returns:
          None
        """
        logging.info(*args, **kwargs)

    def start(self):
        """
        Starts the Comfy server.

        This method launches the process for the Comfy server and logs a message
        indicating that the server has started. If an exception occurs during the
        process launch, an error message is logged and the server is killed.

        Raises:
          Exception: If an error occurs during the process launch.

        Returns:
          None
        """
        try:
            self.__launch_process()
            self.log("Server started\n")
        except Exception as e:
            self.log(f"Error starting comfy server: {e}")
            self.kill()

    def kill(self):
        """
        Terminates the server process and waits for it to finish.
        Closes the log stream.

        If the server process exists, it will be terminated and the method will wait
        for the process to finish. If the server process does not exist, a log message
        will be printed indicating that there is no server to stop.
        """
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            log_msg = "Server stopped"
        else:
            log_msg = "Disconnect Attempt: No ComfyUI server process to kill"
        # Close the log stream before logging from separate process
        self.__close_log_stream()
        self.log(log_msg)

    def __get_comfy_cli_args(self):
        """
        Get the command-line arguments for running the Comfy CLI.
        See all available arguments in the Comfy CLI documentation:
        https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/cli_args.py

        Returns:
          list: A list of command-line arguments.
        """
        return [
            str(self.python_path),
            str(self.comfy_launcher_target),
            "--port",
            str(self.port),
            "--output-directory",
            str(self.output_directory),
            "--input-directory",
            str(self.input_directory),
            "--disable-auto-launch",
            "--disable-metadata",
        ]

    def __setup_logging(self):
        self.logfile_path = (
            (Path(__file__).parent.parent)
            / "logs"
            / f"comfy_server_{time.strftime('%Y-%m-%d_%H:%M:%S')}.log"
        )
        self.logfile_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            format="[Server Process %(process)d] [%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            handlers=[
                logging.FileHandler(self.logfile_path),
                logging.StreamHandler(),
            ],
        )

    def __set_log_stream(self):
        """
        Returns:
          File: The log file stream.
        """
        self.log_stream = open(str(self.logfile_path), "a")
        return self.log_stream

    def __close_log_stream(self):
        if (
            self.log_stream
            and "closed" in dir(self.log_stream)
            and not self.log_stream.closed
        ):
            self.log_stream.close()

    def __launch_process(self):
        """
        Launches the server process.

        This method checks if the server is already running by making a request to the server URL.
        If the server is already running, it logs a message and returns.
        If the server is not running, it starts a new server in a detached process and redirects
        the output to the server log file.

        Returns:
          None
        """
        try:
            with request.urlopen(self.server_url) as f:
                if f.status == 200:
                    self.log(f"Server already running on port {self.port} - Connecting")
                    return
        except (error.URLError, error.HTTPError, KeyError):
            self.log(
                f"No existing server on port {self.port}. Starting detached server process"
            )

        log = self.__set_log_stream()
        self.server_process = subprocess.Popen(
            self.__get_comfy_cli_args(),
            stderr=log,
            stdout=log,
            start_new_session=True,
        )
        self.pid = self.server_process.pid
