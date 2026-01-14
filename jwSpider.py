import httpx
import asyncio
import re
import base64
import warnings
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

warnings.filterwarnings("ignore")

# 配置你的个人信息在下面的  async def main(): 部分。

# 支持CC NC-SA 4.0

# Github @ mloong
# Github @ KawasakiKusako


class CdutAsyncSpider:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "origin": "https://cas.paas.cdut.edu.cn",
        }
        # 开启自动重定向，自动处理登录后的 302 跳转
        self.client = httpx.AsyncClient(headers=self.headers, verify=False, follow_redirects=True)

    async def get_rsa_password(self):
        url = "https://cas.paas.cdut.edu.cn/cas/jwt/publicKey"
        response = await self.client.get(url)
        pub_pem = response.text
        rsakey = RSA.import_key(pub_pem)
        cipher = PKCS1_v1_5.new(rsakey)
        cipher_text = cipher.encrypt(self.password.encode())
        return "__RSA__" + base64.b64encode(cipher_text).decode()

    async def login(self):
        login_url = "https://cas.paas.cdut.edu.cn/cas/login?service=http%3A%2F%2Fjw.cdut.edu.cn%2Fsso%2Flogin.jsp%3FtargetUrl%3Dbase64aHR0cDovL2p3LmNkdXQuZWR1LmNuL0xvZ29uLmRvP21ldGhvZD1sb2dvblNTT2NkbGdkeA%3D%3D"

        # 1. 获取 execution
        res01 = await self.client.get(login_url)
        execution = re.search(r'name="execution" value="(.*?)"', res01.text).group(1)

        # 2. 构造参数
        encrypted_pw = await self.get_rsa_password()
        login_data = {
            "username": self.username,
            "password": encrypted_pw,
            "captcha": "",
            "currentMenu": "1",
            "failN": "0",
            "mfaState": "",
            "execution": execution,
            "_eventId": "submit",
            "geolocation": "",
            "submit": "Login1"
        }

        # 3. 提交登录（client开启了重定向，会自动完成 Location 跳转）
        await self.client.post(login_url, data=login_data)

    async def get_kbjcmsid(self):
        # 对应原代码 res02 = session.get(url, ...)
        url = "https://jw.cdut.edu.cn/jsxsd/framework/xsMainV_new.htmlx"
        params = {"t1": "1"}

        res = await self.client.get(url, params=params)

        # 必须在 res02 (即 xsMainV_new.htmlx) 的结果中搜索，而非 viewtable.do
        pattern = r'data-value="([^"]+)"[^>]*name="kbjcmsid"'
        return re.search(pattern, res.text).group(1)

    async def save_room_schedule(self, room, kbjcmsid, xnxq01id):
        url = "https://jw.cdut.edu.cn/jsxsd/xskb/viewtable.do"
        params = {
            "xnxq01id": xnxq01id,
            "kbjcmsid": kbjcmsid,
            "jsid": room["jsid"],
            "lx": "jsid"
        }

        response = await self.client.get(url, params=params)
        filename = f"{room['jsh']}.html"

        with open(filename, "w", encoding="utf-8-sig") as f:
            f.write(response.text)

        print(f"已保存 {filename}")

    async def close(self):
        await self.client.aclose()


async def main():

    # username 填写 电话/学号 （只需要填写一个即可）
    # e.g. 
    #username = 
    #password = 

    username = "202*********"
    password = "YourPassword"

    spider = CdutAsyncSpider(username, password)

    await spider.login()

    kbjcmsid = await spider.get_kbjcmsid()

    rooms = [
        {"jsid": "4129", "jsmc": "(C075-06-31)C075-06-31", "jsh": "C075-06-31", "n": 1},
        {"jsid": "4130", "jsmc": "(C075-06-32)C075-06-32", "jsh": "C075-06-32", "n": 2},
        {"jsid": "4131", "jsmc": "(C075-06-34)C075-06-34", "jsh": "C075-06-34", "n": 3},
        {"jsid": "4124", "jsmc": "(C075-06-22)C075-06-22", "jsh": "C075-06-22", "n": 1},
        {"jsid": "4128", "jsmc": "(C075-06-30)C075-06-30", "jsh": "C075-06-30", "n": 9},
        {"jsid": "4125", "jsmc": "(C075-06-27)C075-06-27", "jsh": "C075-06-27", "n": 2},
        {"jsid": "4126", "jsmc": "(C075-06-28)C075-06-28", "jsh": "C075-06-28", "n": 3},
        {"jsid": "4127", "jsmc": "(C075-06-29)C075-06-29", "jsh": "C075-06-29", "n": 4}
    ]

    xnxq01id = "2025-2026-1"

    tasks = [spider.save_room_schedule(room, kbjcmsid, xnxq01id) for room in rooms]
    await asyncio.gather(*tasks)

    await spider.close()


if __name__ == "__main__":
    asyncio.run(main())
