class OpenAIEmbedding:
    def __init__(self, **params):
        self.code_prompt_tokens = 0
        self.text_prompt_tokens = 0
        self.code_total_tokens = 0
        self.text_total_tokens = 0

        self.prompt_tokens = 0
        self.total_tokens = 0