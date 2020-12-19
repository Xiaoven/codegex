## BIT_SIGNED_CHECK， BIT_SIGNED_CHECK_HIGH_BIT

### Regex

```regex
\(\s*([~-]?(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.-])++)\s*&\s*([~-]?(?:(?&aux1)|[\w.])++)\s*\)\s*([><=!]+)\s*0
```

### Examples

```Java
if ((e.getChangeFlags() & 0x8000000000000000L) > 0)
if ((x & ~0x10000000) > 0)
if ((-1 & x) > 0)
```

### 实现思路

#### Spotbugs
1. 由 `!equality && arg2.longValue() == 0` 可知，BIT_SIGN_CHECK 和 BIT_SIGN_CHECK_HIGH_BIT 针对 `((A & CONSTANT)) > 0`, `((A & CONSTANT)) >= 0`, `((A & CONSTANT)) < 0` 和 `((A & CONSTANT)) <= 0`.
2. 根据 `highBit` 和 `onlyLowBits` 的字面意思可以猜测，它们取决于 `arg1` 的二进制形式最高位的 1 在哪里，也就是 `arg1` 的大小。看了 `getFlagBits` 方法的代码后，我猜测大概是用来处理 long 和 int 这两种类型的，具体目的不明。
3. 接下来关注 high bit 和 low bit 的定义，即有多少个 bits 算是 high bit 或 low bit。我们可以找出几个临界值。

	- 从 `onlyLowBits = bits >>> 12 == 0`，我们可以判断二进制在 12 bits 以内的 `arg1` 会使得 `onlyLowBits` 为 true, 因为不考虑符号位，移除最低 12 bits 后，只剩下 0 了。于是第一个临界值为`0b1111 1111 1111`, 即4095。最后发现当 `-4096 <= arg1 <= 4095` 时，onlyLowBits 就会为 true，且 `highbit` 为 false，无论 long or int

	- 从 `highbit = !isLong && (bits & 0x80000000) != 0` 得当constant `arg1` 为 int，且它的最高位(第32位)为 1 时，`highbit` 为 true. `0x80000000` 对应的数字是 `2147483648L`, 但在 Java 中它们并不相等，但是 `0x80000000 == -2147483648` 是 true. 经试验，

		- 131071，即 `0x1ffff`（17个1,超32半数，用 `~arg1` 进行的判断），从两者皆为 false 跳转为 `highbit = true	onlyLowBits = false`， 之后又变回两者皆 false

		- 196607，即 `2fffe` （17个1,超32半数，用 `~arg1` 进行的判断），又出现上面的跳转

	> Integer.MAX_VALUE = 2^31 - 1 = 2147483647, 即 0x7fffffff, 31个 one-bit
	> Integer.MAX_VALUE + 1 = Integer.MIN_VALUE = -2147483648, 即 0x80000000, 只有第 32 bit 是 1


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
    boolean onlyLowBits = bits >>> 12 == 0;  // -4096 <= arg1 <= 4095 (二进制12个1)，
    BugInstance bug;
    if (highbit) {
    	// Const.IFLE 代表 <=, IFGT 为 >， 见 https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-6.html#jvms-6.5.ifge  对于这两种符号，置信度为 High， 对另外两种为 Medium
        bug = new BugInstance(this, "BIT_SIGNED_CHECK_HIGH_BIT", (seen == Const.IFLE || seen == Const.IFGT) ? HIGH_PRIORITY: MEDIUM_PRIORITY);
    } else {
        bug = new BugInstance(this, "BIT_SIGNED_CHECK", onlyLowBits ? LOW_PRIORITY : MEDIUM_PRIORITY);
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
因为不太看得懂 spotbugs 的实现，只好根据 description 出发，提取 `&` 两边的操作数, 判断是否包含 constant。如果 constant 是负数，则为 BIT_SIGNED_CHECK_HIGH_BIT, 否则 BIT_SINED_CHECK

注意 Java 中 int 和 long 的正负数分界，如果提取到的 constant 不是用十进制表示的，那么在 python 中转化成数字时，是个正数，因为 python 可以表示任意大小的数字。具体解决方法见代码实现。

### BIT_AND_ZZ

与上述两个 patterns 一起实现。当 constant 为 0, 操作符为 `!=` 或 `==` 时，为 BIT_AND_ZZ