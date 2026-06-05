---
title: Object 源码解析
date: 2026-06-05
draft: false
description: JDK17 Object 类源码解析，涵盖类注释、构造方法、内存布局（Mark Word / Klass Pointer）、equals 与 hashCode 契约
categories:
  - SourceCode
tags:
  - JDK17
  - SourceCode
---
# Object 源码阅读

## 类注释

> Object 类从 JDK 1.0 开始就已经存在。这是 Java 诞生之初就有的核心基础类.

```java
/**
 * Class {@code Object} is the root of the class hierarchy.
 * Every class has {@code Object} as a superclass. All objects,
 * including arrays, implement the methods of this class.
 *
 * @see     java.lang.Class
 * @since   1.0
 */
```

1. 在 Java 中，Object 类是整个 Java 类继承体系的根节点（根部）。也就是说除了 Object 本身之外，所有的类都直接或间接地继承自 Object。
2. 每一个类都以 Object 作为其父类（超类）。即使写了一个没有 extends 任何类的简单 class A {}，编译器也会自动让它继承 Object。如果某个类已经继承了其他类，则最终往上追溯，最顶层的类依然继承 Object。
3. 所有对象——包括数组——都实现了 Object 类中的方法。因为所有类都间接继承 Object，所以 Object 中的方法（如 equals()、hashCode()、toString()、wait()/notify() 等）可以被任何对象调用。数组在 Java 中也是对象，因此也继承了这些方法。

## 无参构造方法

```java
/**
    * Constructs a new object.
    */
@IntrinsicCandidate
public Object() {}
```

### @IntrinsicCandidate 注解

@IntrinsicCandidate 是内置注解，表示：

- **内联候选方法**：JVM 可能将此方法作为内联方法（intrinsic method）处理
- **性能优化**：JVM 可以用高度优化的机器码替换标准实现
- **平台相关**：不同硬件平台的实现可能不同（如 x86、ARM）
- **示例**：常见的同步操作、数学计算等底层操作都有内联版本

### 空方法体

- 方法体内没有任何代码
- 这意味着 `new Object()` 不会执行任何显式的初始化逻辑
- JVM 会负责：
  - 分配堆内存
  - 设置对象头（mark word、类元数据指针）

### new Object()

当执行 `Object obj = new Object();` 时：

1. **调用此构造方法**
2. **JVM 分配内存**（通常16字节对齐）
3. **设置对象头**：
   - Mark Word
   - Klass 指针
4. **返回对象引用**

```java
package io.github.jiangbyte;

import org.openjdk.jol.info.ClassLayout;

public class SeeMemoryLayout {
    public static void main(String[] args) {
        Object obj = new Object();
        
        // 打印对象内存布局
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());
        
        // 验证：对象头已被设置，大小16字节
        System.out.println("\n对象大小: " + 
            ClassLayout.parseInstance(obj).instanceSize() + " 字节");
    }
}
```

输出结果：

```
java.lang.Object object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
  8   4        (object header: class)    0x00000d58
 12   4        (object alignment gap)    
Instance size: 16 bytes
Space losses: 0 bytes internal + 4 bytes external = 4 bytes total


对象大小: 16 字节
```

先来了解这张图[^1]：

> 这张图存疑，但是可以参考

![img](assets/v2-773175d3d55668daf774d1b0fd0427b1_1440w.jpg)

上述的结果中：

| 缩写    | 含义                                         |
| :------ | :------------------------------------------- |
| **OFF** | Offset（偏移量，从对象起始地址开始的字节数） |
| **SZ**  | Size（占用多少字节）                         |

#### Mark Word

> 偏移量 0-7，共8字节

```
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
```

```
输入值: 0000000000000001

计算方法: 将每位十六进制数字转换为对应的4位二进制数

转换过程:
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
1 → 1 → 0001

结果: 0000000000000000000000000000000000000000 00000000 00000000 00000001

最终输出: 1
```

**低位的含义**[^2]

```
...00000001 (二进制)
        └┬┘
        低3位 = 001

001 对应的锁状态：无锁 (Unlocked)

01	无锁状态
0	未偏向（偏向锁未激活）
0000 (0)	GC 分代年龄为 0（刚创建，未经历 GC）
0	尚未计算 hashCode
```

> JOL 注释说 "non-biasable" 是因为 JDK 17 默认禁用了偏向锁（`-XX：-UseBiasedLocking`）

#### Klass Pointer

> 偏移量 8-11，共4字节

```
OFF  SZ   TYPE DESCRIPTION               VALUE
  8   4        (object header: class)    0x00000d58
```

