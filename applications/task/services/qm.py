import json
import uuid

import requests
from requests import Session

QQMUSIC_SONG_COVER = "http://y.qq.com/music/photo_new/T002R300x300M000{id}.jpg"


class HttpRequest:
    __session = None

    def __init__(self):
        # 全局唯一Session
        self.__session = requests.Session()

    def getHttp(self, url: str, method: int = 0, data: bytes = r'', header: dict = {}) -> requests.Response:
        """
        Http请求-提交二进制流
        Args:
            url: url网址
            method: 0 表示Get请求 1 表示用POST请求. 默认值为 0.
            data: 提交的二进制流data数据. 默认值为 r''.
            header: 协议头. 默认值为 {}.

        Returns:
            requests.Response: 返回的http数据
        """
        if method == 0:
            d = self.__session.get(url, headers=header)
        else:
            d = self.__session.post(url, data, headers=header)
        return d

    def getHttp2Json(self, url: str, method: int = 0, data: dict = {}, header: dict = {}):
        """Http请求-提交json数据

        Args:
            url (str): url网址
            method (int): 0 表示Get请求 1 表示用POST请求. 默认值为 0.
            data (bytes): 提交的json对象数据. 默认值为 {}.
            header (dict): 协议头. 默认值为 {}.

        Returns:
            requests.Response: 返回的http数据
        """
        d = json.dumps(data, ensure_ascii=False)
        d = d.encode('utf-8')
        return self.getHttp(url, method, d, header)

    def getSession(self) -> Session:
        return self.__session

    def setCookie(self, ck):
        for a in ck:
            self.__session.cookies.set(a, ck[a])
        print("cookie set.")


