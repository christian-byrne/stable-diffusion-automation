Automate Stable Diffusion tasks by starting a detached ComfyUI process and sending commands to its API via a websocket. Start as many clients and servers as desired using different ports and system processes. Load, edit, and save workflows dynamically. Can be used for the backend of a webapp that uses stable diffusion or simply for automation.

If doing iterative/loopback things, see ***NOTE*** about setting the `INPUT_DIRECTORY` in the [Params for Client, Server, and Workflow Classes](#params-for-client-server-and-workflow-classes) section.

Gladly welcome fork/PR for any improvements or bug fixes. Have only tested on Ubuntu23 + python3.10.6/python3.11 and on a linux server.

--------

**Table of Contents**:
- [Usage](#usage)
- [Requirements/Dependencies](#requirementsdependencies)
- [Example Output](#example-output)
- [Params for Client, Server, and Workflow Classes](#params-for-client-server-and-workflow-classes)
- [Workflows](#workflows)
- [TODO](#todo)


## Usage

1. `pip install websocket-client`
2. Clone/install [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
3. Run ComfyUI and set up a workflow to serve as the template
4. Save the workflow as an API formatted json file
      - Make sure to use the `Save (API Formatted)` button after you've checked `Enable Dev mode Options` in the settings
5. Change the constants in [main.py](main.py) or write code that sets them dynamically
      - See the [Params for Client, Server, and Workflow Classes](#params-for-client-server-and-workflow-classes) section for more info about each constant
6. `cd` to the folder where this repo is cloned. Run `python3 main.py` or `python main.py`


## Requirements/Dependencies

- [websocket-client](https://websocket-client.readthedocs.io/en/latest/installation.html)
  - See [this](https://websocket-client.readthedocs.io/en/latest/faq.html#what-s-going-on-with-the-naming-of-this-library) if you have issues with package namespace or pyenv or virtual environments when trying to `import websocket` or if you import websocket and it doesn't have a `WebSocket` class. 
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and its dependencies

## Example Output

```
[16:50:56] [DEBUG] This is the command that will be used to start the ComfyUI server process:
~/.pyenv/versions/3.10.6/bin/python3 ~/sd/sd-interfaces/ComfyUI/main.py --port 8188 --output-directory ~/comfy-ui-automation/output --input-directory ~/sd/sd-interfaces/ComfyUI/input --disable-auto-launch --disable-metadata

[16:50:56] [INFO] [Workflow - my_workflow] Created Copy of Workflow Template in ~/comfy-ui-automation/workflows

[16:50:56] [INFO] [Client 004c5d63] New Comfy Client Created at 2024-05-12_16:50:56

[16:50:56] [INFO] No existing server on port 8188. Starting detached server process
[16:50:56] [INFO] [Server 64668] Server started on port 8188

[16:50:56] [DEBUG] [Client 004c5d63] Connection Attempt 1/12: Failed - Connection Refused
[16:50:57] [DEBUG] [Client 004c5d63] Connection Attempt 2/12: Failed - Connection Refused
[16:50:58] [DEBUG] [Client 004c5d63] Connection Attempt 3/12: Failed - Connection Refused
[16:50:59] [DEBUG] [Client 004c5d63] Connection Attempt 4/12: Failed - Connection Refused
[16:51:00] [DEBUG] [Client 004c5d63] Connection Attempt 5/12: Failed - Connection Refused
[16:51:01] [DEBUG] [Client 004c5d63] Connection Attempt 6/12: Failed - Connection Refused

[16:51:02] [INFO] [Client 004c5d63] Connection Attempt 7/12: Succeeded - Connection Established
[16:51:02] [INFO] [Client 004c5d63] Queueing Workflow at: 04:51PM

[16:51:02] [DEBUG] [Client 004c5d63] {'exec_info': {'queue_remaining': 0}}
[16:51:02] [DEBUG] [Client 004c5d63] {'exec_info': {'queue_remaining': 1}}
[16:51:02] [DEBUG] [Client 004c5d63] {'exec_info': {'queue_remaining': 1}}

[16:51:02] [INFO] [Client 004c5d63] Executing Node: Load Checkpoint
[16:51:02] [INFO] [Client 004c5d63] Executing Node: CLIP Text Encode (Prompt)
[16:51:03] [INFO] [Client 004c5d63] Executing Node: CLIP Text Encode (Prompt)
[16:51:03] [INFO] [Client 004c5d63] Executing Node: Empty Latent Image
[16:51:03] [INFO] [Client 004c5d63] Executing Node: KSampler
[16:51:04] [INFO] [Client 004c5d63] Executing Node: VAE Decode
[16:51:04] [INFO] [Client 004c5d63] Executing Node: Save Image

[16:51:04] [DEBUG] [Client 004c5d63] {'exec_info': {'queue_remaining': 0}}

[16:51:04] [INFO] [Client 004c5d63] ComfyUI Server finished processing request at: 04:51PM (Time elapsed - 00min, 02sec)
[16:51:04] [INFO] [Client 004c5d63] Disconnect Client Attempt: Client is already disconnected

[16:51:04] [INFO] [Server 64668] Server stopped
```

## Params for Client, Server, and Workflow Classes

- `PYTHON_PATH`
  - (pathlib.Path) Path of the exectuable for the python version that works with torch and ComfyUI on your system
  - [How do I find my python installation path?](https://blog.enterprisedna.co/where-is-python-installed/)
  - If using pyenv, you can find the path by running `pyenv which python`. E.g., `"/home/user/.pyenv/versions/3.10.6/bin/python3"`
- `COMFY_PATH`
  - (pathlib.Path) Path of the ComfyUI source directory that you cloned/downloaded. E.g., `"~/ComfyUI"` or `"C:\\Users\\username\\ComfyUI"`
- `OUTPUT_DIRECTORY`
  - (pathlib.Path) Path of the directory where you want to save the generated pictures. 
  - When using ComfyUI normally, this is the `output` folder in the ComfyUI source directory.
- `INPUT_DIRECTORY`
  - (pathlib.Path) Path of the directory where the ComfyUI process(es) should look for input files (for example, when using the Load Image node or doing img2img). 
  - When using ComfyUI normally, this is the `input` directory in the comfyui source directory. 
  - ***NOTE***: If you are automating a process in which you generate images and then use those images as inputs for another queued workflow, you should set the `INPUT_DIRECTORY` to  `OUTPUT_DIRECTORY` of the previous workflow. 
    - If you're not creating multiple clients, simply set `INPUT_DIRECTORY` to `OUTPUT_DIRECTORY`.
- `SERVER_URL`
  - (str) The URL of the comfyui server. E.g., `"http://localhost"` if running on the same machine and just using this for automation.
- `MAX_CONNECT_ATTEMPTS`
  - (int) The maximum number of times a client will attempt to connect to the server before giving up. Increase if system containing server is slow to start ComfyUI.
- `WORKFLOW_NAME`
  - (str) The name to give the workflow instance, if you are making changes to the workflow and want to save a new version to disk. Will save in the same directory as the template workflow.
- `WORKFLOW_TEMPLATE_PATH`
  - (pathlib.Path) The path to the template workflow (API version) json file. E.g., `"~/ComfyUI/workflows/img2img-inpaint-API.json"`.


## Workflows

Make sure to use the `Save (API Formatted)` button after you've checked `Enable Dev mode Options` in the settings.

**Why is there an entire wrapper Class for workflows?**

Maybe you run this program in the backend of a webapp, and you want to edit node input values based on user input. Or maybe you have a program that must change node input values depending on the output of another program. The wrapper also helps provide meaningful log/error messages for fixing problems that are otherwise hard to debug.


## TODO

- System testing
- Server/container testing
- Compress logs after limit reached
- More Workflow methods for dynamically adjusting values