```
输入值: 00000d58

计算方法: 将每位十六进制数字转换为对应的4位二进制数

转换过程:
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
0 → 0 → 0000
d → 13 → 1101
5 → 5 → 0101
8 → 8 → 1000

结果: 00000000000000000000110101011000

最终输出: 1101 0101 1000
```

#### 对齐填充

> 偏移量 12-15，共4字节

```
OFF  SZ   TYPE DESCRIPTION               VALUE
 12   4        (object alignment gap) 
```

 `Object obj = new Object()` 时——JVM 只分配了16字节，设置好对象头，就完事了。构造方法其实没有做什么。

## getClass()

```java
/**
     * Returns the runtime class of this {@code Object}. The returned
     * {@code Class} object is the object that is locked by {@code
     * static synchronized} methods of the represented class.
     *
     * <p><b>The actual result type is {@code Class<? extends |X|>}
     * where {@code |X|} is the erasure of the static type of the
     * expression on which {@code getClass} is called.</b> For
     * example, no cast is required in this code fragment:</p>
     *
     * <p>
     * {@code Number n = 0;                             }<br>
     * {@code Class<? extends Number> c = n.getClass(); }
     * </p>
     *
     * @return The {@code Class} object that represents the runtime
     *         class of this object.
     * @jls 15.8.2 Class Literals
     */
@IntrinsicCandidate
public final native Class<?> getClass();
```

### 返回运行时类

> Returns the runtime class of this `Object`.

- **编译时类型 vs. 运行时类型**：
    - 编译时类型：变量声明时的类型（如 `Number n`）。
    - 运行时类型：对象实际创建时的类型（如 `new Integer(0)`）。
- **`getClass()` 返回的是运行时类型**。即使用父类引用指向子类对象，也能告诉这个对象是 `Integer`、`String` 还是其他类。

### 锁机制的说明

`static synchronized` 锁定的是 Class 对象

> The returned `Class` object is the object that is locked by `static synchronized` methods of the represented class.

- 当你在一个类中定义 `static synchronized` 方法时，线程进入该方法前必须先获得该类的 **`Class` 对象的锁**。
- 这个 `Class` 对象正是 `getClass()` 返回的那个对象。
- 对比：
    - 实例的 `synchronized` 方法 ➜ 锁的是 `this`（实例对象）
    - 静态的 `synchronized` 方法 ➜ 锁的是 `ClassName.class`（Class 对象）

**示例：**

```java
public class MyClass {
    static synchronized void staticMethod() { } 
    // 等价于：synchronized(MyClass.class) { }
}
```
任何地方调用 `obj.getClass()` 得到的对象，就是 `static synchronized` 方法锁定的那个对象。

### 精确的泛型返回类型

> The actual result type is `Class<? extends |X|>` where `|X|` is the erasure of the static type of the expression on which `getClass` is called.

- **`|X|`**：表示 `X` 的**类型擦除**。
- **`X`**：调用 `getClass()` 的那个**表达式的静态类型**（编译时类型）。

**逐步推导：**
1. `n.getClass()`，其中 `n` 的静态类型（声明类型）是 `Number`。
2. 泛型擦除：`Number` 本身不是泛型类，擦除后还是 `Number`。
3. 实际返回类型：`Class<? extends Number>`。

**泛型类示例**：

```java
List<String> list = new ArrayList<>();
Class<? extends List> c = list.getClass(); 
// 注意不是 Class<? extends List<String>>
// 因为运行时泛型被擦除，list 的静态类型 List<String> 擦除后为 List
```

**注释里给的例子：**

```java
Number n = 0;                             // 静态类型 = Number
Class<? extends Number> c = n.getClass(); // 不需要强制转换
```
如果返回类型只是 `Class<?>`，就需要强转。但设计者通过这种精确的返回类型，无需手动强制转换。

### 方法修饰符与来源

- `public final`：所有类共享此方法，且不能被子类覆盖（保证运行时类型获取的确定性）。
- `native`：由 JVM 底层实现（通常用 C/C++ 编写），不是 Java 代码实现。
- `@IntrinsicCandidate`：是一个 JDK 内部注解，表示 JVM 可能会用**高效的内在实现**（比如 CPU 指令）替换该方法，属于性能优化。

### getClass() vs .class

| 特性                     | `obj.getClass()`                       | `ClassName.class`                |
| ------------------------ | -------------------------------------- | -------------------------------- |
| 获得的对象               | 运行时类的 Class 对象                  | 编译时已知类的 Class 对象        |
| 需要实例                 | 是                                     | 否                               |
| 受泛型擦除影响的结果类型 | `Class<? extends \|静态类型\|>`        | `Class<ClassName>`               |
| 示例                     | `"hello".getClass()` → `Class<String>` | `String.class` → `Class<String>` |

