# 第一周wp
## 签到
群公告可见
`flag{w3Lc0Me_T0_cS315!}`

## HTTP code 206
筛选http的包（虽然也可以现在code是206，但是并不影响），导出分组解析结果为json，之后直接梭

```python
import json

f = json.load(open("1.json", "r", encoding="utf8"))
for i in f:
    try:
        print(i['_source']['layers']['http']['http.file_data'],end="")
    except:
        pass
```
得到 `fl{17uaji1l}`

注意到包文中有标注对应位，因为只有14位手动看一下就能发现只少了2-3位，手动补ag得到

`flag{17uaji1l}`


## Time-based SQL Injection
**url解码两次发现是SSRF时间盲注打本机服务**  
简单一看脚本是遍历不是二分，那就不需要处理时间了，直接判断后一位是否小于前一位（新一位的开始）  
当然也可以不停地覆盖，但是需要取两个值，上边的做法只需要取一个地方，写脚本会快一些  
直接一把梭不过滤全部导出，然后
```python
import json

f = json.load(open("2.json", "r", encoding="utf8"))
d = []
for i in f:
    try:
        d.append(int(i['_source']['layers']['http']["http.request.full_uri"].split("%2527")[1]))
    except:
        pass

for i in range(len(d)):
    try:
        if d[i] > d[i + 1]:
            print(chr(d[i]), end="")
    except:
        print(chr(d[i]))
```
得到`flag{1qwy2781}`