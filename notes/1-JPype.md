# 引入JARs
1. `classpath` 可以使用绝对路径或者相对路径，使用相对路径的时候，是相对当前`.py`文件所在的位置（易错点）
2. 确保第三方库 (本项目是 spoon) 所依赖的库也被引入
    - 自动下载依赖的办法来自[JPype Github Issue](https://github.com/jpype-project/jpype/issues/1002#issuecomment-924596536)，使用了 ivy 来管理依赖
        - [maven](https://stackoverflow.com/questions/7110114/how-to-simply-download-a-jar-using-maven) 和 gradle 也有类似的将依赖下载为 JARs 的功能，但不能指定下载位置，或需要在 Java 项目里执行，所以选择了 ivy
    - 对应的配置文件和自动化脚本在 [utils/dependencies](utils/dependencies)目录下

```python
import jpype.imports
jpype.startJVM(classpath="dependencies/jars/*")
# ...
jpype.shutdownJVM()
```

查看是否成功导入了JARs

```python
print(jpype.java.lang.System.getProperty("java.class.path"))
```

输出示例：
```
dependencies/jars/slf4j-simple-1.7.30.jar:dependencies/jars/commons-io-2.8.0.jar:dependencies/jars/jackson-core-2.12.3.jar:dependencies/jars/slf4j-api-1.7.30.jar:dependencies/jars/jsap-2.1.jar:dependencies/jars/org.eclipse.jdt.core-3.25.0.jar:dependencies/jars/maven-model-3.8.1.jar:dependencies/jars/plexus-utils-3.2.1.jar:dependencies/jars/commons-compress-1.20.jar:dependencies/jars/maven-shared-utils-3.3.3.jar:dependencies/jars/maven-invoker-3.1.0.jar:dependencies/jars/commons-lang3-3.12.0.jar:dependencies/jars/spoon-core-9.1.0-beta-9.jar:dependencies/jars/javax.inject-1.jar:dependencies/jars/jackson-annotations-2.12.3.jar:dependencies/jars/jackson-databind-2.12.3.jar
```

# import Java 类型
按照python的语法import，虽然PyCharm检测会报错，但其实是可以执行的

```python
import spoon.Launcher as Launcher
from spoon.reflect.cu.position import NoSourcePosition
from spoon.reflect.code import *
```

# 编程
JPype 负责帮忙引入Java第三方库，我们编程的时候还是用python

强制转换可怎么办？
```python
children = ((CtBodyHolder) node).getBody().getDirectChildren();
```