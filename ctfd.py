"""
Author: Frankss
"""
import requests
import json
import re
import time

url = "http://detroit.sustech.edu.cn/"
username = "你的用户名"
password = "你的密码"
match_key = "COMPASS CTF"

# 这个list可以用数字id(int类型)或者str类型的题目名做key
submit_list = {
    "beginner/欢迎": "compassctf{w3Lc0mE_To_c0Mp4ss_CTF!!}",
    "beginner/加入QQ群": "compass{welcome_to_ctf_group}",
    "beginner/如何打开网页": "compass{uRL_1s_tH4t_R3411y_mAtTeRs}",
    "misc/签到": "compass{wELc0me_T0_c0mP4sS_ctF}",
    "misc/黑猫": "compass{y0U_f1Nd_tH3_c4t}",
    "crypto/基础": "compass{D0_U_kNoW_0r_NoT?}",
    "reverse/开导": "compass{g1aD_u_r_p4ss!}",
    "misc/诡计多端的零": "compass{11111111111111111111111111111111}",
    "reverse/esreveR": "compass{H@pPy_r3v!}",
    "misc/秦朝的图片": "compass{dont_compress_image_ok?}",
    "crypto/刷刷刷": "compass{m4Y_bE_n0t_sECuR3_;(}",
    "misc/不要用压缩包压缩压缩包里的压缩包": "compass{yA_Y4_ya_g1V3_mE_uR_mAg1c!!}",
}

wait_time = 15

login_url = url + "/login"
list_url = url + "/challenges"
challenges_url = url + "/api/v1/challenges"
attempt_url = url + "/api/v1/challenges/attempt"
session = requests.Session()


def get_challenges():
    req = session.get(url).content
    session.headers.update({"csrf-token": re.findall(''''csrfNonce': "(.*?)"''', req.decode('utf-8'))[0]})
    content = session.get(challenges_url).content
    return json.loads(content)["data"]


def submit(challenge_id, flag):
    req = session.get(list_url).content
    session.headers.update({"csrf-token": re.findall(''''csrfNonce': "(.*?)"''', req.decode('utf-8'))[0]})
    session.headers.update({"Content-Type": 'application/json'})
    req = session.post(attempt_url, json={"challenge_id": challenge_id, "submission": flag})
    return json.loads(req.text)["data"]


if __name__ == '__main__':
    print("[!] Login...")
    init = session.get(login_url)
    session.headers.update({"Cookies": init.headers['Set-Cookie']})
    data = {
        "name": username,
        "password": password,
        "_submit": "Submit",
        "nonce": re.findall(''''csrfNonce': "(.*?)"''', init.content.decode('utf-8'))[0]
    }
    r = session.post(login_url, data=data, allow_redirects=False)
    if "Your username or password is incorrect" in str(r.content):
        print("[-] Incorrect username or password")
        exit(-1)
    if "Forbidden" in str(r.content):
        print("[-] Unknown error, this script is not suitable for your CTFd; e.g. need captcha")
        exit(-1)
    print("[+] Login succeed!")
    session.headers.update({"Cookies": r.headers['Set-Cookie']})
    print("[!] Testing connection...")
    challenges = get_challenges()
    if len(challenges) > 0:
        print(f"[+] More than one challenges found!")
        while True:
            questions = {}
            for challenge in challenges:
                if challenge['category'].lower().startswith(match_key.lower()):
                    questions.update({challenge['id']: challenge['name']})

            print(f"[{time.strftime('%H:%M:%S', time.localtime())}] {len(questions.keys())} challenges in {match_key}.")

            pop_list = []
            for i in sorted(questions.keys()):
                for j in submit_list.keys():
                    if (i == j) or (str(j) in questions[i]):
                        print("[ " + "=" * 50 + " ]")
                        print(f"Submitting to challenge [{i}] {questions[i]}\nUsing flag: {submit_list[j]}")
                        print(str(submit(i, submit_list[j])) + "\n")
                        pop_list.append(j)

            for i in pop_list:
                submit_list.pop(i)
            if len(submit_list.keys()) == 0:
                exit(0)
            time.sleep(wait_time)
            challenges = get_challenges()
    else:
        print("[-] Web connection interrupted")
        exit(-1)