## hashCode()

```java
/**
     * Returns a hash code value for the object. This method is
     * supported for the benefit of hash tables such as those provided by
     * {@link java.util.HashMap}.
     * <p>
     * The general contract of {@code hashCode} is:
     * <ul>
     * <li>Whenever it is invoked on the same object more than once during
     *     an execution of a Java application, the {@code hashCode} method
     *     must consistently return the same integer, provided no information
     *     used in {@code equals} comparisons on the object is modified.
     *     This integer need not remain consistent from one execution of an
     *     application to another execution of the same application.
     * <li>If two objects are equal according to the {@link
     *     equals(Object) equals} method, then calling the {@code
     *     hashCode} method on each of the two objects must produce the
     *     same integer result.
     * <li>It is <em>not</em> required that if two objects are unequal
     *     according to the {@link equals(Object) equals} method, then
     *     calling the {@code hashCode} method on each of the two objects
     *     must produce distinct integer results.  However, the programmer
     *     should be aware that producing distinct integer results for
     *     unequal objects may improve the performance of hash tables.
     * </ul>
     *
     * @implSpec
     * As far as is reasonably practical, the {@code hashCode} method defined
     * by class {@code Object} returns distinct integers for distinct objects.
     *
     * @return  a hash code value for this object.
     * @see     java.lang.Object#equals(java.lang.Object)
     * @see     java.lang.System#identityHashCode
     */
@IntrinsicCandidate
public native int hashCode();
```

hashCode() 方法返回一个哈希码，哈希表（如 HashMap、HashSet）利用这个方法（通过哈希值）快速存储和查找对象。

> Returns a hash code value for the object. This method is supported for the benefit of hash tables such as those provided by {@link java.util.HashMap}.

### 一致性

> Whenever it is invoked on the same object more than once during an execution of a Java application, the {@code hashCode} method must consistently return the same integer, provided no information used in {@code equals} comparisons on the object is modified. This integer need not remain consistent from one execution of an application to another execution of the same application.

- 在同一个 Java 程序执行期间，同一个对象多次调用 `hashCode()` 必须返回相同的整数
- **前提条件**：对象中用于 `equals()` 比较的信息没有被修改
- **跨程序执行**：不同次运行程序时，哈希码可以不同（不需要保持一致）

```java
public class HashCodeRead {
    public static void main(String[] args) {
        String s = "hello";
        int hash1 = s.hashCode(); // 返回 99162322
        System.out.println(hash1);
        int hash2 = s.hashCode(); // 必须也是 99162322
        System.out.println(hash2);
        // 但下次重启程序，s.hashCode() 可能是其他值（实际上String是确定的，但规范允许不同）
    }
}
```

### equals 与 hashCode

> If two objects are equal according to the {@link equals(Object) equals} method, then calling the {@code hashCode} method on each of the two objects must produce the same integer result.

- 如果两个对象根据 `equals()` 方法判断相等，那么它们的 `hashCode()` 返回值**必须相同**
- 这是最重要的一条规则，如果违反，哈希表无法正常工作

```java
public class HashCode2Test {
    public static class Person {
        private final String name;
        private final int age;

        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Person person = (Person) obj;
            return age == person.age && Objects.equals(name, person.name);
        }

        // 注意：没有重写 hashCode！！！
    }
    
    public static void main(String[] args) {
        HashMap<Person, String> map = new HashMap<>();
        
        Person p1 = new Person("张三", 20);
        Person p2 = new Person("张三", 20);
        
        // p1 和 p2 是逻辑上相等的对象
        System.out.println(p1.equals(p2));  // true
        
        map.put(p1, "程序员");
        
        // 用 p2 去获取，期望得到"程序员"
        String value = map.get(p2);
        
        System.out.println(value);  // 输出 null ！！！
        // 明明 p1.equals(p2) 为 true，却取不到值
    }
}
```

##### 为什么会返回 null？

核心问题：查找时**走错了桶**

getNode 方法：

```java
final Node<K,V> getNode(Object key) {
        Node<K,V>[] tab; Node<K,V> first, e; int n, hash; K k;
        if ((tab = table) != null && (n = tab.length) > 0 &&
            (first = tab[(n - 1) & (hash = hash(key))]) != null) {   // ← 关键行
            if (first.hash == hash && // always check first node
                ((k = first.key) == key || (key != null && key.equals(k))))
                return first;
            if ((e = first.next) != null) {
                if (first instanceof TreeNode)
                    return ((TreeNode<K,V>)first).getTreeNode(hash, key);
                do {
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        return e;
                } while ((e = e.next) != null);
            }
        }
        return null;
    }
```

