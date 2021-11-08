使用第三方库 loguru，[参考文档](https://cloud.tencent.com/developer/article/1521386), [官方使用手册](https://buildmedia.readthedocs.org/media/pdf/loguru/stable/loguru.pdf)

在 loguru 里面**有且仅有一个**主要对象 (logger)，而且它已经被提前配置了一些基础信息，比如比较友好的格式化、文本颜色信息等等

loguru 对输出到文件的配置有非常强大的支持，比如**支持输出到多个文件，分级别分别输出，过大创建新文件，过久自动删除**等等

## add 方法重要参数

```python
def add(
        self,
        sink,
        *,
        level=_defaults.LOGURU_LEVEL,
        format=_defaults.LOGURU_FORMAT,
        filter=_defaults.LOGURU_FILTER,
        colorize=_defaults.LOGURU_COLORIZE,
        serialize=_defaults.LOGURU_SERIALIZE,
        backtrace=_defaults.LOGURU_BACKTRACE,
        diagnose=_defaults.LOGURU_DIAGNOSE,
        enqueue=_defaults.LOGURU_ENQUEUE,
        catch=_defaults.LOGURU_CATCH,
        **kwargs
    ):
    pass
```

使用范例
```python
logger.add("interface_log_{time}.log", rotation="500MB", encoding="utf-8", enqueue=True, compression="zip", retention="10 days")
```
### sink
支持多种不同类型的对象
- str   常用，代表输出的log文件的路径
- pathlib.Path 对象
#### 删除sink
```python
from loguru import logger

trace = logger.add('runtime.log')
logger.remove(trace)
```
### enqueue
enqueue=True 代表异步写入, 在多进程同时往日志文件写日志的时候使用队列达到异步功效

### compression
压缩格式，常见的格式 zip、tar、gz、tar.gz

### level
最低的日志级别，如 `level='INFO'` 会记录 info 和 error 的日志，而不会记录 debug

## 输出到多个日志
借助 add 方法的 filter 参数实现。filter 可以是一个函数，返回类型是布尔值。使用例子见[官方手册](https://buildmedia.readthedocs.org/media/pdf/loguru/stable/loguru.pdf)

```python
# 只保留 debug 级别的记录
logger.add("debug.log", filter=lambda record: record["level"].name == "DEBUG")
```

## 自动分割日志
```python
logger.add('runtime_{time}.log', rotation="500 MB")  # log 文件大小超过500MB就会新创建一个log文件
logger.add('runtime_{time}.log', rotation='00:00')   # 每天 0 点新创建一个 log 文件
logger.add('runtime_{time}.log', rotation='1 week')  # 一周创建一个 log 文件
```

## 过久自动删除
```python
logger.add('runtime.log', retention='10 days')  # 日志文件最长保留 10 天
```

## 异常追踪
用它提供的装饰器就可以直接进行 Traceback 的记录，如果遇到运行错误会自动记录, 而且会输出当时的变量值

```python
@logger.catch
def div(a, b):
    return a/b

div(0, 0)
```
输出
```
2021-11-02 11:20:50.773 | ERROR    | __main__:<module>:26 - An error has been caught in function '<module>', process 'MainProcess' (79362), thread 'MainThread' (4457758208):
Traceback (most recent call last):

> File "/Users/audrey/Documents/GitHub/xiaoven/codegex/utils/log_config.py", line 26, in <module>
    div(0, 0)
    └ <function div at 0x7fe56b70cf70>

  File "/Users/audrey/Documents/GitHub/xiaoven/codegex/utils/log_config.py", line 7, in div
    return a/b
           │ └ 0
           └ 0

ZeroDivisionError: division by zero
```