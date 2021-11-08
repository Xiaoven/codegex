## 使用pathlib代替os.path
适用于 Python 3.4 之后
[功能对应表](https://www.dongwm.com/post/use-pathlib/#和os功能对应的方法列表)
[官方文档](https://docs.python.org/zh-cn/3.7/library/pathlib.html?highlight=pathlib#module-pathlib)

```python
from pathlib import Path
# 获取上级目录，并移动，等同于 ../dependencies/jars
JARS_PATH = dependenciesPath = Path.cwd().parent / 'dependencies' / 'jars'
```

但是 `Path.cwd()` 返回值跟执行入口相关，不适用于上述场景。假如在 tests/unit_tests/utils 下 import ast_helper，执行测试，
会找不到 spoon，经打印，发现`Path.cwd()` 返回的路径是 `tests/unit_tests/utils`。 `__file__` 宏与执行入口无关。