##### 关键计算：(n - 1) & hash

这就是**定位桶的位置**的公式：

```java
// n = table.length（桶的数量，必须是2的幂，默认16）
// hash = hash(key)  // 注意：是经过扰动的hash，不是key.hashCode()

index = (n - 1) & hash
```

##### 为什么 p1 和 p2 去了不同的桶

1. `hash(key)` 方法

```java
/**
     * Computes key.hashCode() and spreads (XORs) higher bits of hash
     * to lower.  Because the table uses power-of-two masking, sets of
     * hashes that vary only in bits above the current mask will
     * always collide. (Among known examples are sets of Float keys
     * holding consecutive whole numbers in small tables.)  So we
     * apply a transform that spreads the impact of higher bits
     * downward. There is a tradeoff between speed, utility, and
     * quality of bit-spreading. Because many common sets of hashes
     * are already reasonably distributed (so don't benefit from
     * spreading), and because we use trees to handle large sets of
     * collisions in bins, we just XOR some shifted bits in the
     * cheapest possible way to reduce systematic lossage, as well as
     * to incorporate impact of the highest bits that would otherwise
     * never be used in index calculations because of table bounds.
     */
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

由于没有重写 `hashCode()`，使用 `Object` 的默认实现（基于内存地址）：

```
// 假设内存地址不同
p1.hashCode() = 12345678  (0x00BC614E)
p2.hashCode() = 87654321  (0x05397FB1)

// 经过扰动计算
hash(p1) = 12345678 ^ (12345678 >>> 16)
        = 0x00BC614E ^ 0x000000BC
        = 0x00BC61F2  (约 12345842)

hash(p2) = 87654321 ^ (87654321 >>> 16)
        = 0x05397FB1 ^ 0x00000539
        = 0x05397A88  (约 87553160)
```

2. 计算桶索引（假设 HashMap 容量为 16）

```
// n = 16, n - 1 = 15 (0x0000000F)

index(p1) = (16 - 1) & hash(p1)
          = 15 & 12345842
          = 0x0000000F & 0x00BC61F2
          = 0x00000002  // 桶 2

index(p2) = 15 & 87553160
          = 0x0000000F & 0x05397A88
          = 0x00000008  // 桶 8
```

**结果：p1 存在桶2，p2 去桶8查找，桶8是空的，返回 null！**

##### 正确示例：同时重写 equals 和 hashCode

```java
public class HashCode2Test {
    public static class Person {
        private final String name;
        private final int age;

        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Person person = (Person) obj;
            return age == person.age && Objects.equals(name, person.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(name, age);  // 基于内容计算
        }
    }

    public static void main(String[] args) {
        HashMap<Person, String> map = new HashMap<>();
        
        Person p1 = new Person("张三", 20);
        Person p2 = new Person("张三", 20);
        
        // p1 和 p2 是逻辑上相等的对象
        System.out.println(p1.equals(p2));  // true
        
        map.put(p1, "程序员");
        
        // 用 p2 去获取，期望得到"程序员"
        String value = map.get(p2);
        System.out.println(value); // 输出"程序员"  ✅ 正确！
    }
}
```

### 不相等对象的哈希码

> It is <em>not</em> required that if two objects are unequal according to the {@link equals(Object) equals} method, then calling the {@code hashCode} method on each of the two objects must produce distinct integer results.  However, the programmer should be aware that producing distinct integer results for unequal objects may improve the performance of hash tables.

- **不要求**：不相等的对象必须产生不同的哈希码
- 不同的对象**可以**有相同的哈希码（这叫哈希冲突）
- 但是，程序员应该知道：为不相等的对象产生不同的哈希码，可以提高哈希表的性能

```java
System.out.println("FB".hashCode()); // 返回 2236
System.out.println("Ea".hashCode()); // 返回 2236
// 但更好的做法：尽量让不同对象返回不同哈希码
```

```java
// 添加 JVM 参数开放访问 --add-opens java.base/java.util=ALL-UNNAMED
public class HashCodePerformanceTest {
    
    // 好的哈希码实现
    static class GoodHash {
        private final String id;
        
