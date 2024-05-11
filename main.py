from pathlib import Path

from src.server import ComfyServer
from src.client import ComfyClient
from src.workflow_wrapper import ComfyAPIWorkflow

PYTHON_PATH = Path("/usr/bin/python3")
COMFY_PATH = Path("/home/c_byrne/tools/sd/sd-interfaces/ComfyUI")
OUTPUT_DIRECTORY = Path("/home/c_byrne/tools/sd/sd-interfaces/ComfyUI/output")
INPUT_DIRECTORY = Path("/home/c_byrne/tools/sd/sd-interfaces/ComfyUI/input")
SERVER_URL = "http://localhost"
MAX_CONNECT_ATTEMPTS = 10
WORKFLOW_NAME = "my_workflow"
WORKFLOW_TEMPLATE_PATH = Path(
    "/home/c_byrne/tools/sd/sd-interfaces/ComfyUI/workflows/template.json"
)


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
