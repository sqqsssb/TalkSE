import importlib
import json
import os
import shutil

from camel.agents.role_playing import RolePlaying
from camel.configs import ChatGPTConfig
from camel.typing import ModelType, TaskType
from camel.web_spider import modal_trans
from talkse.chat_env import ChatEnvConfig, ChatEnv
from talkse.utils import now


def check_bool(s):
    return s.lower() == "true"

class ChatChain:
    def __init__(self,
                 config_path: str = None,
                 config_phase_path: str = None,
                 config_role_path: str = None,
                 task_prompt: str = None,
                 project_name: str = None,
                 org_name: str = None,
                 model_type: ModelType = ModelType.GPT_3_5_TURBO,
                 code_path: str = None
                 ):
        """
        Args:
            config_path：指向 ChatChainConfig.json 文件的路径。
            config_phase_path：指向 PhaseConfig.json 文件的路径。
            config_role_path：指向 RoleConfig.json 文件的路径。
            task_prompt：用户输入的软件任务提示。
            project_name：用户输入的软件名。
            org_name：用户所属组织的名称。
            model_type：实际的模型标识符。
            code_path：现有代码路径, TalkSE将以增量开发模式对现有代码进行修改。
        """

        # 加载配置文件
        self.config_path = config_path
        self.config_phase_path = config_phase_path
        self.config_role_path = config_role_path
        self.project_name = project_name
        self.org_name = org_name
        self.model_type = model_type
        self.code_path = code_path

        with open(self.config_path, 'r', encoding="utf8") as file:
            self.config = json.load(file)
        with open(self.config_phase_path, 'r', encoding="utf8") as file:
            self.config_phase = json.load(file)
        with open(self.config_role_path, 'r', encoding="utf8") as file:
            self.config_role = json.load(file)

        # init chat_chain config and recruitments
        self.chain = self.config["chain"]
        self.recruitments = self.config["recruitments"]
        self.web_spider = self.config["web_spider"]

        # init default max chat turn
        self.chat_turn_limit_default = 10

        # init ChatEnv
        self.chat_env_config = ChatEnvConfig(clear_structure=check_bool(self.config["clear_structure"]),
                                             gui_design=check_bool(self.config["gui_design"]),
                                             git_management=check_bool(self.config["git_management"]),
                                             incremental_develop=check_bool(self.config["incremental_develop"]),
                                             background_prompt=self.config["background_prompt"],
                                             with_memory=check_bool(self.config["with_memory"]))

        self.chat_env = ChatEnv(self.chat_env_config)

        # the user input prompt will be self-improved (if set "self_improve": "True" in ChatChainConfig.json)
        # the self-improvement is done in self.preprocess
        self.task_prompt_raw = task_prompt
        self.task_prompt = ""

        # init role prompts
        self.role_prompts = dict()
        for role in self.config_role:
            self.role_prompts[role] = "\n".join(self.config_role[role])

        # init log
        self.start_time, self.log_filepath = self.get_logfilepath()

        # init SimplePhase instances
        # import all used phases in PhaseConfig.json from talkse.phase
        # note that in PhaseConfig.json there only exist SimplePhases
        # ComposedPhases are defined in ChatChainConfig.json and will be imported in self.execute_step
        self.compose_phase_module = importlib.import_module("talkse.composed_phase")
        self.phase_module = importlib.import_module("talkse.phase")
        self.phases = dict()
        for phase in self.config_phase:
            assistant_role_name = self.config_phase[phase]['assistant_role_name']
            user_role_name = self.config_phase[phase]['user_role_name']
            phase_prompt = "\n\n".join(self.config_phase[phase]['phase_prompt'])
            phase_class = getattr(self.phase_module, phase) # 从 talkse.phase 模块中获取名称为 phase 的类
            phase_instance = phase_class(assistant_role_name=assistant_role_name,
                                         user_role_name=user_role_name,
                                         phase_prompt=phase_prompt,
                                         role_prompts=self.role_prompts,
                                         phase_name=phase,
                                         model_type=self.model_type,
                                         log_filepath=self.log_filepath)
            self.phases[phase] = phase_instance

    def get_logfilepath(self):
        """
        get the log path (under the software path)
        Returns:
            start_time: time for starting making the software
            log_filepath: path to the log
        """
        start_time = now()
        filepath = os.path.dirname(__file__)
        # root = "/".join(filepath.split("/")[:-1])
        root = os.path.dirname(filepath)
        # directory = root + "/WareHouse/"
        directory = os.path.join(root, "WareHouse")
        log_filepath = os.path.join(directory,
                                    "{}.log".format("_".join([self.project_name, self.org_name, start_time])))
        return start_time, log_filepath

    def pre_processing(self):
        """
        remove useless files and log some global config settings
        Returns: None
        """
        filepath = os.path.dirname(__file__)
        root = os.path.dirname(filepath)
        directory = os.path.join(root, "WareHouse") # 仓库目录

        if self.chat_env.config.clear_structure:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # logs with error trials are left in WareHouse/
                if os.path.isfile(file_path) and not filename.endswith(".py") and not filename.endswith(".log"):
                    os.remove(file_path)
                    print("{} Removed.".format(file_path))

        software_path = os.path.join(directory, "_".join([self.project_name, self.org_name, self.start_time]))
        self.chat_env.set_directory(software_path)

        if self.chat_env.config.with_memory is True:
            self.chat_env.init_memory()

        # copy config files to software path
        shutil.copy(self.config_path, software_path)
        shutil.copy(self.config_phase_path, software_path)
        shutil.copy(self.config_role_path, software_path)

        # 增量开发模式
        # copy code files to software path in incremental_develop mode
        if check_bool(self.config["incremental_develop"]):
            for root, dirs, files in os.walk(self.code_path):
                relative_path = os.path.relpath(root, self.code_path)
                target_dir = os.path.join(software_path, 'base', relative_path)
                os.makedirs(target_dir, exist_ok=True)
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    shutil.copy2(source_file, target_file)
            self.chat_env._load_from_hardware(os.path.join(software_path, 'base'))

        # write task prompt to software
        with open(os.path.join(software_path, self.project_name + ".prompt"), "w") as f:
            f.write(self.task_prompt_raw)

        preprocess_msg = "**[Preprocessing]**\n\n"
        chat_gpt_config = ChatGPTConfig()

        preprocess_msg += "**TalkSE Starts** ({})\n\n".format(self.start_time)
        preprocess_msg += "**Timestamp**: {}\n\n".format(self.start_time)
        preprocess_msg += "**config_path**: {}\n\n".format(self.config_path)
        preprocess_msg += "**config_phase_path**: {}\n\n".format(self.config_phase_path)
        preprocess_msg += "**config_role_path**: {}\n\n".format(self.config_role_path)
        preprocess_msg += "**task_prompt**: {}\n\n".format(self.task_prompt_raw)
        preprocess_msg += "**project_name**: {}\n\n".format(self.project_name)
        preprocess_msg += "**Log File**: {}\n\n".format(self.log_filepath)
        preprocess_msg += "**TalkSEConfig**:\n{}\n\n".format(self.chat_env.config.__str__())
        preprocess_msg += "**ChatGPTConfig**:\n{}\n\n".format(chat_gpt_config)
        # log_visualize(preprocess_msg)

        # init task prompt
        if check_bool(self.config['self_improve']):
            self.chat_env.env_dict['task_prompt'] = self.self_task_improve(self.task_prompt_raw)
        else:
            self.chat_env.env_dict['task_prompt'] = self.task_prompt_raw
        if check_bool(self.web_spider):
            self.chat_env.env_dict['task_description'] = modal_trans(self.task_prompt_raw)

    def self_task_improve(self, task_prompt):
        """
        ask agent to improve the user query prompt
        Args:
            task_prompt: original user query prompt

        Returns:
            revised_task_prompt: revised prompt from the prompt engineer agent
        """
        self_task_improve_prompt = """I will give you a short description of a software design requirement, 
please rewrite it into a detailed prompt that can make large language model know how to make this software better based this prompt,
the prompt should ensure LLMs build a software that can be run correctly, which is the most import part you need to consider.
remember that the revised prompt should not contain more than 200 words, 
here is the short description:\"{}\". 
If the revised prompt is revised_version_of_the_description, 
then you should return a message in a format like \"<INFO> revised_version_of_the_description\", do not return messages in other formats.""".format(
            task_prompt)
        role_play_session = RolePlaying(
            assistant_role_name="Prompt Engineer",
            assistant_role_prompt="You are an professional prompt engineer that can improve user input prompt to make LLM better understand these prompts.",
            user_role_prompt="You are an user that want to use LLM to build software.",
            user_role_name="User",
            task_type=TaskType.CHATDEV,
            task_prompt="Do prompt engineering on user query",
            with_task_specify=False,
            model_type=self.model_type,
        )

        # log_visualize("System", role_play_session.assistant_sys_msg)
        # log_visualize("System", role_play_session.user_sys_msg)

        _, input_user_msg = role_play_session.init_chat(None, None, self_task_improve_prompt)
        assistant_response, user_response = role_play_session.step(input_user_msg, True)
        revised_task_prompt = assistant_response.msg.content.split("<INFO>")[-1].lower().strip()
        # log_visualize(role_play_session.assistant_agent.role_name, assistant_response.msg.content)
        # log_visualize(
        #     "**[Task Prompt Self Improvement]**\n**Original Task Prompt**: {}\n**Improved Task Prompt**: {}".format(
        #         task_prompt, revised_task_prompt))
        return revised_task_prompt