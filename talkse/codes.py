import re

class Codes:
    # 管理和组织生成的代码，方便后续对代码进行存储、查找等操作
    def __init__(self, generated_content=""):
        self.directory: str = None # 代码相关目录路径
        self.version: float = 0.0 # 代码版本，初始为 0.0
        self.generated_content: str = generated_content # 传入的生成代码内容
        self.codebooks = {} # 存放解析整理后的代码，键为文件名，值为对应的代码内容

        def extract_filename_from_line(lines):
            file_name = ""
            for candidate in re.finditer(r"(\w+\.\w+)", lines, re.DOTALL):
                file_name = candidate.group()
                file_name = file_name.lower()
            return file_name

        def extract_filename_from_code(code):
            file_name = ""
            regex_extract = r"class (\S+?):\n"
            matches_extract = re.finditer(regex_extract, code, re.DOTALL)
            for match_extract in matches_extract:
                file_name = match_extract.group(1)
            file_name = file_name.lower().split("(")[0] + ".py"
            return file_name

        if generated_content != "":
            regex = r"(.+?)\n```.*?\n(.*?)```"
            matches = re.finditer(regex, self.generated_content, re.DOTALL)
            for match in matches:
                code = match.group(2)
                if "CODE" in code:
                    continue
                group1 = match.group(1)
                filename = extract_filename_from_line(group1)
                if "__main__" in code:
                    filename = "main.py"
                if filename == "":  # post-processing
                    filename = extract_filename_from_code(code)
                assert filename != ""
                if filename is not None and code is not None and len(filename) > 0 and len(code) > 0:
                    self.codebooks[filename] = self._format_code(code)