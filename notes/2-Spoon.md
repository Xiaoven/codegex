# SourcePosition
**目标**：获取 AST node 对应的行号

[Position官方描述](https://spoon.gforge.inria.fr/comments.html)

## 类型
```
SourcePosition (spoon.reflect.cu)
    CompoundSourcePosition (spoon.reflect.cu.position)
        DeclarationSourcePosition (spoon.reflect.cu.position)
            BodyHolderSourcePosition (spoon.reflect.cu.position)
                BodyHolderSourcePositionImpl (spoon.support.reflect.cu.position)
            DeclarationSourcePositionImpl (spoon.support.reflect.cu.position)
                BodyHolderSourcePositionImpl (spoon.support.reflect.cu.position)
        CompoundSourcePositionImpl (spoon.support.reflect.cu.position)
            DeclarationSourcePositionImpl (spoon.support.reflect.cu.position)
                BodyHolderSourcePositionImpl (spoon.support.reflect.cu.position)
    NoSourcePosition (spoon.reflect.cu.position)
        PartialSourcePositionImpl (spoon.support.reflect.cu.position)
    SourcePositionImpl (spoon.support.reflect.cu.position)
        CompoundSourcePositionImpl (spoon.support.reflect.cu.position)
            DeclarationSourcePositionImpl (spoon.support.reflect.cu.position)
                BodyHolderSourcePositionImpl (spoon.support.reflect.cu.position)
```

## 观察
观察到单行的sourceStartline属性都为-1，但是getLine方法会对它进行处理（调用searchLineNumber方法根据offset搜）

### NoSourcePosition
唯一的子类是 `PartialSourcePosition` 不支持 `getLine()` 调用

观察到一般是源代码没有写的对象会有这种类型的position，比如隐式/默认的空参构造方法(CtConstructor)和super()调用

### DeclarationSourcePosition
- CtField 有comments和annotations成员变量，sourceStartline 不包括它们的范围
- CtAnonymousExecutable 如static初始化块, 多行，但sourceStartline 为 -1
