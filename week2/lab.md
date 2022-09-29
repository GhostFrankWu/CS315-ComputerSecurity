# (a) What happens when you compile without “-z execstack”?
without `-z execstack`, by default, gcc will enable NX protection, which means the stack is not executable.    

Actually in this program, the shellcode is stored in the stack, and since the stack segment is marked as Writeable, it cant be executed. 

So the program will crash and raise a `segment fault` when it tries to execute the shellcode, because the program is trying to execute the shellcode in non-executable segment (stack).

# (b) What happens if you enable ASLR? Does the return address change?
By ASLR itself meaning, the OS will help to randomize the address of the program's virtual memory, for example, the address of the stack, heap, dynamic librarys, and the address of the program itself.

Also, with different versions of the OS, the ASLR will be implemented in different ways.

However, if program is not compiled as Position Independent Executable (PIE), the address of the program itself will not be randomized.

In this lab, we did not disable PIE with (-fno-pie), so the address of the program itself will be randomized, and the **return address will change**.

# (c) Does the address of the buffer[] in memory change when you run BOF using GDB, /home/root/Desktop/Lab2-BufferOverflows/BOF, and ./BOF

Answer: **yes**

但是为了不被莫名其妙被扣20分还是写一下原因吧：

众所周知程序的入口并不是main，main只是初始化完之后默认执行的第一个函数。

main函数的声明总是
```cpp
int main(int argc, char *argv[], char *envp[]);
```

我们的main实际上是在`__libc_start_main`这个函数里面被调用的，而`__libc_start_main`是在`_start`这个函数里面被调用的。

因为有函数调用，所以argc，argv，envp都会被压到栈里，其中的`argv[0]`就是题目的后两个不同点，而gdb和外界shell，或者不同shell之间的env环境变量可能都是不同的，同时gdb启动默认会用绝对路径运行，所以被压进去的东西也不一样，栈上数据的地址也不一样。

至于怎么解决这个问题，最简单的方法就是相同env下运行生成badfile的程序，这样就可以自动算出栈上数据的偏移，详见附件的C代码。

当然假设远程环境未知也有很多解决方法，我们的溢出长度有512字节，可以轻易栈喷射。

本题用strcpy进行溢出，所以ROP还是很受限的(需要避免0字节)，但是仍然可以构造puts ROP泄露libc基址，然后修改badfile直接打libc的OG。