        public GoodHash(String id) { 
            this.id = id; 
        }
        
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof GoodHash)) return false;
            return Objects.equals(this.id, ((GoodHash) obj).id);
        }
        
        @Override
        public int hashCode() {
            return id.hashCode();  // 使用String的哈希码，分布良好
        }
        
        @Override
        public String toString() {
            return "GoodHash{id='" + id + "'}";
        }
    }
    
    // 中等哈希码（只有少量冲突）
    static class MediumHash {
        private final String id;
        
        public MediumHash(String id) { 
            this.id = id; 
        }
        
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof MediumHash)) return false;
            return Objects.equals(this.id, ((MediumHash) obj).id);
        }
        
        @Override
        public int hashCode() {
            // 只有10种可能的哈希码，大量冲突
            return id.length() % 10;
        }
        
        @Override
        public String toString() {
            return "MediumHash{id='" + id + "'}";
        }
    }
    
    // 坏的哈希码实现（所有对象哈希码相同）
    static class BadHash {
        private String id;
        
        public BadHash(String id) { 
            this.id = id; 
        }
        
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof BadHash)) return false;
            return Objects.equals(this.id, ((BadHash) obj).id);
        }
        
        @Override
        public int hashCode() {
            return 42;  // 所有对象返回相同值！
        }
        
        @Override
        public String toString() {
            return "BadHash{id='" + id + "'}";
        }
    }
    
    public static void main(String[] args) {
        int size = 10000;
        
        System.out.println("========== HashMap 哈希码性能测试 ==========\n");
        
        // 测试好的哈希码
        testPerformance("好的哈希码（分布良好）", size, GoodHash.class);
        
        // 测试中等哈希码
        testPerformance("中等哈希码（少量冲突）", size, MediumHash.class);
        
        // 测试坏的哈希码
        testPerformance("坏的哈希码（全部相同）", size, BadHash.class);
    }
    
    static void testPerformance(String name, int size, Class<?> clazz) {
        try {
            System.out.println("测试: " + name);
            System.out.println("─────────────────────────────────────────");
            
            Map<Object, String> map = new HashMap<>();
            
            // 获取构造函数（使用 getDeclaredConstructor 并设置可访问）
            var constructor = clazz.getDeclaredConstructor(String.class);
            constructor.setAccessible(true);
            
            // 插入数据
            long insertStart = System.nanoTime();
            for (int i = 0; i < size; i++) {
                Object key = constructor.newInstance("key" + i);
                map.put(key, "value" + i);
            }
            long insertEnd = System.nanoTime();
            
            // 查找数据
            Object searchKey = constructor.newInstance("key" + (size / 2));
            
            // 多次查找取平均
            int iterations = 10000;
            for (int i = 0; i < iterations; i++) {
                map.get(searchKey);
            }

            // 正式测试查找
            long realSearchStart = System.nanoTime();
            for (int i = 0; i < iterations; i++) {
                map.get(searchKey);
            }
            long realSearchEnd = System.nanoTime();
            long avgSearchTime = (realSearchEnd - realSearchStart) / iterations;
            
            // 输出结果
            System.out.println("  插入 " + size + " 个元素耗时: " + 
                             (insertEnd - insertStart) / 1_000_000 + " ms");
            System.out.println("  平均查找耗时: " + avgSearchTime + " ns");
            System.out.println("  查找吞吐量: " + (1_000_000_000 / avgSearchTime) + " 次/秒");
            
            // 分析桶分布
            analyzeBucketDistribution(map, name);
            
            System.out.println();
            
        } catch (Exception e) {
            System.err.println("  错误: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    static void analyzeBucketDistribution(Map<?, ?> map, String testName) {
        try {
            // 使用反射获取内部table
            Field tableField = HashMap.class.getDeclaredField("table");
            tableField.setAccessible(true);
            Object[] table = (Object[]) tableField.get(map);
            
            if (table == null) {
                System.out.println("  table is null");
                return;
            }
            
            int maxBucketSize = 0;
            int emptyBuckets = 0;
            List<Integer> bucketSizes = new ArrayList<>();
            
            for (int i = 0; i < table.length; i++) {
                Object node = table[i];
                int count = 0;
                while (node != null) {
                    count++;
                    try {
                        Field nextField = node.getClass().getDeclaredField("next");
                        nextField.setAccessible(true);
                        node = nextField.get(node);
                    } catch (Exception e) {
                        break;
                    }
                }
                bucketSizes.add(count);
                if (count == 0) emptyBuckets++;
                if (count > maxBucketSize) maxBucketSize = count;
            }
            
            // 计算统计信息
            double avgBucketSize = bucketSizes.stream()
                .mapToInt(Integer::intValue)
                .average()
                .orElse(0);
            
            double variance = bucketSizes.stream()
                .mapToDouble(s -> Math.pow(s - avgBucketSize, 2))
                .average()
                .orElse(0);
            double stdDev = Math.sqrt(variance);
            
            System.out.println("     桶分布分析:");
            System.out.println("     总桶数: " + table.length);
            System.out.println("     空桶数: " + emptyBuckets);
            System.out.println("     最大桶大小: " + maxBucketSize);
            System.out.println("     平均桶大小: " + String.format("%.2f", avgBucketSize));
            System.out.println("     标准差: " + String.format("%.2f", stdDev));
            
            // 显示非空桶分布
            List<Integer> nonEmptyBuckets = bucketSizes.stream()
                .filter(s -> s > 0)
                .sorted((a, b) -> Integer.compare(b, a))  // 降序
                .toList();
            
            if (!nonEmptyBuckets.isEmpty()) {
                System.out.print("     前10个最大桶的大小: ");
                nonEmptyBuckets.stream()
                    .limit(10)
                    .forEach(s -> System.out.print(s + " "));
                System.out.println();
            }
            
        } catch (Exception e) {
            System.err.println("  分析桶分布时出错: " + e.getMessage());
        }
    }
}
```

```
========== HashMap 哈希码性能测试 ==========

测试: 好的哈希码（分布良好）
─────────────────────────────────────────
  插入 10000 个元素耗时: 16 ms
  平均查找耗时: 49 ns
  查找吞吐量: 20408163 次/秒
     桶分布分析:
     总桶数: 16384
     空桶数: 10158
     最大桶大小: 4
     平均桶大小: 0.61
     标准差: 0.92
     前10个最大桶的大小: 4 4 4 4 4 4 4 4 4 4 

测试: 中等哈希码（少量冲突）
─────────────────────────────────────────
  插入 10000 个元素耗时: 768 ms
  平均查找耗时: 17121 ns
  查找吞吐量: 58407 次/秒
     桶分布分析:
     总桶数: 16384
     空桶数: 16380
     最大桶大小: 10
     平均桶大小: 0.00
     标准差: 0.08
     前10个最大桶的大小: 10 1 1 1 

测试: 坏的哈希码（全部相同）
─────────────────────────────────────────
  插入 10000 个元素耗时: 1216 ms
  平均查找耗时: 486 ns
  查找吞吐量: 2057613 次/秒
     桶分布分析:
     总桶数: 16384
     空桶数: 16383
     最大桶大小: 1
     平均桶大小: 0.00
     标准差: 0.01
     前10个最大桶的大小: 1 
```

### 实现规范

> As far as is reasonably practical, the {@code hashCode} method defined by class {@code Object} returns distinct integers for distinct objects.

- `Object` 类的 `hashCode()` 实现会尽量为不同对象返回不同的整数
- "as far as is reasonably practical" 表示在合理可行的范围内
- 通常这是通过将对象的内存地址映射成整数实现的（但不是绝对的）

### 注解

- `@IntrinsicCandidate`：表示这个方法在 JVM 内部有高性能的 intrinsic（固有实现），可能被 JIT 编译器特殊处理
- `native`：这是一个本地方法，由 JVM 用 C/C++ 实现，不是在 Java 代码中实现的
- 返回类型 `int`：哈希码是 32 位整数

## equals(Object obj)

> Indicates whether some other object is "equal to" this one.

- 该方法是用来判断**当前对象**与**另一个对象**是否“相等”。  
- 注意不是判断引用是否相同（尽管默认实现是这样），而是从逻辑或业务角度判断内容是否相同。

- **代码示例：**

```java
public class equalsRead01 {
    public static void main(String[] args) {
        String a = new String("hello");
        String b = new String("hello");
        System.out.println(a.equals(b)); // true (内容相同)
        System.out.println(a == b);      // false (引用不同)
    }
}
```

### 等价关系的要求（5 条核心规则）

#### 自反性

> The {@code equals} method implements an equivalence relation on non-null object references:
> It is <i>reflexive</i>: for any non-null reference value {@code x}, {@code x.equals(x)} should return {@code true}.

任何非空对象 `x`，`x.equals(x)` 必须返回 `true`。  即一个对象必须等于它自己。

```java
public class equalsRead02 {
    public static void main(String[] args) {
        class Person {
            String name;
        }
        Person p = new Person();
        System.out.println(p.equals(p)); // 必须 true
    }
}
```

#### 对称性

> It is <i>symmetric</i>: for any non-null reference values {@code x} and {@code y}, {@code x.equals(y)} should return {@code true} if and only if {@code y.equals(x)} returns {@code true}.

如果 `x.equals(y)` 返回 `true`，则 `y.equals(x)` 也必须返回 `true`，反之亦然。  
  常见错误：子类中增加新字段导致对称性被破坏。

```java
public class equalsRead04 {
    static class Point {
        int x, y;

        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Object o) {
            if (!(o instanceof Point)) return false;
            Point p = (Point) o;
            return x == p.x && y == p.y;
        }
    }

    static class ColorPoint extends Point {
        String color;

        ColorPoint(int x, int y, String color) {
            super(x, y);
            this.color = color;
        }

        @Override
        public boolean equals(Object o) {
            if (!(o instanceof ColorPoint)) return false;
            ColorPoint cp = (ColorPoint) o;
            return super.equals(cp) && color.equals(cp.color);
        }
    }

    public static void main(String[] args) {
        ColorPoint cp1 = new ColorPoint(1, 2, "red");
        Point p1 = new Point(1, 2);

        System.out.println(cp1.equals(p1)); // false (因为 p1 不是 ColorPoint)
        System.out.println(p1.equals(cp1)); // true (Point.equals 认为颜色无所谓)
        // 违反对称性！
    }
}
```

#### 传递性

> It is <i>transitive</i>: for any non-null reference values {@code x}, {@code y}, and {@code z}, if {@code x.equals(y)} returns {@code true} and {@code y.equals(z)} returns {@code true}, then {@code x.equals(z)} should return {@code true}.

若 `x` 等于 `y`，且 `y` 等于 `z`，则 `x` 必须等于 `z`。  继承结构中的额外字段容易破坏传递性。

```java
// 测试违反传递性
public class TransitivityViolation {
    // 父类：二维点
    static class Point {
        private final int x;
        private final int y;

