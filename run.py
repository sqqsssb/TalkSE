import argparse
import logging
import os.path
import sys

from camel.typing import ModelType
from talkse.chat_chain import ChatChain

# --------------------------------------
print("__file:  " + __file__)
# root 为当前脚本run.py的目录路径
root = os.path.dirname(__file__)
print("root:    " + root)
# 将当前脚本所在的目录添加到 Python 的模块搜索路径中，以便能够更方便地导入同一目录下的其他模块
sys.path.append(root)
# ----------------------------------------

def get_config(config):
    """
    return configuration json files for TalkSE
    user can customize only parts of configuration json files, other files will be left for default
    Args:
        config: customized configuration name under Config/

    Returns:
        path to three configuration jsons: [config_path, config_phase_path, config_role_path]
    """
    config_dir = os.path.join(root, "Config", config)
    # print(config_dir)TalkSE\Config\Default
    default_config_dir = os.path.join(root, "Config", "Default")
    # print(default_config_dir)TalkSE\Config\Default

    config_files = [
        "ChatChainConfig.json",
        "PhaseConfig.json",
        "RoleConfig.json"
    ]

    config_paths = []

    for config_file in config_files:
        config_file_path = os.path.join(config_dir, config_file)
        default_config_path = os.path.join(default_config_dir, config_file)

        if os.path.exists(config_file_path):
            config_paths.append(config_file_path)
        else:
            config_paths.append(default_config_path)

    return tuple(config_paths)
# ----------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default="Default",
                    help="配置文件夹的名字，默认为Default")
parser.add_argument('--org', type=str, default="DefaultOrganization",
                    help="您的组织名org，软件生成路径：WareHouse/name_org_timestamp")
parser.add_argument('--task', type=str, default="say hi in python.",
                    help="软件的prompt")
parser.add_argument('--name', type=str, default="hello",
                    help="软件名name，软件生成路径：WareHouse/name_org_timestamp")
parser.add_argument('--model', type=str, default="GPT_4O_MINI",
                    help="使用的GPT模型,可用模型：'GPT_3_5_TURBO', 'GPT_4', 'GPT_4_TURBO', 'GPT_4O', 'GPT_4O_MINI'")
parser.add_argument('--path', type=str, default="",
                    help="现有代码路径, TalkSE将以增量开发模式对现有代码进行修改")
args= parser.parse_args()
# ----------------------------------------

# Start TalkSE

# ----------------------------------------
#          Init ChatChain
# ----------------------------------------
# print(args.config)
config_path, config_phase_path, config_role_path = get_config(args.config)
# print(config_path)TalkSE\Config\Default\ChatChainConfig.json
# print(config_phase_path)TalkSE\Config\Default\PhaseConfig.json
# print(config_role_path)TalkSE\Config\Default\RoleConfig.json
args2type = {'GPT_3_5_TURBO': ModelType.GPT_3_5_TURBO_NEW,
             'GPT_4': ModelType.GPT_4,
             'GPT_4_TURBO': ModelType.GPT_4_TURBO,
             'GPT_4O': ModelType.GPT_4O,
             'GPT_4O_MINI': ModelType.GPT_4O_MINI,
             }
chat_chain = ChatChain(config_path=config_path,
                       config_phase_path=config_phase_path,
                       config_role_path=config_role_path,
                       task_prompt=args.task,
                       project_name=args.name,
                       org_name=args.org,
                       model_type=args2type[args.model],
                       code_path=args.path)

# ----------------------------------------
#          Init Log
# ----------------------------------------
logging.basicConfig(filename=chat_chain.log_filepath, level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%d-%m %H:%M:%S', encoding="utf-8")

# ----------------------------------------
#          Pre Processing
# ----------------------------------------

chat_chain.pre_processing()

# ----------------------------------------
#          Personnel Recruitment
# ----------------------------------------
