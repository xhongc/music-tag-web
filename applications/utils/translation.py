import hashlib
import random
import time

import requests


from component import translators as ts


def translation_lyc_text(contents):
    if len(contents) > 1000:
        results = []
        contents = contents.split('\n')
        content_1k = ""
        for each in contents:
            if len(content_1k + each + '\n') > 1000:
                results.append(content_1k)
                content_1k = each + '\n'
            else:
                content_1k += each + '\n'
        if content_1k:
            results.append(content_1k)
        translate_res = ""
        for content in results:
            res = ts.translate_text(content, translator="youdao", to_language="zh-CHS")
            if translate_res:
                translate_res += "\n" + res
            else:
                translate_res = res
        return translate_res
    else:
        res = ts.translate_text(contents, translator="youdao", to_language="zh-CHS")
        print(res)
        return res


if __name__ == '__main__':
    a = translation_lyc_text('スピード')
    print(a)