class QQMusicApi:
    QQHttpServer = HttpRequest()

    mQQCookie = ""

    def getCookie(self):
        return self.mQQCookie

    def setQQCookie(self, ck: str):
        self.mQQCookie = ck

    def getHead(self):
        return {
            "User-Agent": "QQ音乐/73222 CFNetwork/1406.0.2 Darwin/22.4.0".encode("utf-8"),
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Referer": "http://y.qq.com",
            'Content-Type': 'application/json; charset=UTF-8',
            "Cookie": self.getCookie(),
        }

    def getQQServersCallback(self, url: str, method: int = 0, data: dict = {}):
        """重新设计了Http接口

        参数:
            url (str): _description_
            method (int): _description_. Defaults to 0.
            data (dict): _description_. Defaults to {}.

        返回:
            requests.Response: 返回的http数据
        """
        return self.QQHttpServer.getHttp2Json(url, method, data, self.getHead())

    def getQQMusicMediaLyric(self, mid: str) -> dict:
        d = self.getQQServersCallback(
            "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?g_tk=5381&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&ct=121&cv=0&songmid=" + mid)
        d = d.text
        # self.download_lyric(mid)
        return json.loads(d)

    def download_lyric(self, songid):
        res = requests.get('https://c.y.qq.com/qqmusic/fcgi-bin/lyric_download.fcg', params=dict(
            version='15',
            miniversion='82',
            lrctype='4',
            musicid=songid,
        ))
        print(res)

    @staticmethod
    def getUUID():
        return uuid.uuid1().__str__()

    def getQQMusicSearch(self, key: str = "", page: int = 1, size: int = 15) -> (dict, dict):
        """搜索音乐

        参数:
            key (str): 搜索关键词. 默认是 "".
            page (int): 分页序号. 默认是 1.

        返回值:
            dict: 返回搜索列表
        """
        # base url
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"

        # 一次获取最多获取30条数据 否则返回空列表
        page_per_num = size
        data = {
            "comm": {
                "ct": 19, "cv": 1845
            },
            "music.search.SearchCgiService": {
                "method": "DoSearchForQQMusicDesktop",
                "module": "music.search.SearchCgiService",
                "param": {
                    "query": key,
                    "num_per_page": page_per_num,
                    "page_num": page
                }
            }
        }

        data = {
            "comm": {
                "wid": "",
                "tmeAppID": "qqmusic",
                "authst": "",
                "uid": "",
                "gray": "0",
                "OpenUDID": "2d484d3157d4ed482e406e6c5fdcf8c3d3275deb",
                "ct": "6",
                "patch": "2",
                "psrf_qqopenid": "",
                "sid": "",
                "psrf_access_token_expiresAt": "",
                "cv": "80600",
                "gzip": "0",
                "qq": "",
                "nettype": "2",
                "psrf_qqunionid": "",
                "psrf_qqaccess_token": "",
                "tmeLoginType": "2"
            },
            "music.search.SearchCgiService.DoSearchForQQMusicDesktop": {
                "module": "music.search.SearchCgiService",
                "method": "DoSearchForQQMusicDesktop",
                "param": {
                    "num_per_page": page_per_num,
                    "page_num": page,
                    "remoteplace": "txt.mac.search",
                    "search_type": 0,
                    "query": key,
                    "grp": 1,
                    "searchid": uuid.uuid1().__str__(),
                    "nqc_flag": 0
                }
            }
        }
        res = self.QQHttpServer.getHttp2Json(
            url, 1, data, {
                "referer": "https://y.qq.com/portal/profile.html",
                "Content-Type": "json/application;charset=utf-8",
                "user-agent": "QQ%E9%9F%B3%E4%B9%90/73222 CFNetwork/1406.0.3 Darwin/22.4.0"
            })
        # print(res.text)
        jsons = res.json()
        # 开始解析QQ音乐的搜索结果
        res = jsons['music.search.SearchCgiService.DoSearchForQQMusicDesktop']['data']
        lst = res['body']['song']['list']
        meta = res['meta']

        # 数据清洗,去掉搜索结果中多余的数据
        list_clear = []
        for i in lst:
            list_clear.append({
                'album': i['album'],
                'docid': i['docid'],
                'id': i['id'],
                'mid': i['mid'],
                'name': i['title'],
                'singer': i['singer'],
                'time_public': i['time_public'],
                'title': i['title'],
                'file': i['file'],
            })

        # rebuild json
        # list_clear: 搜索出来的歌曲列表
        # {
        #   size 搜索结果总数
        #   next 下一搜索页码 -1表示搜索结果已经到底
        #   cur  当前搜索结果页码
        # }
        return {
            'data': list_clear,
            'page': {
                'size': meta['sum'],
                'next': meta['nextpage'],
                'cur': meta['curpage'],
                'searchKey': key
            }
        }

    def getQQMusicMatchSong(self, name):
        song_list = self.getQQMusicSearch(name)
        songs = self.formatList(song_list["data"])
        if len(songs) == 0:
            return []
        return songs

    def formatList(self, mlist):
        """
        处理音乐列表
        Args:
            mlist (Array<T>): 歌曲列表

        Returns:
            lists, songs: 处理过的数据数组
        """
        songs = []  # : list[Songs]
        for i in mlist:
            singer = ",".join([i["name"] for i in i["singer"]])

            _id = i["file"]
            # 批量下载不需要选择音质 直接开始解析为最高音质 枚举
            code = ""
            format = ""
            qStr = ""
            fsize = 0
            mid = _id['media_mid']
            if int(_id['size_hires']) != 0:
                # 高解析无损音质
                code = "RS01"
                format = "flac"
                qStr = "高解析无损 Hi-Res"
                fsize = int(_id['size_hires'])
            elif int(_id['size_flac']) != 0:
                isEnc = False  # 这句代码是逆向出来的 暂时无效
                if (isEnc):
                    code = "F0M0"
                    format = "mflac"
                else:
                    code = "F000"
                    format = "flac"
                qStr = "无损品质 FLAC"
                fsize = int(_id['size_flac'])
            elif int(_id['size_320mp3']) != 0:
                code = "M800"
                format = "mp3"
                qStr = "超高品质 320kbps"
                fsize = int(_id['size_320mp3'])
            elif int(_id['size_192ogg']) != 0:
                isEnc = False  # 这句代码是逆向出来的 暂时无效
                if (isEnc):
                    code = "O6M0"
                    format = "mgg"
                else:
                    code = "O600"
                    format = "ogg"
                qStr = "高品质 OGG"
                fsize = int(_id['size_192ogg'])
            elif int(_id['size_128mp3']) != 0:
                isEnc = False  # 这句代码是逆向出来的 暂时无效
                if (isEnc):
                    code = "O4M0"
                    format = "mgg"
                else:
                    code = "M500"
                    format = "mp3"
                qStr = "标准品质 128kbps"
                fsize = int(_id['size_128mp3'])
            elif int(_id['size_96aac']) != 0:
                code = "C400"
                format = "m4a"
                qStr = "低品质 96kbps"
                fsize = int(_id['size_96aac'])
            else:
                print("这首歌曲好像无法下载,请检查是否有vip权限.")
                continue

            albumName = str(i["album"]['title']).strip(" ")
            if albumName == '':
                albumName = "未分类专辑"

            # 开始检查歌曲过滤显示
            # 第三方修改歌曲可以在这里对歌曲做二次处理
            flacName = i["title"]

            time_publish = i["time_public"]
            if time_publish == '':
                time_publish = ""

            # 通过检查 将歌曲放入歌曲池展示给用户 未通过检查的歌曲将被放弃并且不再显示
            songs.append({
                'prefix': code,
                'extra': format,
                'notice': qStr,
                'mid': mid,
                'musicid': i['id'],
                'id': i['mid'],
                'size': f"%.2fMB" % (fsize / 1024 / 1024),
                'name': flacName,
                'artist': singer,
                'album': albumName,
                "album_id": i["album"]['mid'],
                'year': time_publish,
                'readableText': f'{time_publish} {singer} - {i["title"]} | {qStr}',
                "album_img": QQMUSIC_SONG_COVER.format(id=i["album"]['mid'])
            })
        # 这部分其实可以只返回songs 但是代码我懒得改了 反正又不是不能用=v=
        return songs

    def getSingleMusicInfo(self, _id: str):
        """
        获取单曲歌曲信息

        参数:
            _id: https://y.qq.com/n/ryqq/songDetail/0042QMDR1VzSsx 里面的 0042QMDR1VzSsx\n
            https://y.qq.com/n/ryqq/songDetail/374229667?songtype=0 里面的 374229667

        返回:

        """
        u = 'https://u.y.qq.com/cgi-bin/musicu.fcg'

        # 这里有两种格式 一种是纯数字 一种是mid 所以判断是否可被int即可

        try:
            sid = int(_id)
            mid = 0
        except Exception as e:
            sid = 0
            mid = _id

        d = {"get_song_detail": {"module": "music.pf_song_detail_svr", "method": "get_song_detail",
                                 "param": {"song_id": sid, "song_mid": mid, "song_type": 0}},
             "comm": {"g_tk": 0, "uin": "", "format": "json", "ct": 6, "cv": 80600,
                      "platform": "wk_v17", "uid": "", "guid": self.getUUID()}}

        r = self.getQQServersCallback(u, 1, d)
        r = r.json()
        # print(r)
        get_song_detail = r['get_song_detail']
        if get_song_detail['code'] == 0:
            i = get_song_detail['data']['track_info']
            lst = [{
                'album': i['album'],
                'docid': '无',
                'id': i['id'],
                'mid': i['mid'],
                'name': i['title'],
                'singer': i['singer'],
                'time_public': i['time_public'],
                'title': i['title'],
                'file': i['file'],
            }]
        else:
            lst = []
        # 数据清洗,去掉搜索结果中多余的数据
        # rebuild json
        # list_clear: 搜索出来的歌曲列表
        # {
        #   size 搜索结果总数
        #   next 下一搜索页码 -1表示搜索结果已经到底
        #   cur  当前搜索结果页码
        # }
        return {
            'data': lst,
            'page': {
                'size': len(lst),
                'next': "1",
                'cur': "1",
                'searchKey': ""
            }
        }
