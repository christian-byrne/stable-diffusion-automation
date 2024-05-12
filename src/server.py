import subprocess
from urllib import request, error
from pathlib import Path
import time


class ComfyServer:
    """
    Represents a Comfy server.

    Args:
      output_directory (Path): The path to the output directory.
      input_directory (Path): The path to the input directory.
      comfy_path (Path): The path to the Comfy installation directory.
      python_path (Path): The path to the Python executable.
      server_url (str): The URL of the server.
      port (int, optional): The port number to run the server on. Defaults to 8188.

    Attributes:
      output_directory (Path): The path to the output directory.
      input_directory (Path): The path to the input directory.
      comfy_path (Path): The path to the Comfy installation directory.
      python_path (Path): The path to the Python executable.
      port (int): The port number to run the server on.
      server_url (str): The URL of the server.
      comfy_launcher_target (Path): The path to the Comfy launcher target.
      logfile_path (Path): The path to the log file.

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
        self.pid = None
        self.comfy_launcher_target = comfy_path / "main.py"

        self.logfile_path = None
        self.log(
            "This is the command that will be used to start the ComfyUI server process:\n"
            + f"{' '.join(self.__get_comfy_cli_args())}\n"
        )

    def log(self, *args, **kwargs):
        # Add your own logging logic
        if self.pid:
            print(f"[Server Process {self.pid}]", *args, **kwargs)
        else:
            print(*args, **kwargs)

        if not self.logfile_path:
            self.logfile_path = (
                (Path(__file__).parent.parent)
                / "logs"
                / f"comfy_server_{time.strftime('%Y-%m-%d_%H:%M:%S')}.log"
            )
            with open(self.logfile_path, "w") as f:
                f.write(
                    f"New Comfy Server Created at {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                )

        with open(self.logfile_path, "a") as f:
            print(*args, **kwargs, file=f)

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

        If the server process exists, it will be terminated and the method will wait
        for the process to finish. If the server process does not exist, a log message
        will be printed indicating that there is no server to stop.
        """
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.log("Server stopped")
        else:
            self.log("Disconnect Attempt: No ComfyUI server process to kill")

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

        log = open(str(self.logfile_path), "a")
        self.server_process = subprocess.Popen(
            self.__get_comfy_cli_args(),
            stderr=log,
            stdout=log,
            start_new_session=True,
        )
        # make copy of the process id
        self.pid = self.server_process.pid
