# 导入camel包下的各个子模块，这样在导入camel包时，这些子模块会被预先加载
# 后续可以通过camel.agents等方式直接访问子模块中的内容
import camel.typing

# 定义该包的版本号为0.1.0，外部代码可以通过camel.__version__来获取这个版本信息
__version__ = '0.1.0'

# 定义当使用from camel import * 这种导入方式时，允许导入的对象列表
# 这里指定了__version__和'camel'，意味着通过上述导入方式，只会导入版本号变量和'camel'相关内容
# 其他导入的子模块（如agents、configs等）不会被导入，除非在__all__列表中明确添加
__all__ = [
    '__version__',
    'camel',
]