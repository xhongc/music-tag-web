import requests
from time import time
from json import loads
from random import randint
from .public import readFile, getCookie
from .encrypt import weEncrypt, linuxEncrypt, eEncrypt


userAgents = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89;GameHelper',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1',
    'Mozilla/5.0 (iPad; CPU OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1',
    'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BKK-AL10 Build/HONORBKK-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.6 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/13.10586'
]


class send:
    def __init__(self, data={}, encrypt_method="weapi", timeout=10, url=""):
        self.BASE_URL = "https://music.163.com/"
        self.headers = {
            "User-Agent": userAgents[randint(0, len(userAgents)) - 1],
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.BASE_URL
        }
        self.session = requests.session()
        self.encrypt_method = encrypt_method
        self.data = data
        self.timeout = timeout
        self.url = url

    def __url(self, url):
        if url == "":
            return self.BASE_URL+"api/linux/forward"
        if url[:4] == "http":
            return url
        return self.BASE_URL + url

    def __cookies(self, data={}):
        try:
            cookies = getCookie()
        except:
            return data
        return {**data, **cookies}

    def encrypt(self, data):
        cookie = self.__cookies()
        if self.encrypt_method == "linuxapi":
            self.headers["User-Agent"] = userAgents[0]
            data["method"] = "POST"
            return linuxEncrypt(data)
        elif self.encrypt_method == "weapi":
            data["csrf_token"] = cookie["__csrf"] if "__csrf" in cookie else ""
            return weEncrypt(data)
        elif self.encrypt_method == "eapi":
            data["header"] = {
                'osver': "",
                "appver": "8.0.0",
                "channel": "",
                "deviceId": "",
                "mobilename": "",
                "os": "android",
                "resolution": "1920x1080",
                "versioncode": "140",
                "buildver": str(int(time())),
                "requestId": str(int(time()*100))+"_0"+str(randint(100, 999)),
                "__csrf": cookie["__csrf"] if "__csrf" in cookie else ""
            }
            if "MUSIC_U" in cookie: data["header"]["MUSIC_U"] = cookie["MUSIC_U"]
            if "MUSIC_A" in cookie: data["header"]["MUSIC_A"] = cookie["MUSIC_A"]
            self.headers["Cookie"] = ''.join(map(lambda key: f"{key}={data['header'][key]};",data["header"]))
            return eEncrypt(self.url, data)
        return data

    def POST(self, url, cookie={}):
        response = self.session.post(self.__url(url),
                                     data=self.encrypt(self.data),
                                     headers=self.headers,
                                     cookies=self.__cookies(cookie),
                                     timeout=self.timeout)
        return response

    def GET(self, url, cookie={}):
        if self.encrypt_method == "eapi":
            self.headers["User-Agent"] = userAgents[-1]
        response = self.session.get(self.__url(url),
                                    headers=self.headers,
                                    cookies=self.__cookies(cookie),
                                    timeout=self.timeout)
        return response
