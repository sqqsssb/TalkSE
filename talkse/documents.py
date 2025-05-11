import re

class Documents():
    def __init__(self, generated_content = "", parse = True, predifined_filename = None):
        self.directory: str = None # 文档相关目录路径
        self.generated_content = generated_content # 传入的生成文档内容
        self.docbooks = {} # 以字典形式存储文档，键为文件名，值为文档内容

        if generated_content != "":
            if parse:
                regex = r"```\n(.*?)```"
                matches = re.finditer(regex, self.generated_content, re.DOTALL)
                for match in matches:
                    filename = "requirements.txt"
                    doc = match.group(1)
                    self.docbooks[filename] = doc
            else:
                self.docbooks[predifined_filename] = self.generated_content