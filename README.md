# rbugs
A light-weight tool like spotbugs

## Selected Patterns

[单行多行分类](https://docs.google.com/spreadsheets/d/1aiYDHrQTci_ih8k-YIuSYZqYCnjTwvZHN3zOKpXv5zQ/edit?usp=sharing)

[Bad Practice例子](https://docs.google.com/presentation/d/1LT1VbDGkFMNARI54cV1zKUBHeN0wc-OSX4BLhUc3ieg/edit?usp=sharing)

[Correctness](https://docs.google.com/presentation/d/1mAIUuQgVncQWGuD7QwHzvduCaMhBQygl4KkkZVBOiBs/edit?usp=sharing)

[其它例子](https://docs.google.com/presentation/d/1cC30HDjKWqpbYAxNSyR_pTEAzpOLncFgn7WD0XfQSj4/edit?usp=sharing)

[Spotbugs Pattern Descriptions](https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html)

## 已有代码解释

1.  `main.py` 

    实现patterns后，会爬取状态为open的pull requests，用我们的detectors检测它，如果有触发warnings，则到对应的pull request下留言说：该pull request存在...问题。

    这部分由张晓文负责，**其他人暂时不需要管**。

2.  `rparser.py`

    只需要**会用即可**，只会用到`parse()` 方法。具体使用例子看各个tests文件，用法很简单。在Pycharm的Structure窗口可以查看它包含的3个classes，或者在debug模式下可以看到它是如何分割输入的patch String的。

## 实现规范

1.  在 spotbugs 搜索 pattern 的缩写名，Code>Java下会有implementation和test files的链接  [example](https://github.com/spotbugs/spotbugs/search?l=Java&q=CNT_ROUGH_CONSTANT_VALUE)

2.  在 rbugs 下**新建你的实现文件**

    如对于 `spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRoughConstants.java`, 则新建 `rbugs/patterns/detect/find_rough_constants.py`. 

    因为有的patterns比较相关，可以放在同一个file里。**class 名字**可以参考spotbugs里的

3.  在`implementation_notes`下新建你的 markdown 文件，以后每实现一个pattern，都在这个文件记录如下内容

    ```markdown
    #### PATTERN_NAME
    ##### Regex
    正则表达式1
    正则表达式2
    ...
    ##### Examples
    正则表达式可以匹配的字符串的例子
    ##### 实现思路
    ...
    ```

4.  测试

    -   测试文件命名：如 `find_rough_constants.py` 对应的测试文件名为 `test_find_rough_constants.py`

    -   测试用例命名规范：如 `test_PATTEN_NAME_01` 、`test_PATTEN_NAME_02` ...

    -   测试用例注释规范：有以下3种情况

        ```python
        # From spotBugs: https://xxx
        def test_PATTEN_NAME_01():
          pass
        
        # From other repository: https://xxx
        def test_PATTEN_NAME_02():
          pass
        
        # DIY
        def test_PATTEN_NAME_03():
          pass
        ```

        