from enum import Enum

class TaskType(Enum):
    AI_SOCIETY = "ai_society"
    CODE = "code"
    MISALIGNMENT = "misalignment"
    TRANSLATION = "translation"
    EVALUATION = "evaluation"
    SOLUTION_EXTRACTION = "solution_extraction"
    CHATDEV = "chat_dev"
    DEFAULT = "default"

class ModelType(Enum):
    # GPT_3_5_TURBO = "gpt-3.5-turbo-16k-0613"
    GPT_3_5_TURBO_NEW = "gpt-3.5-turbo-16k"
    GPT_4 = "gpt-4"
    GPT_4_32k = "gpt-4-32k"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_TURBO_V = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

    STUB = "stub"

    @property
    # 将value_for_tiktoken方法转换为属性，调用时无需括号（如model.value_for_tiktoken）
    def value_for_tiktoken(self):
        return self.value if self.name != "STUB" else "gpt-4o"