        public Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof Point)) return false;
            Point other = (Point) obj;
            return this.x == other.x && this.y == other.y;
        }

        @Override
        public int hashCode() {
            return 31 * x + y;
        }

        @Override
        public String toString() {
            return "Point(" + x + ", " + y + ")";
        }
    }

    // 子类：带颜色的点
    static class ColorPoint extends Point {
        private final String color;

        public ColorPoint(int x, int y, String color) {
            super(x, y);
            this.color = color;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;

            // 问题：这里要求 obj 必须是 ColorPoint 类型
            if (!(obj instanceof ColorPoint)) return false;

            ColorPoint other = (ColorPoint) obj;
            return super.equals(obj) && this.color.equals(other.color);
        }

        @Override
        public int hashCode() {
            return 31 * super.hashCode() + color.hashCode();
        }

        @Override
        public String toString() {
            return "ColorPoint(" + super.toString() + ", color=" + color + ")";
        }
    }

    public static void main(String[] args) {
        ColorPoint redPoint = new ColorPoint(1, 2, "红色");
        Point plainPoint = new Point(1, 2);
        ColorPoint bluePoint = new ColorPoint(1, 2, "蓝色");

        System.out.println("=== 违反传递性的示例 ===");
        System.out.println("1. redPoint.equals(plainPoint): " + redPoint.equals(plainPoint));
        // 输出: false (因为 plainPoint 不是 ColorPoint 类型)

        System.out.println("2. plainPoint.equals(redPoint): " + plainPoint.equals(redPoint));
        // 输出: true (Point.equals 只比较坐标)

        System.out.println("3. plainPoint.equals(bluePoint): " + plainPoint.equals(bluePoint));
        // 输出: true (Point.equals 只比较坐标)

        System.out.println("4. redPoint.equals(bluePoint): " + redPoint.equals(bluePoint));
        // 输出: false (颜色不同)

        System.out.println("\n❌ 传递性被破坏:");
        System.out.println("   步骤2得到 true (redPoint == plainPoint)");
        System.out.println("   步骤3得到 true (plainPoint == bluePoint)");
        System.out.println("   但步骤4得到 false (redPoint ≠ bluePoint)");
        System.out.println("   传递性要求: 如果 a=b 且 b=c，则 a=c");
    }
}
```

#### 一致性

> It is <i>consistent</i>: for any non-null reference values {@code x} and {@code y}, multiple invocations of {@code x.equals(y)} consistently return {@code true} or consistently return {@code false}, provided no information used in {@code equals} comparisons on the objects is modified.

只要对象没有被修改，多次调用 `equals` 必须返回相同结果。  不能依赖随机值或变化的状态（如当前时间）。

```java
public class equalsRead06 {
    static class RandomID {
        int id = (int)(Math.random() * 100);
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof RandomID)) return false;
            return this.id == ((RandomID) o).id; // 随机生成的值不稳定
        }
    }

    public static void main(String[] args) {
        RandomID r1 = new RandomID();
        RandomID r2 = new RandomID();
        System.out.println(r1.equals(r2)); // 可能 true，可能 false，即使对象没变
    }
}
```

#### 非空与空

> For any non-null reference value {@code x}, {@code x.equals(null)} should return {@code false}.

任何非空对象与 `null` 比较必须返回 `false`。  这是为了防止 `NullPointerException` 并保证逻辑合理。

```java
String s = "hello";
System.out.println(s.equals(null)); // false
// 注意：null.equals(s) 会报 NPE
```

### 等价类划分

> An equivalence relation partitions the elements it operates on into <i>equivalence classes</i>; all the members of an equivalence class are equal to each other. Members of an equivalence class are substitutable for each other, at least for some purposes.

等价关系将对象划分为**等价类**。同一等价类中所有对象互相相等，并且在某些场景下可以互相替换（比如在 `HashSet` 或 `HashMap` 中作为键）。

```java
Set<String> set = new HashSet<>();
set.add("hello");
set.add(new String("hello")); // 同一个等价类
System.out.println(set.size()); // 1，因为 "hello" 与 new String("hello") 相等
```


### @implSpec — Object 类的默认实现

> @implSpec
> The {@code equals} method for class {@code Object} implements the most discriminating possible equivalence relation on objects; that is, for any non-null reference values {@code x} and {@code y}, this method returns {@code true} if and only if {@code x} and {@code y} refer to the same object ({@code x == y} has the value {@code true}). 
> In other words, under the reference equality equivalence relation, each equivalence class only has a single element.

`Object` 类的默认 `equals` 实现使用 `==`，即只有**同一对象引用**才相等。  每个等价类只有一个元素。  这就是为什么自定义类通常需要重写 `equals`。

```java
Object obj1 = new Object();
Object obj2 = new Object();
System.out.println(obj1.equals(obj2)); // false
System.out.println(obj1.equals(obj1)); // true
```

### @apiNote — 与 hashCode 的关系

> @apiNote
>  It is generally necessary to override the {@link hashCode hashCode} method whenever this method is overridden, so as to maintain the general contract for the {@code hashCode} method, which states that equal objects must have equal hash codes.

  重写 `equals` 时必须重写 `hashCode`，以保证**相等的对象必须具有相等的哈希码**。  
  否则在哈希表（如 `HashMap`）中会出现逻辑错误。

**错误**

```java
class BadKey {
    int id;
    BadKey(int id) { this.id = id; }
    @Override
    public boolean equals(Object o) {
        if (!(o instanceof BadKey)) return false;
        return id == ((BadKey) o).id;
    }
    // 没有重写 hashCode！！！
}

