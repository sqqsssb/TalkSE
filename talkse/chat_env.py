import os
import shutil
import time
from typing import Dict

from talkse.codes import Codes
from talkse.documents import Documents
from talkse.memory import Memory
from talkse.roster import Roster


class ChatEnvConfig:
    def __init__(self,
                 clear_structure,
                 gui_design,
                 git_management,
                 incremental_develop,
                 background_prompt,
                 with_memory):
        self.clear_structure = clear_structure  # Whether to clear non-software files in the WareHouse and cache files in generated software path
        self.gui_design = gui_design  # Encourage ChatDev generate software with GUI
        self.git_management = git_management  # Whether to use git to manage the creation and changes of generated software
        self.incremental_develop = incremental_develop  # Whether to use incremental develop on an existing project
        self.background_prompt = background_prompt  # background prompt that will be added to every inquiry to LLM
        self.with_memory = with_memory # Whether to use memory in the interaction between agents

    def __str__(self):
        string = ""
        string += "ChatEnvConfig.with_memory: {}\n".format(self.with_memory)
        string += "ChatEnvConfig.clear_structure: {}\n".format(self.clear_structure)
        string += "ChatEnvConfig.git_management: {}\n".format(self.git_management)
        string += "ChatEnvConfig.gui_design: {}\n".format(self.gui_design)
        string += "ChatEnvConfig.incremental_develop: {}\n".format(self.incremental_develop)
        string += "ChatEnvConfig.background_prompt: {}\n".format(self.background_prompt)
        return string

class ChatEnv:
    def __init__(self, chat_env_config: ChatEnvConfig):
        self.config = chat_env_config
        self.roster: Roster = Roster()
        self.codes: Codes = Codes()
        self.memory: Memory = Memory()
        self.proposed_images: Dict[str, str] = {} # 提议的图像信息
        self.incorporated_images: Dict[str, str] = {} # 已整合的图像信息
        self.requirements: Documents = Documents()
        self.manuals: Documents = Documents()
        self.env_dict = {
            "directory": "",
            "task_prompt": "",
            "task_description":"",
            "modality": "",
            "ideas": "",
            "language": "",
            "review_comments": "",
            "error_summary": "",
            "test_reports": ""
        }

    def set_directory(self, directory):
        assert len(self.env_dict['directory']) == 0
        self.env_dict['directory'] = directory
        self.codes.directory = directory
        self.requirements.directory = directory
        self.manuals.directory = directory

        if os.path.exists(self.env_dict['directory']) and len(os.listdir(directory)) > 0:
            new_directory = "{}.{}".format(directory, time.strftime("%Y%m%d%H%M%S", time.localtime()))
            shutil.copytree(directory, new_directory)
            print("{} Copied to {}".format(directory, new_directory))
        if os.path.exists(self.env_dict['directory']):
            shutil.rmtree(self.env_dict['directory'])
            os.mkdir(self.env_dict['directory'])
            print("{} Created".format(directory))
        else:
            os.mkdir(self.env_dict['directory'])

    def init_memory(self):
        self.memory.id_enabled = True
        self.memory.directory = os.path.join(os.getcwd(),"ecl","memory")
        if not os.path.exists(self.memory.directory):
            os.mkdir(self.memory.directory)
        self.memory.upload()

    def _load_from_hardware(self, directory) -> None:
        self.codes._load_from_hardware(directory)