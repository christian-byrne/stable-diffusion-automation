from pathlib import Path

from src.server import ComfyServer
from src.client import ComfyClient
from src.workflow_wrapper import ComfyAPIWorkflow


PYTHON_PATH = Path("/usr/bin/python3")
COMFY_PATH = Path("/home/user/ComfyUI")
OUTPUT_DIRECTORY = COMFY_PATH / "output"
INPUT_DIRECTORY = COMFY_PATH / "input"
SERVER_URL = "http://localhost"
MAX_CONNECT_ATTEMPTS = 25
WORKFLOW_NAME = "my_workflow"
WORKFLOW_TEMPLATE_PATH = COMFY_PATH / "workflows" / "template.json"

from src.dev_constants import *

def main():
    server = ComfyServer(
        output_directory=OUTPUT_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
        comfy_path=COMFY_PATH,
        python_path=PYTHON_PATH,
        server_url=SERVER_URL,
        port=8188,
    )
    client = ComfyClient(
        workflow=ComfyAPIWorkflow(
            workflow_template_path=WORKFLOW_TEMPLATE_PATH,
            name=WORKFLOW_NAME,
        ),
        server_url=SERVER_URL,
        max_connect_attempts=MAX_CONNECT_ATTEMPTS,
        port=8188,
    )
    server.start()
    client.connect()

    client.queue_workflow()

    client.disconnect()
    server.kill()


if __name__ == "__main__":
    main()