HashMap<BadKey, String> map = new HashMap<>();
BadKey k1 = new BadKey(1);
BadKey k2 = new BadKey(1);
map.put(k1, "value");
System.out.println(map.get(k2)); // null（因为 hashCode 不同，找不到）
```

**正确**

```java
@Override
public int hashCode() {
    return Integer.hashCode(id);
}
```


### 方法签名与返回值说明

> @param   obj   the reference object with which to compare.
> @return  {@code true} if this object is the same as the obj
>          argument; {@code false} otherwise.
> @see     #hashCode()
> @see     java.util.HashMap

  - `@param obj`：要比较的另一个对象引用（可能为 `null`）。  
  - `@return`：当且仅当两个对象“相等”时返回 `true`。  
  - `@see`：关联到 `hashCode` 方法和 `HashMap` 类，提示它们依赖 `equals` 的正确实现。

```java
class Person {
    String name;
    int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;               // 自反性 & 性能优化
        if (o == null || getClass() != o.getClass()) return false; // 类型一致
        Person p = (Person) o;
        return age == p.age && Objects.equals(name, p.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

### 总结

| 规则         | 说明                         | 违反后果                     |
|--------------|------------------------------|------------------------------|
| 自反性       | x.equals(x) 必须 true        | 集合逻辑混乱                 |
| 对称性       | x.equals(y) == y.equals(x)   | HashSet 中对象无法找到       |
| 传递性       | 相等关系可传递               | 排序或分组错误               |
| 一致性       | 结果不随机变化               | 不可预测的行为               |
| 非空与 null  | x.equals(null) 必须 false    | NPE 或逻辑错误               |
| 与 hashCode 一致 | 相等对象必须哈希码相等    | HashMap 中键查找失败         |

## clone()

> 待续...

## 参考文献

- [^1]: https://zhuanlan.zhihu.com/p/151856103
- [^2]: https://jishuzhan.net/article/1929814208161558529

注：水平有限，谬误之处还请指出修正！
