# dev-ast@xiaoven

This branch is to introduce AST context into Codegex to detect more kinds of patterns and bug instances.

# Usage

TODO: 使用该工具检查的步骤

# Development
### Step 1: Download Dependencies
```shell
# install python dependencies
$ pip3 install -r requirements.txt

# download java libraries
$ cd utils/dependencies
$ ./download.sh
```

TODO: 开发该工具的步骤

# Notes

## 项目背景

SpotBugs 中有的 patterns 与 text 内容比较相关，根据正则是否能够完全支持其实现，可分为2类：

1.   只需要正则做 text 匹配就能实现，如 self assignment (`x = x;`)
2.   需要其它的context信息, 如 Comparison of String objects using == or != (`stringVar1 == stringVar2`)

对于第一种，我们希望 AST 能为其提供operand的类型信息，以检测到更多的bug instances；对于第二种，我们希望regex可以提供定位服务，确定需要对哪个可以的modified file进行AST parsing，然后执行基于AST的detectors，以检测更多的patterns。

因此，我们需要解决的问题如下：

1.   AST node 和 text 之间的 mapping，最好能通过 O(1) 的时间获取到对应的信息，如果是 O(N) 时间，还不如不用regex，全部基于扫描 AST 实现得了（N指 AST nodes 数）
2.   Parse 单个 file，参照 spotbugs 实现基于  AST 的 detectors

另外，除了 PRs 外，希望也能支持 commits 的检测（无法留言，但是可以用于做实验或本地检测）

## 框架设计

1.   Parser 服务
     -   基于 diff 的 statement parser (fuzzy parsing)
     -   针对single file 的 AST parser
2.   Mapping 服务
     -   根据 line number 快速定位到对应的 AST
        - [spoon metadata graph](https://spoon.gforge.inria.fr/structural_elements.html)

3.   Detectors
     -   基于 regex 的 detectors
     -   基于 AST 的 detectors
     -   detectors的config功能（读取config文件实现, `detector_name: True`）
4.   Bug Instances
     -   优先级策略
     -   filter 功能 (根据 detector，priority)
5.   Github PR 留言功能
6.   utils
     -   常用方法封装 (是否要将utils.py按功能拆成不同文件)
     -   Internet 服务 （与GitHub API的交互服务）

## TODOs

-   [x] 检查流程设计
    -   先进行 regex-detectors 的检查，通过 regex-detectors invoke 对应的 ast detectors
    -   [x] 参考 spotbugs、pmd 等工具的流程
    -   spoon AST 提供的 visitor 模式： CtScanner 类
-   parsers
     - [x] AST parser 选择：spoon (java写的，比较靠谱)
          - [ ] python调用java库：[JPype](https://jpype.readthedocs.io/en/latest/)
          
          - [x] spoon 编译单个java文件的可行性
            ```java
            CtClass clazz = Launcher.parseClass("public class A {}");
            ```
            
          - [x] AST node的位置属性：SourcePosition类，有getLine方法，也有offset
          
              ```java
                      List<CtElement> ll = clazz.getDirectChildren();
                      for (CtElement element : ll) {
                          SourcePosition sp = element.getPosition();
                          if (!(sp instanceof NoSourcePosition)) {
                              int start = sp.getLine();
                              int end = sp.getEndLine();
                              System.out.printf("start %d\tend %d\n", start, end);
                          }
                      }
              ```
          
              
- 代码重构
    - config：enable detectors，filters
    - service:
        - config：增量更新、重置

## 疑惑

1.   AST能拿到method call的signature吗


## Mapping
## SourcePosition 调查
[官方描述](https://spoon.gforge.inria.fr/comments.html)

似乎单行的sourceStartline属性都为-1，但是getLine方法会对它进行处理（调用searchLineNumber方法根据offset搜）

### SourcePositionImpl
- CtJavaDoc 多行的 comment sourceStartline 不为 -1
- CtAnnotation 单行的 sourceStartline 为 -1
- CtIf 为 -1
- CtBlock 为 -1
### NoSourcePosition
- CtConstructor 默认的，即源代码没有写的
### DeclarationSourcePosition
- CtField 有comments和annotations成员变量，sourceStartline 不包括它们的范围
- CtAnonymousExecutable 如static初始化块, 多行，但sourceStartline 为 -1
- CtLocalVariable 本地变量赋值，根据 defaultExpression 可以访问右边的 expression
### BodyHolderSourcePosition
可以通过body下的statements访问所属的statement
- CtClass
- CtMethod

### PartialSourcePosition
super() 不能调用 getPosition().getLine()  unsupportedOperationExeception

[ ] CtMethod, CtField, CtExpression 的 getDirectChildren是什么类型，
- CtMethod 的 directChild 是返回值类型(CtTypeReference), CtBlock, CtJavaDoc(注释)、CtParameter等
- CtExpression
- CtAssignment 的 directChild 是类型(CtTypeReference)、CtFieldWrite 变量名、CtLiteral (e.g. true)
[ ] expression的getLine方法和它所属的statement一样吗？
  
CtConstructor 是 CtStatement 的子类型，而 CtMethod 却不是。它们俩的共同父类型是 CtExecutable