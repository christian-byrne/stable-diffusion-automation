Automate Stable Diffusion tasks by starting a detached ComfyUI process and sending commands to its API via a websocket. Start as many clients and servers as desired using different ports and system processes. Load, edit, and save workflows dynamically. Can be used for the backend of a webapp that uses stable diffusion or simply for automation.

If doing iterative/loopback things, see ***NOTE*** about setting the `INPUT_DIRECTORY` in [Constants](#constants) section.

Gladly welcome fork and PR for any improvements or bug fixes.Have only tested on Ubuntu 23.10 + Nvidia GPU + python3.10.6 and on a linux server.

--------

**Table of Contents**:
- [Usage](#usage)
- [Requirements/Dependencies](#requirementsdependencies)
- [Example Output](#example-output)
- [Params for Client, Server, and Workflow Classes](#params-for-client-server-and-workflow-classes)
- [Workflows](#workflows)


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
This is the command that will be used to start the ComfyUI server process:
~/.pyenv/versions/3.10.6/bin/python3 ~/sd/sd-interfaces/ComfyUI/main.py --port 8188 --output-directory ~/sd/comfy-ui-automation/output --input-directory ~/sd/sd-interfaces/ComfyUI/input --disable-auto-launch --disable-metadata

Created Copy of Workflow Template in ~/stable-diffusion-automation/workflows

[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] New Client - ID: b20b9d51-bf76-4fc7-9c63-356dd92e0d67

No existing server on port 8188. Starting detached server process
[Server Process 195800] Server started

[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 1/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 2/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 3/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 4/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 5/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 6/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 7/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 8/12: Failed - Connection Refused
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Connection Attempt 9/12: Succeeded - Connection Established

[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Queueing Workflow at: 05:37PM
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] {'exec_info': {'queue_remaining': 0}}
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] {'exec_info': {'queue_remaining': 1}}
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] {'exec_info': {'queue_remaining': 1}}
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: Load Checkpoint
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: CLIP Text Encode (Positive Prompt)
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: CLIP Text Encode (Negative Prompt)
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: Empty Latent Image
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: KSampler
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: VAE Decode
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Executing Node: Save Image
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] {'exec_info': {'queue_remaining': 0}}
[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] ComfyUI Server finished processing request at: 05:37PM (Time elapsed - 00min, 02sec)

[Client b20b9d51-bf76-4fc7-9c63-356dd92e0d67] Disconnect Client Attempt: Client is already disconnected

[Server Process 195800] Server stopped
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

