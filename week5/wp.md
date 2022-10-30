# Week5
## baby_re
IDA 或者 strings 一把梭，有两个flag，一个假的，交另一个。

## RNG boost
这题用angr搞了好久没写出来，正常逆很快就出了

题目大概是自己写了个Lehmer random number generator，MSVC编译选项看起来像_DEBUG, MD, O2。需要预测前5个随机数，种子是114514，不知道能不能复现一个出来，解出来之后得知前五个的答案是
```
232665
1332123
7300
1060456
1282900
```
还有一种可行的做法是动态调试去看比较右边的随机数。   

还有一种解法的原因是这题的输入 **只被用作了比较**，也就是说干掉比较函数程序就会傻乎乎地自己吐出flag。  

需要干掉的比较地方就是把输入和随机数比较的那个分支，**本文档同目录下也放了patch好的程序**。  
把比较函数后边的`jz`条件跳转干掉（比如nop掉，或者把上边搞成永远真）  
搞定之后随便输五个数就可以看到flag了。   


## mov
好久前看过这个有趣的问题，好像是B站硬核会员的答题选项，然后就推到了校队群里，没想到被出成了题目。  
出题的脚本大概是 https://github.com/Battelle/movfuscator   

简单来说，mov是图灵完备的前提是发生异常之后跳到程序起始地址，所有这个mov壳最外层需要套一个吃异常并跳转到开头的处理函数。  
而GDB调试时，ptrace会先于这个处理函数吃到异常，就难以直接调试。  

这里不修直接让gdb把sig全传回给程序也是可以的，但是控制流会看的有些头疼。  

在GitHub上可以找到能脱一点壳的脚本 https://github.com/kirschju/demovfuscator  
但是环境很难搭，好在DockerHub上（CTFer就应该逛各种Hub不是吗）有打好的镜像 https://hub.docker.com/r/iyzyi/demovfuscator   

拉下来直接脱壳，脱好的附件放在了本文档同级的目录下。

虽然还有大量的mov，但是入口修了，引用也清晰多了，至少还原了关键的控制流，而且也没有通过吃信号跳转的函数了，可以方便地调试。

然后调试时候发现大循环里的Invaild分支是逐次比较，又根据%20s可知flag长度应为20个字符。  
于是根据第一题格式丢一个`cs315{0123456789012}`进去，gdb调试发现在第6次Invalid比较时进到了Invalid里边。  

（可能需要说明一下第0次比较在最外层，所以不动那个c）

改一下放`cA315{0123456789012}`，第一次比较就炸了，于是先推测是逐位比较的（好像mov也只能这么做），而且后边的输入不影响前边，即所有的运算都是字节不相关的。

写个和GDB交互的脚本爆破（运行起来还是挺漂亮的）：
```python
from pwn import *

flag = list('cs315{*************}')
stri = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_{}"
p = process(["gdb", "fuck"])
p.sendline(b"b *0x804c3a9")
sp = b"LEGEND: "  # 注意我用的是pwndbg，使用其他插件可能要更换分割符
# context.log_level='debug' 
for i in range(6, 19):
    for j in range(len(stri)):
        p.sendline(b"r")
        tr = [x for x in flag]
        tr[i] = stri[j]
        p.sendline(''.join(tr).encode())
        _ = p.recvuntil(sp)
        cnt = 0
        print(f'No.{i+1}, trying {stri[j]}, now flag is {"".join(flag)}')
        try:
            while True:
                cnt += 1
                p.sendline(b"c")
                r = p.recvuntil(sp, timeout=0.1)
                if b"Invalid." in r:
                    break
            if cnt == i+1:
                raise Exception
        except:
            print("hit!!!!")
            flag[i] = stri[j]
            print(''.join(flag))
            break

print(''.join(flag))
```
一分钟左右就能跑出flag
