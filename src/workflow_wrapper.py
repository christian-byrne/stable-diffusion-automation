import json
from pathlib import Path
import time

class ComfyAPIWorkflow:
  def __init__(
    self,
    workflow_template_path: Path,
    name: str,
  ):
    """
    Initializes a ComfyAPIWorkflow instance. The workflow should be a JSON file that was saved using
    the "Save as API" option in the Comfy UI. Normal workflows will not work.

    Args:
      workflow_template_path (Path): The path to the workflow template JSON file (API version).
      project_name (str): The name of the project.

    Attributes:
      workflow_template_path (Path): The path to the workflow template JSON file.
      name (str): The name of the workflow, if saving a new version to disk.
      filename (str): The name of the workflow file.
      workflows_dir (Path): The directory where the workflow file is located.
      path (Path): The full path to the workflow file.
      logfile_path (Path): The path to the log file.
      workflow_dict (dict): The workflow data.

    Raises:
      FileNotFoundError: If the workflow template JSON file could not be found at the given path.
    """
    self.workflow_template_path = workflow_template_path
    self.project_name = name

    self.filename = workflow_template_path.name.replace(".json", "") + f"-{self.project.name}.json"
    self.workflows_dir = workflow_template_path.parent
    self.path = self.workflows_dir / self.filename

    self.__set_workflow()
    self.__set_node_mappings()
    self.save()
    
    self.logfile_path = None
    self.log(
      "Created Copy in Project Dir of Workflow Template:",
      self.workflow_template_path,
    )

  def log(self, *args, **kwargs):
    """
    Logs the provided arguments to the console and the log file.

    Args:
      *args: Variable length argument list.
      **kwargs: Arbitrary keyword arguments.
    """
    # Add your own logging logic
    print(*args, **kwargs)
    
    if not self.logfile_path:
      self.logfile_path = (Path(__file__).parent.parent) / "logs" / f"comfy_workflow_wrapper_{int(time.time())}.log"
      with open(self.logfile_path, "w") as f:
        f.write(f"Comfy Workflow Instance Created at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    with open(self.logfile_path, "a") as f:
      print(*args, **kwargs, file=f)

  def save(self):
    """
    Saves the workflow dictionary to the workflow file.
    """
    with open(self.path, "w") as workflow_file:
      json.dump(self.workflow_dict, workflow_file, indent=4)

  def update(
    self, node_name: str, key: str, value: any, save_after=False, append=False
  ) -> None:
    """
    Update one of the inputs of a node in the workflow dict.

    Args:
      node_name (str): The name of the node to update (either its title or class_type).
      key (str): The name of the input field to update.
      value (any): The new value to put in the input field.
      save_after (bool, optional): Whether to save the workflow to the disk after updating.
        Defaults to False.
      append (bool, optional): Whether to append the new value to the existing value.

    Raises:
      ValueError: If the node does not exist in the provided template workflow.
      KeyError: If the key does not exist in the workflow node.
    """
    if node_name in self.__node_titles:
      index = self.__node_titles[node_name]
    elif node_name in self.__node_class_types:
      index = self.__node_class_types[node_name]
    else:
      raise ValueError(
        "Project Workflow Error:",
        f"The node {node_name} does not exist in the provided template workflow",
      )

    if "image" in key.lower():
      print(
        "\nKeep in mind that the image inputs are just filenames, not full paths.",
        "The path is assumed to be the comfy input image directory"
        "(which should be manually set to whatever folder you need before passing this workflow to a comfy client)\n",
        sep="\n"
      )
    if key not in self.workflow_dict[index]["inputs"].keys():
      raise KeyError(
        "Project Workflow Error:",
        f"The key {key} does not exist in the workflow node {node_name}",
      )

    if self.workflow_dict[index]["inputs"][key] == value:
      self.log(
        f"{node_name}'s {key} value is already set to: {value}",
      )
      return

    if append:
      self.log(
        f"{node_name}'s {key} Value Appended with:",
        value,
      )
      # Try to add a space between the old and new value
      try:
        self.workflow_dict[index]["inputs"][key] += " " + value
      except TypeError:
        self.workflow_dict[index]["inputs"][key] += value
    else:
      self.log(
        f"Updating {node_name}'s {key} value:",
        f"from {self.workflow_dict[index]['inputs'][key]} to {value}",
      )
      self.workflow_dict[index]["inputs"][key] = value
    if save_after:
      self.save()

  def get_workflow_dict(self):
    """
    Returns the workflow dictionary.

    Returns:
      dict: The workflow dictionary.
    """
    return self.workflow_dict

  def parse_node_name(self, data):
    """
    Accepts the data dict from a response from the comfy server and returns the name of the node that the data is about.
    Allows errors, in which case returns "Unknown".

    Args:
      data (dict): The data dict from a response from the comfy server.

    Returns:
      str: The name of the node or "Unknown".
    """
    node_index = str(data["node"])
    try:
      node_name = self.workflow_dict[node_index]["_meta"]["title"]
    except KeyError:
      try:
        node_name = self.workflow_dict[node_index]["class_type"]
      except KeyError:
        node_name = "Unknown"
    return node_name

  def __set_workflow(self):
    """
    Sets the workflow dictionary by loading the workflow template JSON file.
    
    Raises:
      FileNotFoundError: If the workflow template JSON file could not be found at the given path.
    """
    try:
      with open(self.workflow_template_path, "r") as workflow_file:
        self.workflow_dict = json.load(workflow_file)
    except FileNotFoundError:
      raise FileNotFoundError(
        f"The passed workflow template json file could not be found at the given path: {self.workflow_template_path}"
      )

  def __set_node_mappings(self):
    """
    Sets the node mappings for quick access to nodes by title or class_type.
    """
    self.__node_titles = {}
    self.__node_class_types = {}

    for node_index, node in self.workflow_dict.items():
      if "_meta" in node.keys() and "title" in node["_meta"].keys():
        self.__node_titles[node["_meta"]["title"]] = node_index
      if "class_type" in node.keys():
        self.__node_class_types[node["class_type"]] = node_index
