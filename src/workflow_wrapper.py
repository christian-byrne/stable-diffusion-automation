import json
from pathlib import Path
import time
import logging


class ComfyAPIWorkflow:
    def __init__(
        self,
        workflow_template_path: Path,
        name: str = "copy",
        log_level: int = logging.DEBUG,
    ):
        """
        Initializes a ComfyAPIWorkflow instance. The workflow should be a JSON file that was saved using
        the "Save as API" option in the Comfy UI. Normal workflows will not work.

        Args:
          workflow_template_path (Path): The path to the workflow template JSON file (API version).
          name (str): The name of the workflow, if saving a new version to disk. Defaults to "copy".
          log_level (int, optional): The logging level (verbosity). Defaults to logging.DEBUG.

        Attributes:
          filename (str): The name of the workflow file.
          workflows_dir (Path): The directory where the workflow files are located.
          path (Path): The full path to the workflow file.
          workflow_dict (dict): The workflow data.

        Methods:
          save: Saves a new copy of the workflow as a json file in the same directory as the template.
          update: Update one of the inputs of a node in the workflow dict.
          get_workflow_dict: Returns the workflow as a dict.
          parse_node_name: Accepts the data dict from a response from the comfy server and returns the name of the node that the data is about.

        Raises:
          FileNotFoundError: If the workflow template JSON file could not be found at the given path.
        """
        self.workflow_template_path = workflow_template_path
        self.name = name

        self.filename = (
            workflow_template_path.name.replace(".json", "") + f"-{self.name}.json"
        )
        self.workflows_dir = workflow_template_path.parent
        self.path = self.workflows_dir / self.filename

        self.__set_workflow()
        self.__set_node_mappings()
        self.save()

        self.logger = logging.getLogger("Workflow")
        self.logger.setLevel(log_level)
        self.__setup_logging()
        self.logger.info(
            f"Created Copy of Workflow Template in {self.workflow_template_path.parent}\n"
        )

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
            self.logger.warning(
                "Keep in mind that the image inputs are just filenames, not full paths."
                + "\nThe path is assumed to be the comfy input image directory"
                + "\n(which should be manually set to whatever folder you need before passing this workflow to a comfy client)\n"
            )
        if key not in self.workflow_dict[index]["inputs"].keys():
            raise KeyError(
                "Project Workflow Error:",
                f"The key {key} does not exist in the workflow node {node_name}",
            )

        if self.workflow_dict[index]["inputs"][key] == value:
            self.logger.warning(
                f"{node_name}'s {key} value is already set to: {value}",
            )
            return

        if append:
            self.logger.info(f"{node_name}'s {key} Value Appended with: {value}")
            # Try to add a space between the old and new value
            try:
                self.workflow_dict[index]["inputs"][key] += " " + value
            except TypeError:
                self.workflow_dict[index]["inputs"][key] += value
        else:
            self.logger.info(
                f"Updating {node_name}'s {key} value: from {self.workflow_dict[index]['inputs'][key]} to {value}"
            )
            self.workflow_dict[index]["inputs"][key] = value
        if save_after:
            self.save()

    def get_workflow_dict(self):
        """
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
                self.logger.debug(
                    f"Could not find the node name for node index {node_index} in the workflow dict"
                )
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

    def __setup_logging(self):
        self.__logfile_path = (
            (Path(__file__).parent.parent)
            / "logs"
            / f"comfy_workflow_{time.strftime('%Y-%m-%d_%H:%M:%S')}.log"
        )
        self.__logfile_path.parent.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s]"
            + f" [Workflow - {self.name}] "
            + "%(message)s",
            datefmt="%H:%M:%S",
        )
        filehandler = logging.FileHandler(self.__logfile_path)
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)

        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)
        self.logger.addHandler(streamhandler)
