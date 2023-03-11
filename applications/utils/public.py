from json import loads
from django.http import HttpResponse

BASE_URL = "https://music.163.com/"


def readFile(method, path, mode="r"):
    with open(path, mode) as f:
        if method == "read":
            return f.read()
        elif method == "readlines":
            return f.readlines()


def saveFile(path, content, mode="w"):
    with open(path, mode) as f:
        f.write(str(content))


def getCookie():
    return loads(
        readFile("read", "cookies").replace("'", '"').encode()
    )


def request_query(r, *args):
    # ["id",{"ids":800435}] ["id","ids"] "id"
    def check(txt):
        if type(txt) == int:
            return str(txt)
        return txt
    dic = {}
    try:
        info = loads(r.body)
    except:
        pass
    for i in args:
        if type(i) == list:
            j = i[1]
            i = i[0]
        else:
            j = i
        if r.method == "POST":
            try:
                query = info[i] if r.body[0] == 123 else r.POST.get(i)
            except:
                query = None
        elif r.method == "GET":
            query = r.GET.get(i)
        try:
            if type(j) == dict:
                key = list(j.keys())[0]
                dic[key] = check(query if query else j[key])
            else:
                dic[j] = check(query)
        except:
            dic[i] = check(query)
    return dic


def Http_Response(r, text, type="application/json,charset=UTF-8"):
    try:
        query = request_query(r, "var", "cb")
    except:
        query = {"var": None, "cb": None}
    if query["var"] or query["cb"]:
        if query["var"]:
            text = "{}={}".format(query["var"], text)
        elif query["cb"]:
            text = "{}({})".format(query["cb"], text)
        type = "application/javascript; charset=UTF-8"
    if type == "":
        return HttpResponse(text)
    return HttpResponse(text, content_type=type)
