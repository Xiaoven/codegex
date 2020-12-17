## BIT: Check for sign of bitwise operation

### Regex

```regex
\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*((?:(?&aux1)|[\w.])+)\s*\)\s*>\s*0
```

### Examples

```Java
CASE1 
if ((e.getChangeFlags() & e.PARENT_CHANGED) > 0)
CASE2    
if ((delta.getKind() & IResourceDelta.CHANGED) > 0 && (delta.getFlags() & IResourceDelta.MARKERS) > 0)
CASE3    
  int a = 1; int b = -1;
  Boolean test_var1 = (a&b)>0;
  int     test_var2 = -1;
  if(test_var1&& test_var2 >0){
            System.out.println("branch1");
  }
// (a&b)>0 will be matched, test_var1&& test_var2 >0 will not
```

### 实现思路

#### Spotbugs
```java
// arg1 和 arg2 可以为 null 或 Long 和 Integer 的  constant
if (arg1 == null || arg2 == null) { return; }
boolean isLong = arg1 instanceof Long;
// 当 Opcode 为 <, <=, >, >= 时，equality 为 false; 当 == 或 != 时，为 true
if (!equality && arg2.longValue() == 0) {
	// 看不懂以下三句在干什么
    long bits = getFlagBits(isLong, arg1.longValue());
    // 似乎是为了判断 arg1 是不是负数， 
    // 据观察，对 long 来说(64 bits)，大于等于 0x8000000000000000L 的是负数，0x7fffffffffffffffL 为最大的正数
    // 对 int 来说 (32 bits), 大于等于 0x80000000 的是负数， 0x7fffffff 为最大的正数
    // 而在 python 里，int('0x8000000000000000', 0) 转换出来的还是正数
    // 如何区分 int 和 long 呢？ 可以通过判断 constant 是否有后缀 'L' 实现。如果没有，则为 int 类型（不然编译不通过），和 int 的最大正数比较判断是否是负数
    // 如果给 int 类型赋超过 32 bits 的值，或者给 long 类型赋超过 64 bits 的值, Java 编译器都会报错; 
    // Java 编译器还要求 超过 32 bits 的 constant， 都要带 'L' 后缀
    boolean highbit = !isLong && (bits & 0x80000000) != 0 || isLong && bits < 0 && bits << 1 == 0;
    boolean onlyLowBits = bits >>> 12 == 0;
    BugInstance bug;
    if (highbit) {
    	// Const.IFLE 代表 <=, IFGT 为 >， 见 https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-6.html#jvms-6.5.ifge
        bug = new BugInstance(this, "BIT_SIGNED_CHECK_HIGH_BIT", (seen == Const.IFLE || seen == Const.IFGT) ? HIGH_PRIORITY: NORMAL_PRIORITY);
    } else {
        bug = new BugInstance(this, "BIT_SIGNED_CHECK", onlyLowBits ? LOW_PRIORITY : NORMAL_PRIORITY);
    }
```
相关方法
```java
static int populationCount(long i) {
        /* 
        1. Returns the number of one-bits in the two's complement binary representation of the specified long value. 即数给定的long值的二进制补码表示形式中，1的个数

        2. 正整数的补码是其二进制表示, 与原码相同, 例：+9的补码是00001001
        
        3. 负整数的补码，将其原码除符号位外的所有位取反（0变1，1变0，符号位为1不变）后加1. 
        	例：-5对应负数5（10000101）→所有位取反（11111010）→加00000001(11111011)
		*/
        return Long.bitCount(i);
    }

    static long getFlagBits(boolean isLong, long arg0) {
    	/*
    		如果 arg0 实际是 int，则把它转成 32-bit (0xffffffffL)
   
			返回 arg0 和 ~arg0 (即 arg0 全部取反)中，对应的二进制补码含 1 个数最多的那个
			但不知道有什么意义
    	*/
        long bits = arg0;
        if (isLong) {
            int a = populationCount(bits);
            long b = ~bits;
            int c = populationCount(b);
            if (a > c) {
                bits = ~bits;
            }
        } else if (populationCount(0xffffffffL & bits) > populationCount(0xffffffffL & ~bits)) {
            bits = 0xffffffffL & ~bits;
        }
        return bits;
    }
```

#### rbugs
