import json
import os
from abc import ABC, abstractmethod
from typing import List

from talkse.embedding import OpenAIEmbedding
from talkse.utils import get_easyDict_from_filepath


class MemoryBase(ABC):
    def __init__(self, directory: str) -> None:
        self.directory: str = directory

        cfg = get_easyDict_from_filepath("./ecl/config.yaml")
        self.top_k_code = cfg.retrieval.top_k_code
        self.top_k_text = cfg.retrieval.top_k_text
        self.code_thresh = cfg.retrieval.searchcode_thresh
        self.text_thresh = cfg.retrieval.searchtext_thresh
        self.embedding_method = None

        if cfg.embedding_method == "OpenAI":
            self.embedding_method = OpenAIEmbedding()

        self.content = None
        if os.path.exists(self.directory) and self.directory.endswith('.json'):
            with open(self.directory) as file:
                self.content = json.load(file)
        elif os.path.exists(self.directory) is False:
            with open(self.directory, 'w') as file:
                json.dump({}, file)  # Create an empty JSON file
            file.close()
            print(f"Now the memory file '{self.directory}' is created")
        if self.content is None:
            print("Empty Memory")

    @abstractmethod
    def memory_retrieval(self) -> str:
        pass


    def _get_memory_count(self) ->int:
        if isinstance(self.content,list):
            return self.content[-1].get("total")
        else:
            return 0


class AllMemory(MemoryBase):
    def __init__(self, directory: str):
        super().__init__(directory)

class Memory:
    def __init__(self):
        self.directory: str = None # 存储记忆相关数据的目录路径
        self.id_enabled : bool = False
        self.user_memory_filepath: str = None # 用户记忆文件路径
        self.assistant_memory_filepath: str = None # 助手记忆文件路径

        self.update_count = 0 # 记忆数据的更新次数
        self.memory_keys: List[str] = ["All"] # 包含记忆数据的键列表
        self.memory_data = {} # 以字典形式存储记忆数据

    # create memory path and upload memory from existed memory
    def upload(self):
        self.directory = os.path.join(os.getcwd(),"ecl","memory")
        if os.path.exists(self.directory) is False:
            os.mkdir(self.directory)
        for key in self.memory_keys:
            if key =="All":
                path = os.path.join(self.directory,"MemoryCards.json")
                self.memory_data[key] = AllMemory(path)