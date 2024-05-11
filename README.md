Automate comfyui workflows by starting a detached comfyui process and sending commands to it via a websocket. Start as many clients and servers as desired. Load edit, save, and queue workflows dynamically with the workflow wrapper. Can be used to make a backend for a webapp that wants to do stable diffusion things or to simply automate comfyui stuff.

See the ***NOTE*** about saving API version of workflow json files in the [Workflows](#workflows) section.

If doing iterative/loopback things, see the ***NOTE*** about setting the `INPUT_DIRECTORY` in the [Constants](#constants) section.

## Requirements/Dependencies

- websocket

## Usage

1. Change the constants in [main.py](main.py)
   - See the [Constants](#constants) section for more information.
2. Run `python main.py`

## Workflows

When saving a workflow to serve as the template, make sure to use the `Save (API Formatted)` button after you've checked `Enable Dev mode Options` in the settings.

**Why is there an entire wrapper Class for workflows?**

Maybe you run this program in the backend of a webapp, and you want to edit node input values based on user input. Or maybe you have a program that must change node input values depending on the output of another program. The wrapper also helps provide meaningful log/error messages for fixing problems that are otherwise hard to debug.


## Constants

- `PYTHON_PATH`
  - `pathlib.Path` to the python executable. [How do I find my python installation path?](https://blog.enterprisedna.co/where-is-python-installed/)
- `COMFY_PATH`
  - (pathlib.Path) Path of the ComfyUI source directory that you cloned/downloaded. E.g., `"/home/user/ComfyUI"` or `"C:\\Users\\user\\ComfyUI"`
- `OUTPUT_DIRECTORY`
  - (pathlib.Path) Path of the directory where you want to save the generated pictures. 
  - When using ComfyUI normally, this is the `output` directory in the comfyui source directory.
- `INPUT_DIRECTORY`
  - (pathlib.Path) Path of the directory where the ComfyUI process should look for input files (for example, when using the Load Image node or doing img2img things). 
  - When using ComfyUI normally, this is the `input` directory in the comfyui source directory. 
  - ***NOTE***: If you are automating a process in which you generate images and then use those images as inputs for another queued workflow, you should set the `INPUT_DIRECTORY` to  `OUTPUT_DIRECTORY` of the previous workflow. 
    - If you're not creating multiple clients, simply set `INPUT_DIRECTORY` to `OUTPUT_DIRECTORY`.
- `SERVER_URL`
  - (str) The URL of the comfyui server. E.g., `"http://localhost"` 
- `MAX_CONNECT_ATTEMPTS`
  - (int) The maximum number of times a client will attempt to connect to the server before giving up. 
- `WORKFLOW_NAME`
  - (str) The name to give the workflow instance, if you are making changes to the workflow and want to save a new version to disk. Will save in the same directory as the template workflow.
- `WORKFLOW_TEMPLATE_PATH`
  - (pathlib.Path) The path to the template workflow (API version) json file. E.g., `"/home/user/ComfyUI/workflows/img2img-inpaint-API.json"`
