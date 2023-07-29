# coding=utf-8
# author=UlionTse

"""
Copyright (C) 2017-2023  UlionTse

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Email: uliontse@outlook.com

translators  Copyright (C) 2017-2023  UlionTse
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""

import os
import re
import sys
import time
import json
import uuid
import hmac
import base64
import random
import hashlib
import datetime
import warnings
import functools
import urllib.parse
from typing import Optional, Union, Tuple, List

import tqdm
import execjs
import requests
import lxml.etree
import pathos.multiprocessing

SessionType = requests.sessions.Session
ResponseType = requests.models.Response
LangMapKwargsType = Union[str, bool]
ApiKwargsType = Union[str, int, float, bool, dict]

__all__ = [
    'translate_text', 'translate_html', 'translators_pool',
    'alibaba', 'apertium', 'argos', 'baidu', 'bing', 'caiyun', 'cloudYi', 'deepl', 'elia', 'google',
    'iciba', 'iflytek', 'iflyrec', 'itranslate', 'judic', 'languageWire', 'lingvanex', 'mglip', 'mirai', 'modernMt',
    'myMemory', 'niutrans', 'papago', 'qqFanyi', 'qqTranSmart', 'reverso', 'sogou', 'sysTran', 'tilde', 'translateCom',
    'translateMe', 'utibet', 'volcEngine', 'yandex', 'yeekit', 'youdao',
    '_alibaba', '_apertium', '_argos', '_baidu', '_bing', '_caiyun', '_cloudYi', '_deepl', '_elia', '_google',
    '_iciba', '_iflytek', '_iflyrec', '_itranslate', '_judic', '_languageWire', '_lingvanex', '_mglip', '_mirai',
    '_modernMt',
    '_myMemory', '_niutrans', '_papago', '_qqFanyi', '_qqTranSmart', '_reverso', '_sogou', '_sysTran', '_tilde',
    '_translateCom',
    '_translateMe', '_utibet', '_volcEngine', '_yandex', '_yeekit', '_youdao',
]  # 36


class TranslatorError(Exception):
    pass


class Tse:
    def __init__(self):
        self.author = 'Ulion.Tse'
        self.all_begin_time = time.time()
        self.default_session_freq = int(1e3)
        self.default_session_seconds = 1.5e3
        self.transform_en_translator_pool = (
            'itranslate', 'lingvanex', 'myMemory', 'apertium', 'cloudYi', 'translateMe')
        self.auto_pool = ('auto', 'detect', 'auto-detect', 'all')
        self.zh_pool = ('zh', 'zh-CN', 'zh-cn', 'zh-CHS', 'zh-Hans', 'zh-Hans_CN', 'cn', 'chi', 'Chinese')

    @staticmethod
    def time_stat(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if_show_time_stat = kwargs.get('if_show_time_stat', False)
            show_time_stat_precision = kwargs.get('show_time_stat_precision', 2)
            sleep_seconds = kwargs.get('sleep_seconds', 0)

            if if_show_time_stat and sleep_seconds >= 0:
                t1 = time.time()
                result = func(*args, **kwargs)
                t2 = time.time()
                cost_time = round((t2 - t1 - sleep_seconds), show_time_stat_precision)
                sys.stderr.write(f'TimeSpent(function: {func.__name__[:-4]}): {cost_time}s\n')
                return result
            return func(*args, **kwargs)

        return _wrapper

    @staticmethod
    def get_timestamp() -> int:
        return int(time.time() * 1e3)

    @staticmethod
    def get_headers(host_url: str,
                    if_api: bool = False,
                    if_referer_for_host: bool = True,
                    if_ajax_for_api: bool = True,
                    if_json_for_api: bool = False,
                    if_multipart_for_api: bool = False,
                    if_http_override_for_api: bool = False
                    ) -> dict:

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        url_path = urllib.parse.urlparse(host_url.strip('/')).path
        host_headers = {
            'Referer' if if_referer_for_host else 'Host': host_url,
            "User-Agent": user_agent,
        }
        api_headers = {
            'Origin': host_url.split(url_path)[0] if url_path else host_url,
            'Referer': host_url,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            "User-Agent": user_agent,
        }
        if if_api and not if_ajax_for_api:
            api_headers.pop('X-Requested-With')
            api_headers.update({'Content-Type': 'text/plain'})
        if if_api and if_json_for_api:
            api_headers.update({'Content-Type': 'application/json'})
        if if_api and if_multipart_for_api:
            api_headers.pop('Content-Type')
        if if_api and if_http_override_for_api:
            api_headers.update({'X-HTTP-Method-Override': 'GET'})
        return host_headers if not if_api else api_headers

    def check_en_lang(self, from_lang: str, to_lang: str, default_translator: Optional[str] = None,
                      default_lang: str = 'en-US') -> Tuple[str, str]:
        if default_translator and default_translator in self.transform_en_translator_pool:
            from_lang = default_lang if from_lang == 'en' else from_lang
            to_lang = default_lang if to_lang == 'en' else to_lang
            from_lang = default_lang.replace('-', '_') if default_translator == 'lingvanex' and from_lang[
                                                                                                :3] == 'en-' else from_lang
            to_lang = default_lang.replace('-', '_') if default_translator == 'lingvanex' and to_lang[
                                                                                              :3] == 'en-' else to_lang
        return from_lang, to_lang

    def check_language(self,
                       from_language: str,
                       to_language: str,
                       language_map: dict,
                       output_auto: str = 'auto',
                       output_zh: str = 'zh',
                       output_en_translator: Optional[str] = None,
                       output_en: str = 'en-US',
                       if_check_lang_reverse: bool = True,
                       ) -> Tuple[str, str]:

        if output_en_translator:
            from_language, to_language = self.check_en_lang(from_language, to_language, output_en_translator, output_en)

        from_language = output_auto if from_language in self.auto_pool else from_language
        from_language = output_zh if from_language in self.zh_pool else from_language
        to_language = output_zh if to_language in self.zh_pool else to_language

        if from_language != output_auto and from_language not in language_map:
            raise TranslatorError(
                'Unsupported from_language[{}] in {}.'.format(from_language, sorted(language_map.keys())))
        elif to_language not in language_map and if_check_lang_reverse:
            raise TranslatorError('Unsupported to_language[{}] in {}.'.format(to_language, sorted(language_map.keys())))
        elif from_language != output_auto and to_language not in language_map[from_language]:
            raise TranslatorError('Unsupported translation: from [{0}] to [{1}]!'.format(from_language, to_language))
        elif from_language == to_language:
            raise TranslatorError(f'from_language[{from_language}] and to_language[{to_language}] should not be same.')
        return from_language, to_language

    @staticmethod
    def warning_auto_lang(translator: str, default_from_language: str, if_print_warning: bool = True) -> str:
        if if_print_warning:
            warn_tips = f'Unsupported [from_language=auto({default_from_language} instead)] with [{translator}]!'
            warnings.warn(f'{warn_tips} Please specify it.')
        return default_from_language

    @staticmethod
    def debug_lang_kwargs(from_language: str, to_language: str, default_from_language: str,
                          if_print_warning: bool = True) -> dict:
        kwargs = {
            'from_language': from_language,
            'to_language': to_language,
            'default_from_language': default_from_language,
            'if_print_warning': if_print_warning,
        }
        return kwargs

    @staticmethod
    def debug_language_map(func):
        def make_temp_language_map(from_language: str, to_language: str, default_from_language: str) -> dict:
            if from_language == to_language or to_language == 'auto':
                raise TranslatorError

            temp_language_map = {from_language: to_language}
            if from_language != 'auto':
                temp_language_map.update({to_language: from_language})
            elif default_from_language != to_language:
                temp_language_map.update({default_from_language: to_language, to_language: default_from_language})

            return temp_language_map

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TranslatorError as e:
                if kwargs.get('if_print_warning', True):
                    warnings.warn(f'GetLanguageMapError: {str(e)}.\nThe function make_temp_language_map() works.')
                return make_temp_language_map(kwargs.get('from_language'), kwargs.get('to_language'),
                                              kwargs.get('default_from_language'))

        return _wrapper

    @staticmethod
    def check_input_limit(query_text: str, input_limit: int) -> None:
        if len(query_text) > input_limit:
            raise TranslatorError

    @staticmethod
    def check_query(func):
        def check_query_text(query_text: str,
                             if_ignore_empty_query: bool,
                             if_ignore_limit_of_length: bool,
                             limit_of_length: int
                             ) -> str:

            if not isinstance(query_text, str):
                raise TranslatorError

            query_text = query_text.strip()
            qt_length = len(query_text)
            if qt_length == 0 and not if_ignore_empty_query:
                raise TranslatorError("The `query_text` can't be empty!")
            if qt_length >= limit_of_length and not if_ignore_limit_of_length:
                raise TranslatorError('The length of `query_text` exceeds the limit.')
            else:
                if qt_length >= limit_of_length:
                    warnings.warn(f'The length of `query_text` is {qt_length}, above {limit_of_length}.')
                    return query_text[:limit_of_length - 1]
            return query_text

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if_ignore_empty_query = kwargs.get('if_ignore_empty_query', False)
            if_ignore_limit_of_length = kwargs.get('if_ignore_limit_of_length', False)
            limit_of_length = kwargs.get('limit_of_length', 20000)
            is_detail_result = kwargs.get('is_detail_result', False)

            query_text = list(args)[1] if len(args) >= 2 else kwargs.get('query_text')
            query_text = check_query_text(query_text, if_ignore_empty_query, if_ignore_limit_of_length, limit_of_length)
            if not query_text and if_ignore_empty_query:
                return {'data': query_text} if is_detail_result else query_text

            if len(args) >= 2:
                new_args = list(args)
                new_args[1] = query_text
                return func(*tuple(new_args), **kwargs)
            return func(*args, **{**kwargs, **{'query_text': query_text}})

        return _wrapper

    @staticmethod
    def uncertified(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                raise_tips1 = f'The function {func.__name__[:-4]}() has been not certified yet.'
                raise_tips2_url = 'https://github.com/UlionTse/translators#supported-translation-services'
                raise_tips2 = f'Please read for details: Status of Translator on this webpage({raise_tips2_url}).'
                raise TranslatorError(f'{raise_tips1} {raise_tips2}')

        return _wrapper

    # @staticmethod
    # def certified(func):
    #     @functools.wraps(func)
    #     def _wrapper(*args, **kwargs):
    #         try:
    #             return func(*args, **kwargs)
    #         except Exception as e:
    #             raise TranslatorError(e)
    #     return _wrapper


class GuestSeverRegion(Tse):
    def __init__(self):
        super().__init__()
        self.get_addr_url = 'https://geolocation.onetrust.com/cookieconsentpub/v1/geo/location'
        self.get_ip_url = 'https://httpbin.org/ip'
        self.ip_api_addr_url = 'http://ip-api.com/json'  # must http.
        self.ip_tb_add_url = 'https://ip.taobao.com/outGetIpInfo'
        self.default_region = os.environ.get('translators_default_region', None)

    @property
    def get_server_region(self, if_judge_cn: bool = True) -> str:
        if self.default_region:
            sys.stderr.write(f'Using customized region {self.default_region} server backend.\n\n')
            return ('CN' if self.default_region == 'China' else 'EN') if if_judge_cn else self.default_region

        _headers_fn = lambda url: self.get_headers(url, if_api=False, if_referer_for_host=True)
        try:
            try:
                data = json.loads(requests.get(self.get_addr_url, headers=_headers_fn(self.get_addr_url)).text[9:-2])
                sys.stderr.write(f'Using region {data.get("stateName")} server backend.\n\n')
                return data.get('country') if if_judge_cn else data.get("stateName")
            except requests.exceptions.Timeout:
                ip_address = requests.get(self.get_ip_url, headers=_headers_fn(self.get_ip_url)).json()['origin']
                payload = {'ip': ip_address, 'accessKey': 'alibaba-inc'}
                data = requests.post(url=self.ip_tb_add_url, data=payload,
                                     headers=_headers_fn(self.ip_tb_add_url)).json().get('data')
                return data.get('country_id')  # region_id

        except requests.exceptions.ConnectionError:
            raise TranslatorError('Unable to connect the Internet.\n\n')
        except:
            warnings.warn('Unable to find server backend.\n\n')
            region = input('Please input your server region need to visit:\neg: [Qatar, China, ...]\n\n')
            sys.stderr.write(f'Using region {region} server backend.\n\n')
            return 'CN' if region == 'China' else 'EN'


class GoogleV1(Tse):
    def __init__(self, server_region='EN'):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = None
        self.cn_host_url = 'https://translate.google.cn'
        self.en_host_url = 'https://translate.google.com'
        self.api_url = None
        self.server_region = server_region
        self.host_headers = None
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @staticmethod
    def _xr(a: int, b: str) -> int:
        size_b = len(b)
        c = 0
        while c < size_b - 2:
            d = b[c + 2]
            d = ord(d[0]) - 87 if 'a' <= d else int(d)
            d = (a % 2 ** 32) >> d if '+' == b[c + 1] else a << d
            a = a + d & (2 ** 32 - 1) if '+' == b[c] else a ^ d
            c += 3
        return a

    @staticmethod
    def _ints(text: str) -> List[int]:
        ints = []
        for v in text:
            int_v = ord(v)
            if int_v < 2 ** 16:
                ints.append(int_v)
            else:
                # unicode, emoji
                ints.append(int((int_v - 2 ** 16) / 2 ** 10 + 55296))
                ints.append(int((int_v - 2 ** 16) % 2 ** 10 + 56320))
        return ints

    def acquire(self, text: str, tkk: str) -> str:
        ints = self._ints(text)
        size = len(ints)
        e = []
        g = 0

        while g < size:
            l = ints[g]
            if l < 2 ** 7:  # 128(ascii)
                e.append(l)
            else:
                if l < 2 ** 11:  # 2048
                    e.append(l >> 6 | 192)
                else:
                    if (l & 64512) == 55296 and g + 1 < size and ints[g + 1] & 64512 == 56320:
                        g += 1
                        l = 65536 + ((l & 1023) << 10) + (ints[g] & 1023)
                        e.append(l >> 18 | 240)
                        e.append(l >> 12 & 63 | 128)
                    else:
                        e.append(l >> 12 | 224)
                    e.append(l >> 6 & 63 | 128)
                e.append(l & 63 | 128)
            g += 1

        b = tkk if tkk != '0' else ''
        d = b.split('.')
        b = int(d[0]) if len(d) > 1 else 0

        a = b
        for value in e:
            a += value
            a = self._xr(a, '+-a^+6')
        a = self._xr(a, '+-3^+b+-f')
        a ^= int(d[1]) if len(d) > 1 else 0
        if a < 0:
            a = (a & (2 ** 31 - 1)) + 2 ** 31
        a %= int(1E6)
        return '{}.{}'.format(a, a ^ b)

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        et = lxml.etree.HTML(host_html)
        lang_list = sorted(list(set(et.xpath('//*/@data-language-code'))))
        return {}.fromkeys(lang_list, lang_list)

    def get_tkk(self, host_html: str) -> str:
        return re.compile("tkk:'(.*?)'").findall(host_html)[0]

    @Tse.time_stat
    @Tse.check_query
    def google_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.google.com, https://translate.google.cn.
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param if_use_cn_host: bool, default None.
                :param reset_host_url: str, default None.
                :param if_check_reset_host_url: bool, default True.
        :return: str or dict
        """

        reset_host_url = kwargs.get('reset_host_url', None)
        if reset_host_url and reset_host_url != self.host_url:
            if kwargs.get('if_check_reset_host_url', True) and not reset_host_url[:25] == 'https://translate.google.':
                raise TranslatorError
            self.host_url = reset_host_url.strip('/')
        else:
            use_cn_condition = kwargs.get('if_use_cn_host', None) or self.server_region == 'CN'
            self.host_url = self.cn_host_url if use_cn_condition else self.en_host_url

        if self.host_url[-2:] == 'cn':
            raise TranslatorError('Google service was offline in inland of China on Oct 2022.')

        self.host_headers = self.host_headers or self.get_headers(self.host_url, if_api=False)

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.api_url):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text

            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, self.session, timeout, proxies, **debug_lang_kwargs)
            from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                             output_zh=self.output_zh)

            tkk = self.get_tkk(host_html)
            tk = self.acquire(query_text, tkk)

            api_url_part_1 = '/translate_a/single?client={0}&sl={1}&tl={2}&hl=zh-CN&dt=at&dt=bd&dt=ex'.format('webapp',
                                                                                                              from_language,
                                                                                                              to_language)
            api_url_part_2 = '&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&source=bh&ssel=0&tsel=0&kc=1'
            api_url_part_3 = '&tk={0}&q={1}'.format(tk, urllib.parse.quote(query_text))
            self.api_url = ''.join([self.host_url, api_url_part_1, api_url_part_2, api_url_part_3])  # [t,webapp]

        r = self.session.get(self.api_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else ''.join([item[0] for item in data[0] if isinstance(item[0], str)])


class GoogleV2(Tse):
    def __init__(self, server_region='EN'):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = None
        self.cn_host_url = 'https://translate.google.cn'
        self.en_host_url = 'https://translate.google.com'
        self.api_url = None
        self.api_url_path = '/_/TranslateWebserverUi/data/batchexecute'
        self.server_region = server_region
        self.host_headers = None
        self.api_headers = None
        self.language_map = None
        self.session = None
        self.rpcid = 'MkEWBc'
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        et = lxml.etree.HTML(host_html)
        lang_list = sorted(list(set(et.xpath('//*/@data-language-code'))))
        return {}.fromkeys(lang_list, lang_list)

    def get_rpc(self, query_text: str, from_language: str, to_language: str) -> dict:
        param = json.dumps([[query_text, from_language, to_language, True], [1]])
        rpc = json.dumps([[[self.rpcid, param, None, "generic"]]])
        return {'f.req': rpc}

    def get_info(self, host_html: str) -> dict:
        data_str = re.compile(r'window.WIZ_global_data = (.*?);</script>').findall(host_html)[0]
        data = execjs.eval(data_str)
        return {'bl': data['cfb2h'], 'f.sid': data['FdrFJe']}

    def get_consent_cookie(self, consent_html: str) -> str:  # by mercuree. merged but not verify.
        et = lxml.etree.HTML(consent_html)
        input_element = et.xpath('.//input[@type="hidden"][@name="v"]')
        cookie_value = input_element[0].attrib.get('value') if input_element else 'cb'
        return f'CONSENT=YES+{cookie_value}'  # cookie CONSENT=YES+cb works for now

    @Tse.time_stat
    @Tse.check_query
    def google_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.google.com, https://translate.google.cn.
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param reset_host_url: str, default None.
                :param if_check_reset_host_url: bool, default True.
        :return: str or dict
        """

        reset_host_url = kwargs.get('reset_host_url', None)
        if reset_host_url and reset_host_url != self.host_url:
            if kwargs.get('if_check_reset_host_url', True) and not reset_host_url[:25] == 'https://translate.google.':
                raise TranslatorError
            self.host_url = reset_host_url.strip('/')
        else:
            use_cn_condition = kwargs.get('if_use_cn_host', None) or self.server_region == 'CN'
            self.host_url = self.cn_host_url if use_cn_condition else self.en_host_url

        if self.host_url[-2:] == 'cn':
            raise TranslatorError('Google service was offline in inland of China on Oct 2022.')

        self.api_url = f'{self.host_url}{self.api_url_path}'
        self.host_headers = self.host_headers or self.get_headers(self.host_url, if_api=False)  # reuse cookie header
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_referer_for_host=True, if_ajax_for_api=True)

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            r = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            if 'consent.google.com' == urllib.parse.urlparse(r.url).hostname:
                self.host_headers.update({'cookie': self.get_consent_cookie(r.text)})
                host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                             proxies=proxies).text
            else:
                host_html = r.text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        rpc_data = self.get_rpc(query_text, from_language, to_language)
        rpc_data = urllib.parse.urlencode(rpc_data)
        r = self.session.post(self.api_url, headers=self.api_headers, data=rpc_data, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        json_data = json.loads(r.text[6:])
        data = json.loads(json_data[0][2])
        time.sleep(sleep_seconds)
        self.query_count += 1
        return {'data': data} if is_detail_result else ' '.join(
            [x[0] for x in (data[1][0][0][5] or data[1][0]) if x[0]])


class BaiduV1(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.baidu.com'
        self.api_url = 'https://fanyi.baidu.com/transapi'
        self.get_lang_url = None
        self.get_lang_url_pattern = 'https://fanyi-cdn.cdn.bcebos.com/webStatic/translation/js/index.(.*?).js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    # @Tse.debug_language_map
    # def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
    #     lang_str = re.compile('langMap: {(.*?)}').search(host_html.replace('\n', '').replace('  ', '')).group()[8:]
    #     return execjs.eval(lang_str)

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        js_html = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).text
        lang_str = re.compile('exports={auto:(.*?)}}}},').search(js_html).group()[8:-3]
        lang_list = re.compile('(\\w+):{zhName:').findall(lang_str)
        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    @Tse.time_stat
    @Tse.check_query
    def baidu_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.baidu.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                 proxies=proxies)  # must twice, send cookies.
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text

            if not self.get_lang_url:
                self.get_lang_url = re.compile(self.get_lang_url_pattern).search(host_html).group()

            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.get_lang_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = {
            'from': from_language,
            'to': to_language,
            'query': query_text,
            'source': 'txt',
        }
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join([item['dst'] for item in data['data']])


class BaiduV2(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.baidu.com'
        self.api_url = 'https://fanyi.baidu.com/v2transapi'
        self.langdetect_url = 'https://fanyi.baidu.com/langdetect'
        self.get_sign_url = 'https://fanyi-cdn.cdn.bcebos.com/static/translation/pkg/index_bd36cef.js'
        self.get_lang_url = None
        self.get_lang_url_pattern = 'https://fanyi-cdn.cdn.bcebos.com/webStatic/translation/js/index.(.*?).js'
        self.acs_url = 'https://dlswbr.baidu.com/heicha/mm/{i}/acs-{i}.js'.format(i=2060)
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.professional_field = ('common', 'medicine', 'electronics', 'mechanics', 'novel')
        self.token = None
        self.sign = None
        self.acs_token = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        js_html = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).text
        lang_str = re.compile('exports={auto:(.*?)}}}},').search(js_html).group()[8:-3]
        lang_list = re.compile('(\\w+):{zhName:').findall(lang_str)
        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    def get_sign(self, query_text: str, host_html: str, ss: SessionType, headers: dict, timeout: float,
                 proxies: dict) -> str:
        gtk_list = re.compile("""window.gtk = '(.*?)';|window.gtk = "(.*?)";""").findall(host_html)[0]
        gtk = gtk_list[0] or gtk_list[1]

        sign_html = ss.get(self.get_sign_url, headers=headers, timeout=timeout, proxies=proxies).text
        begin_label = 'define("translation:widget/translate/input/pGrab",function(r,o,t){'
        end_label = 'var i=null;t.exports=e});'
        sign_js = sign_html[sign_html.find(begin_label) + len(begin_label):sign_html.find(end_label)]
        sign_js = sign_js.replace('function e(r)', 'function e(r,i)')
        return execjs.compile(sign_js).call('e', query_text, gtk)

    def get_tk(self, host_html: str) -> str:
        tk_list = re.compile("""token: '(.*?)',|token: "(.*?)",""").findall(host_html)[0]
        return tk_list[0] or tk_list[1]

    # def get_acs_token(self):
    #     pass

    @Tse.time_stat
    @Tse.check_query
    def baidu_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.baidu.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default 'common'. Choose from ('common', 'medicine', 'electronics', 'mechanics', 'novel')
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', 'common')
        if use_domain not in self.professional_field:  # only support zh-en, en-zh.
            raise TranslatorError

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.token and self.sign):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                 proxies=proxies)  # must twice, send cookies.
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.token = self.get_tk(host_html)
            self.sign = self.get_sign(query_text, host_html, self.session, self.host_headers, timeout, proxies)

            if not self.get_lang_url:
                self.get_lang_url = re.compile(self.get_lang_url_pattern).search(host_html).group()

            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.get_lang_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        if from_language == 'auto':
            res = self.session.post(self.langdetect_url, headers=self.api_headers, data={"query": query_text},
                                    timeout=timeout, proxies=proxies)
            from_language = res.json()['lan']

        params = {"from": from_language, "to": to_language}
        payload = {
            "from": from_language,
            "to": to_language,
            "query": query_text,  # from urllib.parse import quote_plus
            "transtype": "realtime",  # ["translang","realtime"]
            "simple_means_flag": "3",
            "sign": self.sign,
            "token": self.token,
            "domain": use_domain,
        }
        payload = urllib.parse.urlencode(payload).encode('utf-8')
        # self.api_headers.update({'Acs-Token': self.acs_token})
        r = self.session.post(self.api_url, params=params, data=payload, headers=self.api_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join([x['dst'] for x in data['trans_result']['data']])


class YoudaoV1(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.youdao.com'
        self.api_url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        self.language_url = 'https://api-overmind.youdao.com/openapi/get/luna/dict/luna-front/prod/langType'
        self.get_sign_old_url = 'https://shared.ydstatic.com/fanyi/newweb/v1.0.29/scripts/newweb/fanyi.min.js'
        self.get_sign_url = None
        self.get_sign_pattern = 'https://shared.ydstatic.com/fanyi/newweb/(.*?)/scripts/newweb/fanyi.min.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.sign_key = None
        self.query_count = 0
        self.output_zh = 'zh-CHS'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    # @Tse.debug_language_map
    # def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
    #     et = lxml.etree.HTML(host_html)
    #     lang_list = et.xpath('//*[@id="languageSelect"]/li/@data-value')
    #     lang_list = [(x.split('2')[0], [x.split('2')[1]]) for x in lang_list if '2' in x]
    #     lang_map = dict(map(lambda x: x, lang_list))
    #     lang_map.pop('zh-CHS')
    #     lang_map.update({'zh-CHS': list(lang_map.keys())})
    #     return lang_map

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        data = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).json()
        lang_list = sorted([it['code'] for it in data['data']['value']['textTranslate']['specify']])
        return {}.fromkeys(lang_list, lang_list)

    def get_sign_key(self, host_html: str, ss: SessionType, timeout: float, proxies: dict) -> str:
        try:
            if not self.get_sign_url:
                self.get_sign_url = re.compile(self.get_sign_pattern).search(host_html).group()
            r = ss.get(self.get_sign_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            r.raise_for_status()
        except:
            r = ss.get(self.get_sign_old_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            r.raise_for_status()
        sign = re.compile('md5\\("fanyideskweb" \\+ e \\+ i \\+ "(.*?)"\\)').findall(r.text)
        return sign[0] if sign and sign != [''] else "Ygy_4c=r#e#4EX^NUGUc5"  # v1.1.10

    def get_form(self, query_text: str, from_language: str, to_language: str, sign_key: str) -> dict:
        ts = str(self.get_timestamp())
        salt = str(ts) + str(random.randrange(0, 10))
        sign_text = ''.join(['fanyideskweb', query_text, salt, sign_key])
        sign = hashlib.md5(sign_text.encode()).hexdigest()
        bv = hashlib.md5(self.api_headers['User-Agent'][8:].encode()).hexdigest()
        form = {
            'i': query_text,
            'from': from_language,
            'to': to_language,
            'lts': ts,  # r = "" + (new Date).getTime()
            'salt': salt,  # i = r + parseInt(10 * Math.random(), 10)
            'sign': sign,  # n.md5("fanyideskweb" + e + i + "n%A-rKaT5fb[Gy?;N5@Tj"),e=text
            'bv': bv,  # n.md5(navigator.appVersion)
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME',
            # not time.["FY_BY_REALTlME", "FY_BY_DEFAULT", "FY_BY_CLICKBUTTION", "lan-select"]
            # 'typoResult': 'false'
        }
        return form

    @Tse.time_stat
    @Tse.check_query
    def youdao_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.youdao.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.sign_key):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.sign_key = self.get_sign_key(host_html, self.session, timeout, proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.language_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        form = self.get_form(query_text, from_language, to_language, self.sign_key)
        r = self.session.post(self.api_url, data=form, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join(
            [' '.join([it['tgt'] for it in item]) for item in data['translateResult']])


class YoudaoV2(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.youdao.com'
        self.api_url = 'https://dict.youdao.com/webtranslate'
        self.api_host = 'https://dict.youdao.com'
        self.get_js_url = None
        self.get_js_pattern = 'js/app.(.*?).js'
        self.get_sign_url = None
        self.get_sign_pattern = ''
        self.login_url = 'https://dict.youdao.com/login/acc/query/accountinfo'
        self.language_url = 'https://api-overmind.youdao.com/openapi/get/luna/dict/luna-front/prod/langType'
        self.domain_url = 'https://doctrans-service.youdao.com/common/enums/list?key=domain'
        self.get_key_url = 'https://dict.youdao.com/webtranslate/key'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.api_headers.update({'Host': self.api_host})
        self.language_map = None
        self.session = None
        self.professional_field = ('0', '1', '2', '3')
        self.professional_field_map = None
        self.default_key = None
        self.secret_key = None
        self.decode_key = None
        self.decode_iv = None
        self.query_count = 0
        self.output_zh = 'zh-CHS'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        data = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).json()
        lang_list = sorted([it['code'] for it in data['data']['value']['textTranslate']['specify']])
        return {}.fromkeys(lang_list, lang_list)

    def get_default_key(self, js_html: str) -> str:
        return re.compile('="webfanyi-key-getter",(\\w+)="(\\w+)";').search(js_html).group(2)

    def get_sign(self, key: str, timestmp: int) -> str:
        value = f'client=fanyideskweb&mysticTime={timestmp}&product=webfanyi&key={key}'
        return hashlib.md5(value.encode()).hexdigest()

    def get_payload(self, keyid: str, key: str, timestamp: int, **kwargs: str) -> dict:
        if keyid not in ('webfanyi-key-getter', 'webfanyi'):
            raise TranslatorError

        payload = {
            'keyid': keyid,
            'mysticTime': str(timestamp),
            'sign': self.get_sign(key, timestamp),
            'client': 'fanyideskweb',
            'product': 'webfanyi',
            'appVersion': '1.0.0',
            'vendor': 'web',
            'keyfrom': 'fanyi.web',
            'pointParam': 'client,mysticTime,product',
        }
        return {**kwargs, **payload} if keyid == 'webfanyi' else payload

    def decrypt(self, cipher_text: str, decrypt_dictionary: dict) -> str:
        _ciphertext = ''.join(list(map(lambda k: decrypt_dictionary[k], cipher_text)))
        return base64.b64decode(_ciphertext).decode()

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def youdao_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.youdao.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default '0'. Choose from ('0','1','2','3')
        :return: str or dict
        """

        domain = kwargs.get('professional_field', '0')
        if domain not in self.professional_field:
            raise TranslatorError

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.secret_key):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            _ = self.session.get(self.login_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.professional_field_map = \
                self.session.get(self.domain_url, headers=self.host_headers, timeout=timeout, proxies=proxies).json()[
                    'data']
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.language_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

            self.get_js_url = ''.join([self.host_url, '/', re.compile(self.get_js_pattern).search(host_html).group()])
            js_html = self.session.get(self.get_js_url, headers=self.host_headers, timeout=timeout,
                                       proxies=proxies).text

            self.decode_key = re.compile('decodeKey:"(.*?)",').search(js_html).group(1)
            self.decode_iv = re.compile('decodeIv:"(.*?)",').search(js_html).group(1)
            self.default_key = self.get_default_key(js_html)

            params = self.get_payload(keyid='webfanyi-key-getter', key=self.default_key, timestamp=self.get_timestamp())
            key_r = self.session.get(self.get_key_url, params=params, headers=self.api_headers, timeout=timeout,
                                     proxies=proxies)
            self.secret_key = key_r.json()['data']['secretKey']

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        translate_form = {
            'i': query_text,
            'from': from_language,
            'to': to_language if from_language != 'auto' else '',
            'domain': domain,
            'dictResult': 'true',
        }
        payload = self.get_payload(keyid='webfanyi', key=self.default_key, timestamp=self.get_timestamp(),
                                   **translate_form)
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()  # raise TranslatorError('YoudaoV2 has not been completed.')  # TODO
        data = self.decrypt(r.text, decrypt_dictionary={})
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else str(data)  # TODO


class YoudaoV3(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://ai.youdao.com/product-fanyi-text.s'
        self.api_url = 'https://aidemo.youdao.com/trans'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh-CHS'
        self.input_limit = int(1e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        et = lxml.etree.HTML(host_html)
        lang_list = et.xpath('//*[@id="customSelectOption"]/li/a/@val')
        lang_list = sorted([it.split('2')[1] for it in lang_list if f'{self.output_zh}2' in it])
        return {**{lang: [self.output_zh] for lang in lang_list}, **{self.output_zh: lang_list}}

    @Tse.time_stat
    @Tse.check_query
    def youdao_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://ai.youdao.com/product-fanyi-text.s
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        if from_language == 'auto':
            from_language = to_language = 'Auto'

        payload = {'q': query_text, 'from': from_language, 'to': to_language}
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translation'][0]


class QQFanyi(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.qq.com'
        self.api_url = 'https://fanyi.qq.com/api/translate'
        self.get_language_url = 'https://fanyi.qq.com/js/index.js'
        self.get_qt_url = 'https://fanyi.qq.com/api/reauth12f'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.qt_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.language_map = None
        self.session = None
        self.qtv_qtk = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(2e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, ss: SessionType, language_url: str, timeout: Optional[float], proxies: Optional[dict],
                         **kwargs: LangMapKwargsType) -> dict:
        r = ss.get(language_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        lang_map_str = re.compile('C={(.*?)}|languagePair = {(.*?)}', flags=re.S).search(r.text).group()  # C=
        return execjs.eval(lang_map_str)

    def get_qt(self, ss: SessionType, timeout: float, proxies: dict) -> dict:
        return ss.post(self.get_qt_url, headers=self.qt_headers, json=self.qtv_qtk, timeout=timeout,
                       proxies=proxies).json()

    @Tse.time_stat
    @Tse.check_query
    def qqFanyi_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.qq.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.qtv_qtk):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
            self.qtv_qtk = self.get_qt(self.session, timeout, proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.session, self.get_language_url, timeout, proxies,
                                                      **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = {
            'source': from_language,
            'target': to_language,
            'sourceText': query_text,
            'qtv': self.qtv_qtk.get('qtv', ''),
            'qtk': self.qtv_qtk.get('qtk', ''),
            'ticket': '',
            'randstr': '',
            'sessionUuid': f'translate_uuid{self.get_timestamp()}',
        }
        r = self.session.post(self.api_url, headers=self.api_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else ''.join(
            item['targetText'] for item in data['translate']['records'])  # auto whitespace


class QQTranSmart(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://transmart.qq.com'
        self.api_url = 'https://transmart.qq.com/api/imt'
        self.get_lang_url = None
        self.get_lang_url_pattern = '/assets/vendor.(.*?).js'  # e4c6831c
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.language_map = None
        self.session = None
        self.uuid = str(uuid.uuid4())
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, timeout: Optional[float], proxies: Optional[dict],
                         **kwargs: LangMapKwargsType) -> dict:
        js_html = ss.get(lang_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
        lang_str_list = re.compile('lngs:\\[(.*?)]').findall(js_html)  # 'lngs:\\[(.*?)\\]'
        lang_list = [execjs.eval(f'[{x}]') for x in lang_str_list]
        lang_list = sorted(list(set([lang for langs in lang_list for lang in langs])))
        return {}.fromkeys(lang_list, lang_list)

    def get_clientKey(self) -> str:
        return f'browser-firefox-110.0.0-Windows 10-{self.uuid}-{self.get_timestamp()}'

    def split_sentence(self, data: dict) -> List[str]:
        index_pair_list = [[item['start'], item['start'] + item['len']] for item in data['sentence_list']]
        index_list = [i for ii in index_pair_list for i in ii]
        return [data['text'][index_list[i]: index_list[i + 1]] for i in range(len(index_list) - 1)]

    @Tse.time_stat
    @Tse.check_query
    def qqTranSmart_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                        **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://transmart.qq.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text

            if not self.get_lang_url:
                self.get_lang_url = f'{self.host_url}{re.compile(self.get_lang_url_pattern).search(host_html).group()}'
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.get_lang_url, self.session, timeout, proxies,
                                                      **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('qqTranSmart', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        client_key = self.get_clientKey()
        self.api_headers.update({'Cookie': f'client_key={client_key}'})

        split_payload = {
            'header': {
                'fn': 'text_analysis',
                'client_key': client_key,
            },
            'type': 'plain',
            'text': query_text,
            'normalize': {'merge_broken_line': 'false'}
        }
        split_data = self.session.post(self.api_url, json=split_payload, headers=self.api_headers, timeout=timeout,
                                       proxies=proxies).json()
        text_list = self.split_sentence(split_data)

        api_payload = {
            'header': {
                'fn': 'auto_translation',
                'client_key': client_key,
            },
            'type': 'plain',
            'model_category': 'normal',
            'source': {
                'lang': from_language,
                'text_list': [''] + text_list + [''],
            },
            'target': {'lang': to_language}
        }
        r = self.session.post(self.api_url, json=api_payload, headers=self.api_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else ''.join(data['auto_translation'])


class AlibabaV1(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translate.alibaba.com'
        self.api_url = 'https://translate.alibaba.com/translationopenseviceapp/trans/TranslateTextAddAlignment.do'
        self.get_language_url = 'https://translate.alibaba.com/translationopenseviceapp/trans/acquire_supportLanguage.do'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.professional_field = ("general", "message", "offer")
        self.dmtrack_pageid = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    def get_dmtrack_pageid(self, host_response: ResponseType) -> str:
        try:
            e = re.compile("dmtrack_pageid='(\\w+)';").findall(host_response.text)[0]
        except:
            e = ''
        if not e:
            e = host_response.cookies.get_dict().get("cna", "001")
            e = re.compile('[^a-z\\d]').sub(repl='', string=e.lower())[:16]
        else:
            n, r = e[0:16], e[16:26]
            i = hex(int(r, 10))[2:] if re.compile('^[\\-+]?[0-9]+$').match(r) else r
            e = n + i

        s = self.get_timestamp()
        o = ''.join([e, hex(s)[2:]])
        for _ in range(1, 10):
            a = hex(int(0 * 1e10))[2:]  # int->str: 16, '0x'
            o += a
        return o[:42]

    @Tse.debug_language_map
    def get_language_map(self, ss: SessionType, lang_url: str, use_domain: str, dmtrack_pageid: str,
                         timeout: Optional[float], proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        params = {'dmtrack_pageid': dmtrack_pageid, 'biz_type': use_domain}
        language_dict = ss.get(lang_url, params=params, headers=self.host_headers, timeout=timeout,
                               proxies=proxies).json()
        return dict(map(lambda x: x, [(x['sourceLuange'], x['targetLanguages']) for x in language_dict['languageMap']]))

    @Tse.time_stat
    @Tse.check_query
    def alibaba_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.alibaba.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default 'message', choose from ("general","message","offer")
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', 'message')
        if use_domain not in self.professional_field:
            raise TranslatorError

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.dmtrack_pageid):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_response = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.dmtrack_pageid = self.get_dmtrack_pageid(host_response)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.session, self.get_language_url, use_domain,
                                                      self.dmtrack_pageid, timeout, proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        payload = {
            "srcLanguage": from_language,
            "tgtLanguage": to_language,
            "srcText": query_text,
            "bizType": use_domain,
            "viewType": "",
            "source": "",
        }
        params = {"dmtrack_pageid": self.dmtrack_pageid}
        r = self.session.post(self.api_url, headers=self.api_headers, params=params, data=payload, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['listTargetText'][0]


class AlibabaV2(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translate.alibaba.com'
        self.api_url = 'https://translate.alibaba.com/api/translate/text'
        self.csrf_url = 'https://translate.alibaba.com/api/translate/csrftoken'
        self.get_language_pattern = '//lang.alicdn.com/mcms/translation-open-portal/(.*?)/translation-open-portal_interface.json'
        self.get_language_url = None
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=False,
                                            if_multipart_for_api=True)
        self.language_map = None
        self.detail_language_map = None
        self.professional_field = ('general',)
        self.csrf_token = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_paragraph = re.compile('"en_US":{(.*?)},"zh_CN":{').search(lang_html).group().replace('",', '",\n')
        lang_items = re.compile('interface.(.*?)":"(.*?)"').findall(lang_paragraph)
        _fn_filter = lambda k, v: 1 if (len(k) <= 3 or (len(k) == 5 and '-' in k)) and len(v.split(' ')) <= 2 else 0
        lang_items = sorted([(k, v) for k, v in lang_items if _fn_filter(k, v)])
        d_lang_map = {k: v for k, v in lang_items}
        lang_list = list(d_lang_map.keys())
        return {}.fromkeys(lang_list, lang_list)

    def get_d_lang_map(self, lang_html: str) -> dict:
        lang_paragraph = re.compile('"en_US":{(.*?)},"zh_CN":{').search(lang_html).group().replace('",', '",\n')
        lang_items = re.compile('interface.(.*?)":"(.*?)"').findall(lang_paragraph)
        _fn_filter = lambda k, v: 1 if (len(k) <= 3 or (len(k) == 5 and '-' in k)) and len(v.split(' ')) <= 2 else 0
        lang_items = sorted([(k, v) for k, v in lang_items if _fn_filter(k, v)])
        return {k: v for k, v in lang_items}

    @Tse.time_stat
    @Tse.check_query
    def alibaba_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.alibaba.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default 'message', choose from ("general",)
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', 'general')
        if use_domain not in self.professional_field:
            raise TranslatorError

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.csrf_token):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.get_language_url = f'https:{re.compile(self.get_language_pattern).search(host_html).group()}'
            lang_html = self.session.get(self.get_language_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(lang_html, **debug_lang_kwargs)
            self.detail_language_map = self.get_d_lang_map(lang_html)

            _ = self.session.get(self.csrf_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.csrf_token = self.session.get(self.csrf_url, headers=self.host_headers, timeout=timeout,
                                               proxies=proxies).json()
            self.api_headers.update({self.csrf_token['headerName']: self.csrf_token['token']})

        from_language, to_language = self.check_language(from_language, to_language, self.language_map, self.output_zh)
        files_data = {
            'query': (None, query_text),
            'srcLang': (None, from_language),
            'tgtLang': (None, to_language),
            '_csrf': (None, self.csrf_token['token']),
            'domain': (None, self.professional_field[0]),
        }  # Content-Type: multipart/form-data
        r = self.session.post(self.api_url, files=files_data, headers=self.api_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['data']['translateText']


class Bing(Tse):
    def __init__(self, server_region='EN'):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = None
        self.cn_host_url = 'https://cn.bing.com/Translator'
        self.en_host_url = 'https://www.bing.com/Translator'
        self.server_region = server_region
        self.api_url = None
        self.host_headers = None
        self.api_headers = None
        self.language_map = None
        self.session = None
        self.tk = None
        self.ig_iid = None
        self.query_count = 0
        self.output_auto = 'auto-detect'
        self.output_zh = 'zh-Hans'
        self.input_limit = int(1e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        et = lxml.etree.HTML(host_html)
        lang_list = et.xpath('//*[@id="tta_srcsl"]/option/@value') or et.xpath('//*[@id="t_srcAllLang"]/option/@value')
        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    def get_ig_iid(self, host_html: str) -> dict:
        et = lxml.etree.HTML(host_html)
        # iid = et.xpath('//*[@id="tta_outGDCont"]/@data-iid')[0]  # browser page is different between request page.
        iid = 'translator.5028'
        ig = re.compile('IG:"(.*?)"').findall(host_html)[0]
        return {'iid': iid, 'ig': ig}

    def get_tk(self, host_html: str) -> dict:
        result_str = re.compile('var params_AbusePreventionHelper = (.*?);').findall(host_html)[0]
        result = execjs.eval(result_str)
        return {'key': result[0], 'token': result[1]}

    @Tse.time_stat
    @Tse.check_query
    def bing_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                 **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://bing.com/Translator, https://cn.bing.com/Translator.
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param if_use_cn_host: bool, default None.
        :return: str or dict
        """

        use_cn_condition = kwargs.get('if_use_cn_host', None) or self.server_region == 'CN'
        self.host_url = self.cn_host_url if use_cn_condition else self.en_host_url
        self.api_url = self.host_url.replace('Translator', 'ttranslatev3')
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.tk and self.ig_iid):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.tk = self.get_tk(host_html)
            self.ig_iid = self.get_ig_iid(host_html)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh, output_auto=self.output_auto)

        payload = {
            'text': query_text,
            'fromLang': from_language,
            'to': to_language,
            'tryFetchingGenderDebiasedTranslations': 'true'
        }
        payload = {**payload, **self.tk}
        api_url_param = f'?isVertical=1&&IG={self.ig_iid["ig"]}&IID={self.ig_iid["iid"]}'
        api_url = ''.join([self.api_url, api_url_param])
        r = self.session.post(api_url, headers=self.host_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data[0] if is_detail_result else data[0]['translations'][0]['text']


class Sogou(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.sogou.com/text'
        self.api_url = 'https://fanyi.sogou.com/api/transpc/text/result'
        self.get_language_old_url = 'https://search.sogoucdn.com/translate/pc/static/js/app.7016e0df.js'
        self.get_language_pattern = '//search.sogoucdn.com/translate/pc/static/js/vendors.(.*?).js'
        self.get_language_url = None
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.uuid = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh-CHS'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, lang_old_url: str, ss: SessionType, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        try:
            if not self.get_language_url:
                lang_url_path = re.compile(self.get_language_pattern).search(host_html).group()
                self.get_language_url = ''.join(['https:', lang_url_path])
            lang_html = ss.get(self.get_language_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
        except:
            lang_html = ss.get(lang_old_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text

        lang_list_str = re.compile('"ALL":\\[(.*?)]').search(lang_html).group().replace('!0', '1').replace('!1', '0')[
                        6:]
        lang_item_list = json.loads(lang_list_str)
        lang_list = [item['lang'] for item in lang_item_list if item['play'] == 1]
        return {}.fromkeys(lang_list, lang_list)

    # def get_uuid(self) -> str:
    #     _uuid = ''
    #     for i in range(8):
    #         _uuid += hex(int(65536 * (1 + 0)))[2:][1:]
    #         if i in range(1, 5):
    #             _uuid += '-'
    #     return _uuid

    def get_form(self, query_text: str, from_language: str, to_language: str, uid: str) -> dict:
        sign_text = "" + from_language + to_language + query_text + '109984457'  # window.__INITIAL_STATE__.common.CONFIG.secretCode
        sign = hashlib.md5(sign_text.encode()).hexdigest()
        form = {
            "from": from_language,
            "to": to_language,
            "text": query_text,
            "uuid": uid,
            "s": sign,
            "client": "pc",  # wap
            "fr": "browser_pc",  # browser_wap
            "needQc": "1",
        }
        return form

    @Tse.time_stat
    @Tse.check_query
    def sogou_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.sogou.com/text
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.uuid):
            self.uuid = str(uuid.uuid4())
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, self.get_language_old_url, self.session, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = self.get_form(query_text, from_language, to_language, self.uuid)
        r = self.session.post(self.api_url, headers=self.api_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['data']['translate']['dit']


class Caiyun(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.caiyunapp.com'
        self.api_url = 'https://api.interpreter.caiyunai.com/v1/translator'
        self.get_js_pattern = '/assets/index.(.*?).js'
        self.get_js_url = None
        self.get_jwt_url = 'https://api.interpreter.caiyunai.com/v1/user/jwt/generate'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=False, if_json_for_api=True)
        self.language_map = None
        self.session = None
        self.professional_field = (None, "medicine", "law", "machinery",)
        self.browser_data = {'browser_id': ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 32))}
        self.normal_key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '0123456789' + '=.+-_/'
        self.cipher_key = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm' + '0123456789' + '=.+-_/'
        self.decrypt_dictionary = self.crypt(if_de=True)
        self.tk = None
        self.jwt = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, js_html: str, **kwargs: LangMapKwargsType) -> dict:
        return execjs.eval(re.compile('={auto:\\[(.*?)}').search(js_html).group()[1:])

    def get_tk(self, js_html: str) -> str:
        return re.compile('headers\\["X-Authorization"]="(.*?)",').findall(js_html)[0]

    # def get_jwt(self, browser_id: str, api_headers: dict, ss: SessionType, timeout: float, proxies: dict) -> str:
    #     data = {"browser_id": browser_id}
    #     return ss.post(self.get_jwt_url, json=data, headers=api_headers, timeout=timeout, proxies=proxies).json()['jwt']

    def crypt(self, if_de: bool = True) -> dict:
        if if_de:
            return {k: v for k, v in zip(self.cipher_key, self.normal_key)}
        return {v: k for k, v in zip(self.cipher_key, self.normal_key)}

    def encrypt(self, plain_text: str) -> str:
        encrypt_dictionary = self.crypt(if_de=False)
        _cipher_text = base64.b64encode(plain_text.encode()).decode()
        return ''.join(list(map(lambda k: encrypt_dictionary[k], _cipher_text)))

    def decrypt(self, cipher_text: str) -> str:
        _ciphertext = ''.join(list(map(lambda k: self.decrypt_dictionary[k], cipher_text)))
        return base64.b64decode(_ciphertext).decode()

    @Tse.time_stat
    @Tse.check_query
    def caiyun_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.caiyunapp.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default None, choose from (None, "medicine","law","machinery")
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', None)
        if use_domain not in (None, "medicine", "law", "machinery"):
            raise TranslatorError

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.tk and self.jwt):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            js_url_path = re.compile(self.get_js_pattern).search(host_html).group()
            self.get_js_url = ''.join([self.host_url, js_url_path])
            js_html = self.session.get(self.get_js_url, headers=self.host_headers, timeout=timeout,
                                       proxies=proxies).text
            self.tk = self.get_tk(js_html)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(js_html, **debug_lang_kwargs)

            self.api_headers.update({
                "app-name": "xy",
                "device-id": "",
                "os-type": "web",
                "os-version": "",
                "version": "1.8.0",
                "X-Authorization": self.tk,
            })
            jwt_r = self.session.post(self.get_jwt_url, json=self.browser_data, headers=self.api_headers,
                                      timeout=timeout, proxies=proxies)
            self.jwt = jwt_r.json()['jwt']
            self.api_headers.update({"T-Authorization": self.jwt})

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = {
            "cached": "true",
            "dict": "true",
            "media": "text",
            "os_type": "web",
            "replaced": "true",
            "request_id": "web_fanyi",
            "source": query_text.split('\n'),
            "trans_type": f"{from_language}2{to_language}",
            "browser_id": self.browser_data['browser_id'],
        }

        if from_language == 'auto':
            payload.update({'detect': 'true'})
        if use_domain:
            payload.update({"dict_name": use_domain, "use_common_dict": "true"})

        _ = self.session.options(self.api_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
        r = self.session.post(self.api_url, headers=self.api_headers, json=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join([self.decrypt(item) for item in data['target']])


class Deepl(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://www.deepl.com/translator'
        self.api_url = 'https://www2.deepl.com/jsonrpc'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=False, if_json_for_api=True)
        self.params = {'split': {'method': 'LMT_split_text'}, 'handle': {'method': 'LMT_handle_jobs'}}
        self.request_id = int(random.randrange(100, 10000) * 10000 + 4)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_list = list(set(re.compile('translateIntoLang\\.(\\w+)":').findall(host_html)))
        return {}.fromkeys(lang_list, lang_list)

    def split_sentences_param(self, query_text: str, from_language: str) -> dict:
        data = {
            'id': self.request_id,
            'jsonrpc': '2.0',
            'params': {
                'texts': query_text.split('\n'),
                'commonJobParams': {'mode': 'translate'},
                'lang': {
                    'lang_user_selected': from_language,
                    'preference': {
                        'weight': {},
                        'default': 'default',
                    },
                },
            },
        }
        return {**self.params['split'], **data}

    def context_sentences_param(self, sentences: List[str], from_language: str, to_language: str) -> dict:
        sentences = [''] + sentences + ['']
        data = {
            'id': self.request_id + 1,
            'jsonrpc': ' 2.0',
            'params': {
                'priority': 1,  # -1 if 'quality': 'fast'
                'timestamp': self.get_timestamp(),
                'commonJobParams': {
                    # 'regionalVariant': 'en-US',
                    'browserType': 1,
                    'mode': 'translate',
                },
                'jobs': [
                    {
                        'kind': 'default',
                        # 'quality': 'fast', # -1
                        'sentences': [{'id': i - 1, 'prefix': '', 'text': sentences[i]}],
                        'raw_en_context_before': sentences[1:i] if sentences[i - 1] else [],
                        'raw_en_context_after': [sentences[i + 1]] if sentences[i + 1] else [],
                        'preferred_num_beams': 1 if len(sentences) >= 4 else 4,  # 1 if two sentences else 4, len>=2+2
                    } for i in range(1, len(sentences) - 1)
                ],
                'lang': {
                    'preference': {
                        'weight': {},
                        'default': 'default',
                    },
                    'source_lang_user_selected': from_language,  # "source_lang_computed"
                    'target_lang': to_language,
                },
            },
        }
        return {**self.params['handle'], **data}

    @Tse.time_stat
    @Tse.check_query
    def deepl_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.deepl.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, language_map=self.language_map,
                                                         output_zh=self.output_zh, output_auto='auto')
        from_language = from_language.upper() if from_language != 'auto' else from_language
        to_language = to_language.upper() if to_language != 'auto' else to_language

        ssp_data = self.split_sentences_param(query_text, from_language)
        r_s = self.session.post(self.api_url, params=self.params['split'], json=ssp_data, headers=self.api_headers,
                                timeout=timeout, proxies=proxies)
        r_s.raise_for_status()
        s_data = r_s.json()

        s_sentences = [it['sentences'][0]['text'] for item in s_data['result']['texts'] for it in item['chunks']]
        h_data = self.context_sentences_param(s_sentences, from_language, to_language)

        r_cs = self.session.post(self.api_url, params=self.params['handle'], json=h_data, headers=self.api_headers,
                                 timeout=timeout, proxies=proxies)
        r_cs.raise_for_status()
        data = r_cs.json()
        time.sleep(sleep_seconds)
        self.request_id += 3
        self.query_count += 1
        return data if is_detail_result else '\n'.join(
            item['beams'][0]['sentences'][0]["text"] for item in data['result']['translations'])


class Yandex(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://yandex.com'
        self.host_url = 'https://translate.yandex.com'
        self.api_url = 'https://translate.yandex.net/api/v1/tr.json/translate'
        self.api_host = 'https://translate.yandex.net'
        self.detect_language_url = 'https://translate.yandex.net/api/v1/tr.json/detect'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.api_headers.update({'Referer': self.api_host, 'x-retpath-y': self.host_url})
        self.language_map = None
        self.session = None
        self.sid = None
        self.yu = None
        self.yum = None
        self.sprvk = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(1e4)  # ten thousand.
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_str = re.compile('TRANSLATOR_LANGS: {(.*?)},').search(host_html).group(0)[18:-1]
        lang_dict = json.loads(lang_str)
        lang_list = sorted(list(lang_dict.keys()))
        return {}.fromkeys(lang_list, lang_list)

    def get_yum(self) -> str:
        return str(int(time.time() * 1e10))

    # def get_csrf_token(self, host_html: str) -> str:
    #     return re.compile(pattern="CSRF_TOKEN: '(.*?)',").findall(host_html)[0]
    #
    # def get_key(self, host_html: str) -> str:
    #     return re.compile(pattern="SPEECHKIT_KEY: '(.*?)',").findall(host_html)[0]

    def get_sid(self, host_html: str) -> str:
        try:
            sid_find = re.compile("SID: '(.*?)',").findall(host_html)[0]
            return '.'.join([w[::-1] for w in sid_find.split('.')])
        except Exception as e:
            captcha_info = 'SmartCaptcha needs verification'
            if captcha_info in host_html:
                raise TranslatorError(captcha_info)
            raise TranslatorError(str(e))

    def detect_language(self, ss: SessionType, query_text: str, sid: str, yu: str, headers: dict, timeout: float,
                        proxies: dict) -> str:
        params = {
            'sid': sid,
            'yu': yu,
            'text': query_text,
            'srv': 'tr-text',
            'hint': 'en,ru',
            'options': 1
        }
        r = ss.get(self.detect_language_url, params=params, headers=headers, timeout=timeout, proxies=proxies)
        lang = r.json().get('lang')
        return lang if lang else 'en'

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def yandex_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.yandex.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param reset_host_url: str, default None. eg: 'https://translate.yandex.fr'
                :param if_check_reset_host_url: bool, default True.
        :return: str or dict
        """

        reset_host_url = kwargs.get('reset_host_url', None)
        if reset_host_url and reset_host_url != self.host_url:
            if kwargs.get('if_check_reset_host_url', True) and not reset_host_url[:25] == 'https://translate.yandex.':
                raise TranslatorError
            self.host_url = reset_host_url.strip('/')

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.sid and self.yu):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.home_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text

            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

            self.sid = self.get_sid(host_html)
            self.yum = self.get_yum()
            self.yu = self.session.cookies.get_dict().get(
                'yuidss') or f'{random.randint(int(1e8), int(9e8))}{int(time.time())}'
            self.sprvk = self.session.cookies.get_dict().get('spravka')

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        if from_language == 'auto':
            from_language = self.detect_language(self.session, query_text, self.sid, self.yu, self.api_headers, timeout,
                                                 proxies)

        params = {
            'id': f'{self.sid}-{self.query_count}-0',
            'source_lang': from_language,
            'target_lang': to_language,
            'srv': 'tr-text',
            'reason': 'paste',  # 'auto'
            'format': 'text',
            'ajax': 1,
            'yu': self.yu,
        }
        if self.sprvk:
            params.update({'sprvk': self.sprvk, 'yum': self.yum})

        payload = urllib.parse.urlencode({'text': query_text, 'options': 4})
        r = self.session.post(self.api_url, params=params, data=payload, headers=self.api_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join(data['text'])


class Argos(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translate.argosopentech.com'
        self.api_url = f'{self.host_url}/translate'
        self.language_url = f'{self.host_url}/languages'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_ajax_for_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=False, if_json_for_api=True)
        self.language_headers = self.get_headers(self.host_url, if_api=False, if_json_for_api=True)
        self.host_pool = ['https://translate.argosopentech.com', 'https://libretranslate.de',
                          'https://translate.astian.org', 'https://translate.mentality.rip',
                          'https://translate.api.skitzen.com', 'https://trans.zillyhuhn.com']
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)  # unknown
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        lang_list = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).json()
        lang_list = sorted([lang['code'] for lang in lang_list])
        return {}.fromkeys(lang_list, lang_list)

    @Tse.time_stat
    @Tse.check_query
    def argos_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.argosopentech.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param reset_host_url: str, default None.
        :return: str or dict
        """

        reset_host_url = kwargs.get('reset_host_url', None)
        if reset_host_url and reset_host_url != self.host_url:
            if reset_host_url not in self.host_pool:
                raise TranslatorError
            self.host_url = reset_host_url
            self.api_url = f'{self.host_url}/translate'
            self.language_url = f'{self.host_url}/languages'

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.language_url, self.session, self.language_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        payload = {'q': query_text, 'source': from_language, 'target': to_language, 'format': 'text'}
        r = self.session.post(self.api_url, headers=self.api_headers, json=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translatedText']


class Iciba(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://www.iciba.com/fy'
        self.api_url = 'https://ifanyi.iciba.com/index.php'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_ajax_for_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=True, if_json_for_api=False)
        self.language_headers = self.get_headers(self.host_url, if_api=False, if_json_for_api=True)
        self.language_map = None
        self.session = None
        self.s_y2 = 'ifanyiweb8hc9s98e'
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(3e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, api_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        params = {'c': 'trans', 'm': 'getLanguage', 'q': 0, 'type': 'en', 'str': ''}
        dd = ss.get(api_url, params=params, headers=headers, timeout=timeout, proxies=proxies).json()
        lang_list = sorted(list(set([lang for d in dd for lang in dd[d]])))
        return {}.fromkeys(lang_list, lang_list)

    @Tse.time_stat
    @Tse.check_query
    def iciba_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.iciba.com/fy
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.api_url, self.session, self.language_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        sign = hashlib.md5(f"6key_web_fanyi{self.s_y2}{query_text}".encode()).hexdigest()[:16]  # strip()
        params = {'c': 'trans', 'm': 'fy', 'client': 6, 'auth_user': 'key_web_fanyi', 'sign': sign}
        payload = {'from': from_language, 'to': to_language, 'q': query_text}
        r = self.session.post(self.api_url, headers=self.api_headers, params=params, data=payload, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['content'] if data.get('isSensitive') == 1 else data['content']['out']


class IflytekV1(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://saas.xfyun.cn/translate?tabKey=text'
        self.api_url = 'https://saas.xfyun.cn/ai-application/trans/its'
        self.language_old_url = 'https://saas.xfyun.cn/_next/static/4bzLSGCWUNl67Xal-AfIl/pages/translate.js'
        self.language_url_pattern = '/_next/static/(\w+([-]?\w+))/pages/translate.js'
        self.language_url = None
        self.cookies_url = 'https://sso.xfyun.cn//SSOService/login/getcookies'
        self.info_url = 'https://saas.xfyun.cn/ai-application/user/info'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'cn'
        self.input_limit = int(2e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        try:
            if not self.language_url:
                url_path = re.compile(self.language_url_pattern).search(host_html).group()
                self.language_url = f'{self.host_url[:21]}{url_path}'
            r = ss.get(self.language_url, headers=headers, timeout=timeout, proxies=proxies)
        except:
            r = ss.get(self.language_old_url, headers=headers, timeout=timeout, proxies=proxies)

        js_html = r.text
        lang_str = re.compile('languageList:\\(e={(.*?)}').search(js_html).group()[16:]
        lang_list = sorted(list(execjs.eval(lang_str).keys()))
        return {}.fromkeys(lang_list, lang_list)

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def iflytek_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://saas.xfyun.cn/translate?tabKey=text
        :param query_text: str, must.
        :param from_language: str, default 'zh', unsupported 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            _ = self.session.get(self.cookies_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            _ = self.session.get(self.info_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, self.session, self.host_headers, timeout, proxies,
                                                      **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('iflytek', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        # cipher_query_text = base64.b64encode(query_text.encode()).decode()
        cipher_query_text = query_text
        payload = {'from': from_language, 'to': to_language, 'text': cipher_query_text}
        r = self.session.post(self.api_url, headers=self.api_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else json.loads(data['data'])['trans_result']['dst']


class IflytekV2(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.xfyun.cn/console/trans/text'  # https://www.iflyrec.com/html/translate.html
        self.api_url = 'https://fanyi.xfyun.cn/api-tran/trans/its'
        self.detect_language_url = 'https://fanyi.xfyun.cn/api-tran/trans/detection'
        self.language_url_pattern = '/js/trans-text/index.(.*?).js'
        self.language_url = None
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'cn'
        self.input_limit = int(2e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        host_true_url = f'https://{urllib.parse.urlparse(self.host_url).hostname}'

        et = lxml.etree.HTML(host_html)
        host_js_url = f"""{host_true_url}{et.xpath('//script[@type="module"]/@src')[0]}"""
        host_js_html = ss.get(host_js_url, headers=headers, timeout=timeout, proxies=proxies).text
        self.language_url = f"""{host_true_url}{re.compile(self.language_url_pattern).search(host_js_html).group()}"""

        lang_js_html = ss.get(self.language_url, headers=headers, timeout=timeout, proxies=proxies).text
        lang_list = re.compile('languageCode:"(.*?)",').findall(lang_js_html)
        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def iflytek_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.xfyun.cn/console/trans/text
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, self.session, self.host_headers, timeout, proxies,
                                                      **debug_lang_kwargs)

        if from_language == 'auto':
            params = {'text': query_text}
            detect_r = self.session.get(self.detect_language_url, params=params, headers=self.host_headers,
                                        timeout=timeout, proxies=proxies)
            from_language = detect_r.json()[
                'data'] if detect_r.status_code == 200 and detect_r.text.strip() != '' else self.output_zh
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = {'from': from_language, 'to': to_language, 'text': query_text}
        r = self.session.post(self.api_url, headers=self.api_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else json.loads(data['data'])['trans_result']['dst']


class Iflyrec(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://fanyi.iflyrec.com'
        self.api_url = 'https://fanyi.iflyrec.com/TranslationService/v1/textAutoTranslation'
        self.detect_lang_url = 'https://fanyi.iflyrec.com/TranslationService/v1/languageDetection'
        self.language_url = 'https://fanyi.iflyrec.com/TranslationService/v1/textTranslation/languages'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.lang_index = {'zh': 1, 'en': 2, 'ja': 3, 'ko': 4, 'ru': 5, 'fr': 6, 'es': 7, 'vi': 8, 'yue': 9, 'ar': 12,
                           'de': 13, 'it': 14}
        self.lang_index_mirror = {v: k for k, v in self.lang_index.items()}
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(2e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_index: dict, **kwargs: LangMapKwargsType) -> dict:
        lang_list = sorted(list(lang_index.keys()))
        lang_map = {lang: ['zh'] for lang in lang_list if lang != 'zh'}
        return {**lang_map, **{'zh': lang_list}}

    @Tse.time_stat
    @Tse.check_query
    def iflyrec_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://fanyi.iflyrec.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.lang_index, **debug_lang_kwargs)

        if from_language == 'auto':
            params = {'t': self.get_timestamp()}
            form = {'originalText': query_text}
            detect_r = self.session.post(self.detect_lang_url, params=params, json=form, headers=self.api_headers,
                                         timeout=timeout, proxies=proxies)
            from_language_id = detect_r.json()['biz'][0]['detectionLanguage']
            from_language = self.lang_index_mirror[from_language_id]
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        api_params = {'t': self.get_timestamp()}
        api_form = {
            'from': self.lang_index[from_language],
            'to': self.lang_index[to_language],
            'openTerminology': 'false',
            'contents': [{'text': t.strip(), 'frontBlankLine': 0} for t in query_text.split('\n') if t.strip() != ''],
        }
        r = self.session.post(self.api_url, params=api_params, json=api_form, headers=self.api_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join([item['translateResult'] for item in data['biz']])


class Reverso(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://www.reverso.net/text-translation'
        self.api_url = 'https://api.reverso.net/translate/v1/translation'
        self.language_url = None
        self.language_pattern = 'https://cdn.reverso.net/trans/v(\\d).(\\d).(\\d)/main.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.decrypt_language_map = None
        self.query_count = 0
        self.output_zh = 'zh'  # 'chi', because there are self.language_tran
        self.input_limit = int(2e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_dict_str = re.compile('={eng:(.*?)}').search(lang_html).group()[1:]
        lang_dict = execjs.eval(lang_dict_str)
        lang_list = sorted(list(lang_dict.values()))
        return {}.fromkeys(lang_list, lang_list)

    def decrypt_lang_map(self, lang_html: str) -> dict:
        lang_dict_str = re.compile('={eng:(.*?)}').search(lang_html).group()[1:]
        lang_dict = execjs.eval(lang_dict_str)
        return {k: v for v, k in lang_dict.items()}

    @Tse.time_stat
    @Tse.check_query
    def reverso_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.reverso.net/text-translation
        :param query_text: str, must.
        :param from_language: str, default 'zh', unsupported 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.decrypt_language_map):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.language_url = re.compile(self.language_pattern).search(host_html).group()
            lang_html = self.session.get(self.language_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.decrypt_language_map = self.decrypt_lang_map(lang_html)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(lang_html, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('reverso', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        from_language, to_language = self.decrypt_language_map[from_language], self.decrypt_language_map[to_language]

        payload = {
            'format': 'text',
            'from': from_language,
            'to': to_language,
            'input': query_text,
            'options': {
                'contextResults': 'true',
                'languageDetection': 'true',
                'sentenceSplitter': 'true',
                'origin': 'translation.web',
            }
        }
        r = self.session.post(self.api_url, json=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else ''.join(data['translation'])


class Itranslate(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://itranslate.com/translate'
        self.api_url = 'https://web-api.itranslateapp.com/v3/texts/translate'
        self.manifest_url = 'https://itranslate-webapp-production.web.app/manifest.json'
        self.language_url = None
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.api_key = None
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(1e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_str = re.compile('\\[{dialect:"auto",(.*?)}]').search(lang_html).group()
        lang_origin_list = execjs.eval(lang_str)
        lang_list = sorted(list(set([dd['dialect'] for dd in lang_origin_list])))
        return {}.fromkeys(lang_list, lang_list)

    def get_apikey(self, lang_html: str) -> str:
        return re.compile('"API-KEY":"(.*?)"').findall(lang_html)[0]

    @Tse.time_stat
    @Tse.check_query
    def itranslate_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                       **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://itranslate.com/translate
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)

            if not self.language_url:
                manifest_data = self.session.get(self.manifest_url, headers=self.host_headers, timeout=timeout,
                                                 proxies=proxies).json()
                self.language_url = manifest_data.get('main.js')

            lang_html = self.session.get(self.language_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(lang_html, **debug_lang_kwargs)

            self.api_key = self.get_apikey(lang_html)
            self.api_headers.update({'API-KEY': self.api_key})

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh,
                                                         output_en_translator='itranslate', output_en='en-US')

        payload = {
            'source': {'dialect': from_language, 'text': query_text, 'with': ['synonyms']},
            'target': {'dialect': to_language},
        }
        r = self.session.post(self.api_url, headers=self.api_headers, json=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['target']['text']


class TranslateCom(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://www.translate.com/machine-translation'
        self.api_url = 'https://www.translate.com/translator/translate_mt'
        self.lang_detect_url = 'https://www.translate.com/translator/ajax_lang_auto_detect'
        self.language_url = 'https://www.translate.com/ajax/language/ht/all'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=False)
        self.session = None
        self.language_map = None
        self.language_description = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(1.5e4)  # fifteen thousand letters left today.
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_desc: dict, **kwargs: LangMapKwargsType) -> dict:
        return {item['code']: [it['code'] for it in item['availableTranslationLanguages']] for item in lang_desc}

    @Tse.time_stat
    @Tse.check_query
    def translateCom_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                         **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.translate.com/machine-translation
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            lang_r = self.session.get(self.language_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.language_description = lang_r.json()
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.language_description, **debug_lang_kwargs)

        if from_language == 'auto':
            detect_form = {'text_to_translate': query_text}
            r_detect = self.session.post(self.lang_detect_url, data=detect_form, headers=self.api_headers,
                                         timeout=timeout, proxies=proxies)
            from_language = r_detect.json()['language']

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = {
            'text_to_translate': query_text,
            'source_lang': from_language,
            'translated_lang': to_language,
            'use_cache_only': 'false',
        }
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translated_text']  # translation_source is microsoft, wtf!


class Utibet(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'http://mt.utibet.edu.cn/mt'  # must http
        self.api_url = self.host_url
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=False)
        self.language_map = {'ti': ['zh'], 'zh': ['ti']}
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)  # unknown
        self.default_from_language = self.output_zh

    def parse_result(self, host_html: str) -> str:
        et = lxml.etree.HTML(host_html)
        return et.xpath('//*[@name="tgt"]/text()')[0]

    @Tse.time_stat
    @Tse.check_query
    def utibet_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'ti',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        http://mt.utibet.edu.cn/mt
        :param query_text: str, must.
        :param from_language: str, default 'auto', equals to 'zh'.
        :param to_language: str, default 'ti'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('utibet', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        payload = {
            'src': query_text,
            'tgt': query_text if from_language == 'ti' else '',
            'lang': 'tc' if from_language == 'ti' else 'ct',
        }
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, headers=self.api_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data_html = r.text
        time.sleep(sleep_seconds)
        self.query_count += 1
        return {'data_html': data_html} if is_detail_result else self.parse_result(data_html)


class Papago(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://papago.naver.com'
        self.api_url = 'https://papago.naver.com/apis/n2mt/translate'  # nsmt
        self.web_api_url = 'https://papago.naver.net/website'
        self.lang_detect_url = 'https://papago.naver.com/apis/langs/dect'
        self.language_url = None
        self.language_url_pattern = '/home.(.*?).chunk.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=False)
        self.language_map = None
        self.session = None
        self.device_id = None
        self.auth_key = None  # 'v1.7.1_12f919c9b5'  #'v1.6.7_cc60b67557'
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_str = re.compile('={ALL:(.*?)}').search(lang_html).group()[1:]
        lang_str = lang_str.lower().replace('zh-cn', 'zh-CN').replace('zh-tw', 'zh-TW')
        lang_list = re.compile(',"(.*?)":|,(.*?):').findall(lang_str)
        lang_list = [j if j else k for j, k in lang_list]
        lang_list = sorted(list(filter(lambda x: x not in ('all', 'auto'), lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    def get_auth_key(self, lang_html: str) -> str:
        return re.compile('AUTH_KEY:"(.*?)"').findall(lang_html)[0]

    def get_authorization(self, url: str, auth_key: str, device_id: str, timestamp: int) -> str:
        auth = hmac.new(key=auth_key.encode(), msg=f'{device_id}\n{url}\n{timestamp}'.encode(),
                        digestmod='md5').digest()
        return f'PPG {device_id}:{base64.b64encode(auth).decode()}'

    @Tse.time_stat
    @Tse.check_query
    def papago_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://papago.naver.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.auth_key):
            self.device_id = str(uuid.uuid4())
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            url_path = re.compile(self.language_url_pattern).search(host_html).group()
            self.language_url = ''.join([self.host_url, url_path])
            lang_html = self.session.get(self.language_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(lang_html, **debug_lang_kwargs)
            self.auth_key = self.get_auth_key(lang_html)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        detect_time = self.get_timestamp()
        detect_auth = self.get_authorization(self.lang_detect_url, self.auth_key, self.device_id, detect_time)
        detect_add_headers = {'device-type': 'pc', 'timestamp': str(detect_time), 'authorization': detect_auth}
        detect_headers = {**self.api_headers, **detect_add_headers}

        if from_language == 'auto':
            detect_form = urllib.parse.urlencode({'query': query_text})
            r_detect = self.session.post(self.lang_detect_url, headers=detect_headers, data=detect_form,
                                         timeout=timeout, proxies=proxies)
            from_language = r_detect.json()['langCode']

        trans_time = self.get_timestamp()
        trans_auth = self.get_authorization(self.api_url, self.auth_key, self.device_id, trans_time)
        trans_update_headers = {'x-apigw-partnerid': 'papago', 'timestamp': str(trans_time),
                                'authorization': trans_auth}
        detect_headers.update(trans_update_headers)
        trans_headers = detect_headers

        payload = {
            'deviceId': self.device_id,
            'text': query_text, 'source': from_language, 'target': to_language, 'locale': 'en',
            'dict': 'true', 'dictDisplay': 30, 'honorific': 'false', 'instant': 'false', 'paging': 'false',
        }
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, headers=trans_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translatedText']


class Lingvanex(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://lingvanex.com/demo/'
        self.api_url = None
        self.language_url = None
        self.auth_url = 'https://lingvanex.com/lingvanex_demo_page/js/api-base.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=False)
        self.session = None
        self.language_map = None
        self.detail_language_map = None
        self.auth_info = None
        self.mode = None
        self.model_pool = ('B2B', 'B2C',)
        self.query_count = 0
        self.output_zh = 'zh-Hans_CN'
        self.input_limit = int(1e4)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        params = {'all': 'true', 'code': 'en_GB', 'platform': 'dp', '_': self.get_timestamp()}
        detail_lang_map = ss.get(lang_url, params=params, headers=headers, timeout=timeout, proxies=proxies).json()
        for _ in range(3):
            _ = ss.get(lang_url, params={'platform': 'dp'}, headers=headers, timeout=timeout, proxies=proxies)
        lang_list = sorted(set([item['full_code'] for item in detail_lang_map['result']]))
        return {}.fromkeys(lang_list, lang_list)

    def get_d_lang_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: float, proxies: dict) -> dict:
        params = {'all': 'true', 'code': 'en_GB', 'platform': 'dp', '_': self.get_timestamp()}
        return ss.get(lang_url, params=params, headers=headers, timeout=timeout, proxies=proxies).json()

    def get_auth(self, auth_url: str, ss: SessionType, headers: dict, timeout: float, proxies: dict) -> dict:
        js_html = ss.get(auth_url, headers=headers, timeout=timeout, proxies=proxies).text
        return {k: v for k, v in re.compile(',(.*?)="(.*?)"').findall(js_html)}

    @Tse.time_stat
    @Tse.check_query
    def lingvanex_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                      **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://lingvanex.com/demo/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param lingvanex_mode: str, default "B2C", choose from ("B2B", "B2C").
        :return: str or dict
        """

        mode = kwargs.get('lingvanex_mode', 'B2C')
        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (
                self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.auth_info and self.mode == mode):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.auth_info = self.get_auth(self.auth_url, self.session, self.host_headers, timeout, proxies)

            if mode not in self.model_pool:
                raise TranslatorError

            if mode != self.mode:
                self.mode = mode
                self.api_url = ''.join([self.auth_info[f'{mode}_BASE_URL'], self.auth_info['TRANSLATE_URL']])
                self.language_url = ''.join([self.auth_info[f'{mode}_BASE_URL'], self.auth_info['GET_LANGUAGES_URL']])
                self.host_headers.update({'authorization': self.auth_info[f'{mode}_AUTH_TOKEN']})
                self.api_headers.update({'authorization': self.auth_info[f'{mode}_AUTH_TOKEN']})
                self.api_headers.update({'referer': urllib.parse.urlparse(self.auth_info[f'{mode}_BASE_URL']).netloc})

            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.language_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)
            self.detail_language_map = self.get_d_lang_map(self.language_url, self.session, self.host_headers, timeout,
                                                           proxies)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('lingvanex', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh,
                                                         output_en_translator='lingvanex', output_en='en_GB')

        payload = {
            'from': from_language,
            'to': to_language,
            'text': query_text,
            'platform': 'dp',
            'is_return_text_split_ranges': 'true'
        }
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['result']['text']


class Mglip(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'http://fy.mglip.com/pc'  # must http
        self.api_url = 'http://fy.mglip.com/t2t'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=False)
        self.language_map = {}.fromkeys(['zh', 'mon', 'xle'], ['zh', 'mon', 'xle'])
        self.session = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e2)
        self.default_from_language = self.output_zh

    @Tse.time_stat
    @Tse.check_query
    def mglip_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'mon',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        http://fy.mglip.com/pc
        :param query_text: str, must.
        :param from_language: str, default 'auto', equals 'zh'.
        :param to_language: str, default 'mon'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('mglip', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        payload = {'userInput': query_text, 'from': from_language, 'to': to_language}
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, headers=self.api_headers, data=payload, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['datas'][0]['paragraph'] if data['datas'][0]['type'] == 'trans' else \
            data['datas'][0]['data']


class VolcEngine(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translate.volcengine.com'
        self.api_url = 'https://translate.volcengine.com/web/translate/v1'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.ms_token = ''
        self.x_bogus = 'DFS#todo'
        self.signature = '_02B#todo'
        self.query_count = 0
        self.output_auto = 'detect'
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_list = re.compile('"language_(.*?)":').findall(host_html)
        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    @property
    def professional_field_map(self) -> dict:
        data = {
            '': {'category': '', 'glossary_list': []},
            'clean': {'category': 'clean', 'glossary_list': []},
            'novel': {'category': 'novel', 'glossary_list': []},
            'finance': {'category': 'finance', 'glossary_list': []},
            'biomedical': {'category': 'biomedical', 'glossary_list': []},

            'ai': {'category': '', 'glossary_list': ['ailab/ai']},
            'menu': {'category': '', 'glossary_list': ['ailab/menu']},
            'techfirm': {'category': '', 'glossary_list': ['ailab/techfirm']},

            'ecommerce': {'category': 'ecommerce', 'glossary_list': ['ailab/ecommerce']},
            'technique': {'category': 'technique', 'glossary_list': ['ailab/technique']},
        }
        return data

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def volcEngine_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                       **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.volcengine.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default '', choose from ('', 'clean')
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', '')
        if use_domain not in self.professional_field_map:
            raise TranslatorError

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_auto=self.output_auto, output_zh=self.output_zh)
        params = {
            'msToken': self.ms_token,
            'X-Bogus': self.x_bogus,
            '_signature': self.signature,
        }
        payload = {
            'text': query_text,
            'source_language': from_language,
            'target_language': to_language,
            'home_language': 'zh',
            'enable_user_glossary': 'false',
        }
        payload.update(self.professional_field_map[use_domain])
        r = self.session.post(self.api_url, params=params, json=payload, headers=self.api_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translation']


class ModernMt(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://www.modernmt.com/translate'
        self.api_url = 'https://webapi.modernmt.com/translate'
        self.language_url = 'https://www.modernmt.com/scripts/app.bundle.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True,
                                            if_http_override_for_api=True)
        self.session = None
        self.language_map = None
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        lang_html = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).text
        d_lang_map = json.loads(re.compile('''('{(.*?)}')''').search(lang_html).group(0)[1:-1])
        lang_list = sorted(d_lang_map.keys())
        return {}.fromkeys(lang_list, lang_list)

    @Tse.time_stat
    @Tse.check_query
    def modernMt_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                     **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.modernmt.com/translate
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.language_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        timestamp = self.get_timestamp()
        payload = {
            'q': query_text,
            'source': '' if from_language == 'auto' else from_language,
            'target': to_language,
            'ts': timestamp,
            'verify': hashlib.md5(f'webkey_E3sTuMjpP8Jez49GcYpDVH7r#{timestamp}#{query_text}'.encode()).hexdigest(),
            'hints': '',
            'multiline': 'true',
        }
        r = self.session.post(self.api_url, json=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['data']['translation']


class MyMemory(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://mymemory.translated.net'
        self.api_web_url = 'https://mymemory.translated.net/api/ajaxfetch'
        self.api_api_url = 'https://api.mymemory.translated.net/get'
        self.get_matecat_language_url = 'https://www.matecat.com/api/v2/languages'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.session = None
        self.language_map = None
        self.myMemory_language_list = None
        self.mateCat_language_list = None
        self.query_count = 0
        self.output_zh = 'zh-CN'
        self.input_limit = int(5e2)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, myMemory_host_html: str, matecat_lang_url: str, ss: SessionType, headers: dict,
                         timeout: Optional[float], proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        et = lxml.etree.HTML(myMemory_host_html)
        lang_list = et.xpath('//*[@id="select_source_mm"]/option/@value')[2:]
        self.myMemory_language_list = sorted(list(set(lang_list)))

        lang_d_list = ss.get(matecat_lang_url, headers=headers, timeout=timeout, proxies=proxies).json()
        self.mateCat_language_list = sorted(list(set([item['code'] for item in lang_d_list])))

        lang_list = sorted(list(set(self.myMemory_language_list + self.mateCat_language_list)))
        return {}.fromkeys(lang_list, lang_list)

    @Tse.time_stat
    @Tse.check_query
    def myMemory_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                     **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://mymemory.translated.net
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param myMemory_mode: str, default "web", choose from ("web", "api").
        :return: str or dict
        """

        mode = kwargs.get('myMemory_mode', 'web')
        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, self.get_matecat_language_url, self.session,
                                                      self.host_headers, timeout, proxies, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('myMemory', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh,
                                                         output_en_translator='myMemory', output_en='en-GB')

        params = {
            'q': query_text,
            'langpair': f'{from_language}|{to_language}'
        }
        params = params if mode == 'api' else {**params, **{'mtonly': 1}}
        api_url = self.api_api_url if mode == 'api' else self.api_web_url

        r = self.session.get(api_url, params=params, headers=self.host_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['responseData']['translatedText']


class Mirai(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://miraitranslate.com'
        self.host_url = 'https://miraitranslate.com/trial/'
        self.api_url = 'https://trial.miraitranslate.com/trial/api/translate.php'
        self.lang_url = None
        self.lang_url_pattern = 'main-es2015.(.*?).js'
        self.detect_lang_url = 'https://trial.miraitranslate.com/trial/api/detect_lang.php'
        self.trace_url = 'https://trial.miraitranslate.com/trial/api/trace.php'
        self.host_headers = self.get_headers(self.home_url, if_api=False)
        self.api_json_headers = self.get_headers(self.home_url, if_api=True, if_json_for_api=True)
        self.api_text_headers = self.get_headers(self.home_url, if_api=True, if_ajax_for_api=False)
        self.session = None
        self.language_map = None
        self.tran_key = None
        self.trans_id = str(uuid.uuid4())
        self.user_id = str(uuid.uuid4())
        self.lang_zh_map = {'zh-CN': 'zh', 'zh-TW': 'zt'}
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(2e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        js_html = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).text
        lang_pairs = re.compile('"/trial/(\\w{2})/(\\w{2})"').findall(js_html)
        return {f_lang: [v for k, v in lang_pairs if k == f_lang] for f_lang, t_lang in lang_pairs}

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def mirai_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'ja',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://miraitranslate.com/en/trial/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'ja'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time and self.tran_key):
            self.begin_time = time.time()
            self.session = requests.Session()
            # _ = self.session.get(self.home_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.tran_key = re.compile('var tran = "(.*?)";').search(host_html).group(1)
            lang_url_part = re.compile(self.lang_url_pattern).search(host_html).group()
            self.lang_url = f'https://miraitranslate.com/trial/inmt/{lang_url_part}'
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.lang_url, self.session, self.api_json_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        if from_language == 'auto':
            r = self.session.post(self.detect_lang_url, headers=self.api_json_headers, json={'text': query_text},
                                  timeout=timeout, proxies=proxies)
            from_language = r.json()['language']
            from_language = self.lang_zh_map[from_language] if 'zh' in from_language else from_language
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)

        trace_data = {
            'operationType': 'SLA',
            'lang': from_language,
            'source': query_text,
            'userId': self.user_id,
            'transId': self.trans_id,
            'uniqueId': self.tran_key,
            'date': f'{datetime.datetime.utcnow().isoformat()[:-3]}Z',
        }
        _ = self.session.post(self.trace_url, json=trace_data, headers=self.api_text_headers, timeout=timeout,
                              proxies=proxies)

        payload = {
            'input': query_text,
            'source': from_language,
            'target': to_language,
            'tran': self.tran_key,
            'adaptPhrases': [],
            'filter_profile': 'nmt',
            'profile': 'inmt',
            'usePrefix': 'false',
            'zt': 'true' if 'zt' in (from_language, to_language) else 'false',
            'InmtTarget': '',
            'InmtTranslateType': 'gisting',
        }
        r = self.session.post(self.api_url, data=payload, headers=self.api_text_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['ouputs'][0]['output'][0]['translation']


class Apertium(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://www.apertium.org/'
        self.api_url = 'https://apertium.org/apy/translate'
        self.get_lang_url = 'https://www.apertium.org/index.js'
        self.detect_lang_url = 'https://apertium.org/apy/identifyLang'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.session = None
        self.language_map = None
        self.query_count = 0
        self.output_zh = None  # unsupported
        self.output_en = 'eng'
        self.input_limit = int(1e4)  # almost no limit.
        self.default_from_language = 'spa'

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        js_html = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).text
        lang_pairs = re.compile('{sourceLanguage:"(.*?)",targetLanguage:"(.*?)"}').findall(js_html)
        return {f_lang: [v for k, v in lang_pairs if k == f_lang] for f_lang, t_lang in lang_pairs}

    @Tse.time_stat
    @Tse.check_query
    def apertium_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                     **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.apertium.org/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.get_lang_url, self.session, self.host_headers, timeout,
                                                      proxies, **debug_lang_kwargs)

        if from_language == 'auto':
            payload = urllib.parse.urlencode({'q': query_text})
            langs = self.session.post(self.detect_lang_url, data=payload, headers=self.api_headers, timeout=timeout,
                                      proxies=proxies).json()
            from_language = sorted(langs, key=lambda k: langs[k], reverse=True)[0]
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_en_translator='apertium', output_en=self.output_en)

        payload = {
            'q': query_text,
            'langpair': f'{from_language}|{to_language}',
            'prefs': '',
            'markUnknown': 'no',
        }
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['responseData']['translatedText']


class Tilde(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translate.tilde.com/'
        self.api_url = 'https://letsmt.eu/ws/service.svc/json/TranslateEx'
        self.get_config_url = 'https://translate.tilde.com/assets/config.local.json'  # ?version=46852
        self.subscribe_url = 'https://translate.tilde.com/assets/subscriptions-config.local.json'
        self.plausible_url = 'https://plausible.io/api/event'
        self.auth_url = 'https://auth.tilde.com/auth/realms/Tilde/protocol/openid-connect/login-status-iframe.html/init'
        self.speech_url = 'https://va.tilde.com/dl/directline/aHR0cDovL3Byb2RrOHNib3R0aWxkZTQ=/tokens/speech'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.langpair_ids = None
        self.config_data = None
        self.sys_data = None
        self.query_count = 0
        self.output_zh = None  # unsupported
        self.output_en = 'eng'
        self.input_limit = int(5e3)  # unknown
        self.default_from_language = 'lv'  # 'fr'

    @Tse.debug_language_map
    def get_language_map(self, sys_data: dict, **kwargs: LangMapKwargsType) -> dict:
        lang_pairs = [[item['SourceLanguage']['Code'], item['TargetLanguage']['Code']] for item in sys_data['System'] if
                      'General' in item['Domain']]
        return {f_lang: [v for k, v in lang_pairs if k == f_lang] for f_lang, t_lang in lang_pairs}

    def get_langpair_ids(self, sys_data: dict) -> dict:
        return {f"{item['SourceLanguage']['Code']}-{item['TargetLanguage']['Code']}": item['ID'] for item in
                sys_data['System'] if 'General' in item['Domain']}

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def tilde_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translate.tilde.com/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.config_data = self.session.get(self.get_config_url, headers=self.host_headers, timeout=timeout,
                                                proxies=proxies).json()
            self.api_headers.update({'client-id': self.config_data['mt']['api']['clientId']})  # must lower keyword

            sys_url = self.config_data['mt']['api']['systemListUrl']
            params = {'appID': self.config_data['mt']['api']['appID'],
                      'uiLanguageID': self.config_data['mt']['api']['uiLanguageID']}
            self.sys_data = self.session.get(sys_url, params=params, headers=self.api_headers, timeout=timeout,
                                             proxies=proxies).json()  # test
            self.langpair_ids = self.get_langpair_ids(self.sys_data)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.sys_data, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('tilde', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map)

        payload = {
            'text': query_text,
            'appID': self.config_data['mt']['api']['appID'],
            'systemID': self.langpair_ids[f'{from_language}-{to_language}'],
            'options': 'widget=text,alignment,markSentences',
        }
        r = self.session.post(self.api_url, json=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translation']


class CloudYi(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://www.cloudtranslation.com'
        self.host_url = 'https://www.cloudtranslation.com/#/translate'
        self.api_url = 'https://www.cloudtranslation.com/official-website/v1/transOneSrcText'
        self.get_lang_url = 'https://online.cloudtranslation.com/api/v1.0/site/get_all_language_and_domain'
        self.detect_lang_url = 'https://online.cloudtranslation.com/api/v1.0/request_translate/langid'
        self.get_cookie_url = 'https://online.cloudtranslation.com/api/v1.0/site/sites_language_list'
        self.host_headers = self.get_headers(self.home_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.home_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.langpair_domain = None
        self.professional_field = None
        self.query_count = 0
        self.output_zh = 'zh-cn'
        self.output_en = 'en-us'
        self.output_auto = 'all'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, d_lang_map: dict, **kwargs: LangMapKwargsType) -> dict:
        return {k: [it['language_code'] for it in item] for k, item in d_lang_map['data']['src_to_tgt'].items()}

    def get_langpair_domain(self, d_lang_map: dict) -> dict:
        return {k: [it['domain_code'] for it in item] for k, item in
                d_lang_map['data']['language_pair_to_domain'].items()}

    def get_professional_field_list(self, d_lang_map: dict) -> set:
        return {it['domain_code'] for _, item in d_lang_map['data']['language_pair_to_domain'].items() for it in item}

    @Tse.time_stat
    @Tse.check_query
    def cloudYi_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.cloudtranslation.com/#/translate
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default 'general'.
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', 'general')
        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            _ = self.session.get(self.get_cookie_url, headers=self.api_headers, timeout=timeout, proxies=proxies)
            d_lang_map = self.session.get(self.get_lang_url, headers=self.api_headers, timeout=timeout,
                                          proxies=proxies).json()
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(d_lang_map, **debug_lang_kwargs)
            self.langpair_domain = self.get_langpair_domain(d_lang_map)
            self.professional_field = self.get_professional_field_list(d_lang_map)

        if from_language == 'auto':
            payload = {'text': query_text}
            r = self.session.post(self.detect_lang_url, json=payload, headers=self.api_headers, timeout=timeout,
                                  proxies=proxies)
            from_language = r.json()['data']['language']
        from_language, to_language = from_language.lower(), to_language.lower()  # must lower
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh,
                                                         output_en_translator='cloudYi', output_en=self.output_en)

        domains = self.langpair_domain.get(f'{from_language}_{to_language}')
        if not domains:
            raise TranslatorError
        if use_domain not in domains:
            use_domain = domains[0]

        payload = {
            'text': query_text,
            'domain': use_domain,
            'srcLangCode': from_language,
            'tgtLangCode': to_language,
        }
        r = self.session.post(self.api_url, json=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['data']['translation']


class SysTran(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://www.systran.net'
        self.host_url = 'https://www.systran.net/translate/'
        self.api_url = 'https://api-translate.systran.net/translation/text/translate'
        self.get_lang_url = 'https://api-translate.systran.net/translation/supportedLanguages'
        self.get_token_url = 'https://translate.systran.net/oidc/token'
        self.get_client_url = 'https://www.systran.net/wp-content/themes/systran/translator/js/translateBox.bundle.js'
        self.host_headers = self.get_headers(self.home_url, if_api=False, if_referer_for_host=True)
        self.api_ajax_headers = self.get_headers(self.home_url, if_api=True, if_ajax_for_api=True)
        self.api_json_headers = self.get_headers(self.home_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.professional_field = None
        self.langpair_domain = None
        self.client_data = None
        self.token_data = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(5e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, d_lang_map: dict, **kwargs: LangMapKwargsType) -> dict:
        return {ii['source']: [jj['target'] for jj in d_lang_map['languagePairs'] if jj['source'] == ii['source']] for
                ii in d_lang_map['languagePairs']}

    def get_professional_field_list(self, d_lang_map: dict) -> set:
        return {it['selectors']['domain'] for item in d_lang_map['languagePairs'] for it in item['profiles']}

    def get_langpair_domain(self, d_lang_map: dict) -> dict:
        data = {
            f'{item["source"]}__{item["target"]}__{it["selectors"]["domain"]}': {
                'domain': it["selectors"]["domain"],
                'owner': it['selectors']['owner'],
                'size': it['selectors']['size'],
            } for item in d_lang_map['languagePairs'] for it in item['profiles']
        }
        return data

    def get_client_data(self, client_url: str, ss: SessionType, headers: dict, timeout: float, proxies: dict) -> dict:
        js_html = ss.get(client_url, headers=headers, timeout=timeout, proxies=proxies).text
        search_groups = re.compile('"https://translate.systran.net/oidc",\\w="(.*?)",\\w="(.*?)";').search(
            js_html)  # \\w{1} == \\w
        client_data = {
            'grant_type': 'client_credentials',
            'client_id': search_groups.group(1),
            'client_secret': search_groups.group(2),
        }
        return client_data

    @Tse.time_stat
    @Tse.check_query
    def sysTran_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                    **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.systran.net/translate/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default None.
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', 'Generic')
        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.client_data = self.get_client_data(self.get_client_url, self.session, self.host_headers, timeout,
                                                    proxies)
            payload = urllib.parse.urlencode(self.client_data)
            self.token_data = self.session.post(self.get_token_url, data=payload, headers=self.api_ajax_headers,
                                                timeout=timeout, proxies=proxies).json()

            header_params = {
                'authorization': f'{self.token_data["token_type"]} {self.token_data["access_token"]}',
                'x-user-agent': 'File Translate Box Portable',
            }
            self.api_json_headers.update(header_params)

            d_lang_map = self.session.get(self.get_lang_url, headers=self.api_json_headers, timeout=timeout,
                                          proxies=proxies).json()
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(d_lang_map, **debug_lang_kwargs)
            self.professional_field = self.get_professional_field_list(d_lang_map)
            self.langpair_domain = self.get_langpair_domain(d_lang_map)

        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh)
        if from_language == 'auto':
            from_language = self.warning_auto_lang('sysTran', self.default_from_language, if_print_warning)

        payload = {
            'target': to_language,
            'source': from_language if from_language != 'auto' else None,
            'inputs': [paragraph for paragraph in query_text.split('\n') if paragraph.strip()],
            'format': 'text/plain',
            'autodetectionMode': 'single',
            'withInfo': 'true',
            'withAnnotations': 'true',
            'profileId': None,
            'domain': None,
            'owner': None,
            'size': None,
        }
        if use_domain and from_language != 'auto':
            domain_payload = self.langpair_domain.get(f'{from_language}__{to_language}__{use_domain}')
            if not domain_payload:
                raise TranslatorError
            else:
                payload.update(domain_payload)

        r = self.session.post(self.api_url, json=payload, headers=self.api_json_headers, timeout=timeout,
                              proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join(' '.join(it['alt_transes'][0]['target']['text'] for it in
                                                                item['output']['documents'][0]['trans_units'][0][
                                                                    'sentences']) for item in data['outputs'])


class TranslateMe(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://translateme.network/'
        self.api_url = 'https://translateme.network/wp-admin/admin-ajax.php'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=True)
        self.session = None
        self.language_map = None
        self.query_count = 0
        self.output_zh = 'Chinese'
        self.output_en = 'English'
        self.input_limit = int(1e2)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, host_html: str, **kwargs: LangMapKwargsType) -> dict:
        lang_list = re.compile('data-lang="(.*?)"').findall(host_html)
        if not lang_list:
            raise TranslatorError

        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    # @Tse.uncertified
    # @Tse.time_stat
    # @Tse.check_query
    def _translateMe_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                         **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translateme.network/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('translateMe', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh,
                                                         output_en_translator='translateMe', output_en=self.output_en)
        if self.output_en not in (from_language, to_language):
            raise TranslatorError('Must use English as an intermediate translation.')

        data_list = []
        paragraphs = [paragraph for paragraph in query_text.split('\n') if paragraph.strip()]
        for paragraph in paragraphs:
            payload = {
                'text': paragraph,
                'lang_from': from_language,
                'lang_to': to_language,
                'action': 'tm_my_action',
                'type': 'convert'
            }
            payload = urllib.parse.urlencode(payload)
            r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout,
                                  proxies=proxies)
            r.raise_for_status()
            data = r.json()
            data_list.append(data)
        time.sleep(sleep_seconds)
        self.query_count += 1
        return {'data': data_list} if is_detail_result else '\n'.join([item['to'] for item in data_list])

    @Tse.uncertified
    @Tse.time_stat
    @Tse.check_query
    def translateMe_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                        **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://translateme.network/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(host_html, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('translateMe', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         output_zh=self.output_zh,
                                                         output_en_translator='translateMe', output_en=self.output_en)

        if self.output_en in (from_language, to_language):
            return self._translateMe_api(query_text, from_language, to_language, **kwargs)

        tmp_kwargs = kwargs.copy()
        tmp_kwargs.update({'is_detail_result': False, 'if_show_time_stat': False})
        next_query_text = self._translateMe_api(query_text, from_language, self.output_en, **tmp_kwargs)
        return self._translateMe_api(next_query_text, self.output_en, to_language, **kwargs)


class Elia(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.host_url = 'https://elia.eus/translator'
        self.api_url = 'https://elia.eus/ajax/translate_string'
        self.detect_lang_url = 'https://elia.eus/ajax/language_detection'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=True)
        self.session = None
        self.language_map = None
        self.professional_field = None
        self.langpair_domain = None
        self.token = None
        self.query_count = 0
        self.output_zh = None  # unsupported
        self.input_limit = int(1e2)
        self.default_from_language = 'fr'

    @Tse.debug_language_map
    def get_language_map(self, dd: dict, **kwargs: LangMapKwargsType) -> dict:
        return {ii['source_language']['code']: [jj['target_language']['code'] for jj in dd['language_pairs'] if
                                                jj['source_language']['code'] == ii['source_language']['code']] for ii
                in dd['language_pairs']}

    def get_professional_field_list(self, dd: dict) -> set:
        return {it['translation_model']['code'] for it in dd['language_pairs']}

    def get_langpair_domain(self, dd: dict) -> dict:
        data = {
            f'{item["source_language"]["code"]}__{item["target_language"]["code"]}__{item["translation_model"]["code"]}': {
                'translation_engine': item["engine"]["pk"],
            } for item in dd['language_pairs']
        }
        return data

    @Tse.time_stat
    @Tse.check_query
    def elia_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                 **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://elia.eus/translator
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param professional_field: str, default 'general'. Choose from ('general', 'admin').
        :return: str or dict
        """

        use_domain = kwargs.get('professional_field', 'general')
        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            host_html = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout,
                                         proxies=proxies).text
            self.token = re.compile('"csrfmiddlewaretoken": "(.*?)"').search(host_html).group(1)
            d_lang_str = re.compile('var languagePairs = JSON.parse\\((.*?)\\);').search(host_html).group()
            d_lang_map = json.loads(d_lang_str[43:-4].replace('&quot;', '"'))
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(d_lang_map, **debug_lang_kwargs)
            self.professional_field = self.get_professional_field_list(d_lang_map)
            self.langpair_domain = self.get_langpair_domain(d_lang_map)

        if from_language == 'auto':
            payload = {
                'text': query_text,
                'csrfmiddlewaretoken': self.token,
            }
            payload = urllib.parse.urlencode(payload)
            r = self.session.post(self.detect_lang_url, data=payload, headers=self.api_headers, timeout=timeout,
                                  proxies=proxies)
            from_language = r.json()['lang_id']
        from_language, to_language = self.check_language(from_language, to_language, self.language_map)

        payload = {
            'input_text': query_text,
            'source_language': from_language,
            'target_language': to_language,
            'translation_model': use_domain,
            'translation_engine': 1,
            'csrfmiddlewaretoken': self.token,
        }

        domain_payload = self.langpair_domain.get(f'{from_language}__{to_language}__{use_domain}')
        if not domain_payload:
            raise TranslatorError
        else:
            payload.update(domain_payload)

        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translated_text'].replace('</div>', '\n').replace('<div>',
                                                                                                     '').replace(
            '<span>', '').replace('</span>', '')


class LanguageWire(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://jwt.languagewire.com'
        self.host_url = 'https://www.languagewire.com/en/technology/languagewire-translate'
        self.api_url = 'https://lwt.languagewire.com/f/api/v1/translations/text'
        self.lang_url = 'https://lwt.languagewire.com/f/api/v1/language-pairs?includeVariants=true'
        self.cookie_url = 'https://lwt.languagewire.com/f/api/v1/auth/cookie'
        self.lwt_js_url = 'https://lwt.languagewire.com/en/main.6f20295b104bc52a.js'
        self.host_headers = self.get_headers(self.home_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.home_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.language_map = None
        self.lwt_data = None
        self.query_count = 0
        self.output_zh = None  # unsupported
        self.input_limit = int(5e3)
        self.default_from_language = 'fr'
        self.default_en_to_language = 'en-US'

    @Tse.debug_language_map
    def get_language_map(self, lang_url: str, ss: SessionType, headers: dict, timeout: Optional[float],
                         proxies: Optional[dict], **kwargs: LangMapKwargsType) -> dict:
        d_lang_map = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).json()
        return {ii['sourceLanguage']['mmtCode']: [jj['targetLanguage']['mmtCode'] for jj in d_lang_map if
                                                  jj['sourceLanguage']['mmtCode'] == ii['sourceLanguage']['mmtCode']]
                for ii in d_lang_map}

    # def get_lwt_data(self, lwt_js_url: str, ss: SessionType, headers: dict, timeout: float, proxies: dict) -> dict:
    #     js_html = ss.get(lwt_js_url, headers=headers, timeout=timeout, proxies=proxies).text
    #     lwt_data = {
    #         'x-lwt-application-id': re.compile('"X-LWT-Application-ID":"(.*?)"').search(js_html).group(1),
    #         'x-lwt-build-id': re.compile('"X-LWT-Build-ID":"(.*?)"').search(js_html).group(1),
    #     }
    #     return lwt_data

    def get_lwt_data(self) -> dict:
        lwt_data = {
            'x-lwt-application-id': 'LWT_WEB',
            'x-lwt-build-id': '346775',
        }
        return lwt_data

    @Tse.time_stat
    @Tse.check_query
    def languageWire_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                         **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.languagewire.com/en/technology/languagewire-translate
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.lwt_data = self.get_lwt_data()
            self.api_headers.update(self.lwt_data)

            _ = self.session.post(self.cookie_url, headers=self.api_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.lang_url, self.session, self.api_headers, timeout, proxies,
                                                      **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('languageWire', self.default_from_language, if_print_warning)
        to_language = self.default_en_to_language if to_language == 'en' else to_language
        from_language, to_language = self.check_language(from_language, to_language, self.language_map,
                                                         if_check_lang_reverse=False)

        payload = {
            'sourceText': query_text,
            'sourceLanguage': from_language,
            'targetLanguage': to_language,
        }
        r = self.session.post(self.api_url, json=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translation']


class Judic(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://judic.io'
        self.host_url = 'https://judic.io/en/translate'
        self.api_url = 'https://judic.io/translate/text'
        self.host_headers = self.get_headers(self.home_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.home_url, if_api=True, if_json_for_api=True)
        self.session = None
        self.lang_list = ['en', 'de', 'fr', 'nl']
        self.language_map = None
        self.query_count = 0
        self.output_zh = None  # unsupported
        self.input_limit = int(1e3)
        self.default_from_language = 'nl'

    @Tse.debug_language_map
    def get_language_map(self, lang_list: List[str], **kwargs: LangMapKwargsType) -> dict:
        return {}.fromkeys(lang_list, lang_list)

    @Tse.time_stat
    @Tse.check_query
    def judic_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                  **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://judic.io/en/translate
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.lang_list, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('judic', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map)

        payload = {
            'sourceText': query_text,
            'inputLang': from_language,
            'outputLang': to_language
        }
        r = self.session.post(self.api_url, json=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['translation']


class Yeekit(Tse):
    def __init__(self):
        super().__init__()
        self.begin_time = time.time()
        self.home_url = 'https://www.yeekit.com'
        self.host_url = 'https://www.yeekit.com/site/translate'
        self.api_url = 'https://www.yeekit.com/site/dotranslate'
        self.lang_url = 'https://www.yeekit.com/js/translate.js'
        self.host_headers = self.get_headers(self.home_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.home_url, if_api=True, if_ajax_for_api=True)
        self.session = None
        self.lang_list = ['zh', 'en', 'ar', 'de', 'ru', 'fr', 'cz', 'pt', 'jp', 'es']
        self.language_map = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = int(1e3)
        self.default_from_language = self.output_zh

    @Tse.debug_language_map
    def get_language_map(self, lang_list: List[str], **kwargs: LangMapKwargsType) -> dict:
        return {}.fromkeys(lang_list, lang_list)

    @Tse.uncertified  # not code, but server.
    @Tse.time_stat
    @Tse.check_query
    def yeekit_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en',
                   **kwargs: ApiKwargsType) -> Union[str, dict]:
        """
        https://www.yeekit.com/site/translate
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_ignore_empty_query: bool, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', 0)
        if_print_warning = kwargs.get('if_print_warning', True)
        is_detail_result = kwargs.get('is_detail_result', False)
        update_session_after_freq = kwargs.get('update_session_after_freq', self.default_session_freq)
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
        self.check_input_limit(query_text, self.input_limit)

        not_update_cond_freq = 1 if self.query_count % update_session_after_freq != 0 else 0
        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and self.language_map and not_update_cond_freq and not_update_cond_time):
            self.begin_time = time.time()
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            debug_lang_kwargs = self.debug_lang_kwargs(from_language, to_language, self.default_from_language,
                                                       if_print_warning)
            self.language_map = self.get_language_map(self.lang_list, **debug_lang_kwargs)

        if from_language == 'auto':
            from_language = self.warning_auto_lang('yeekit', self.default_from_language, if_print_warning)
        from_language, to_language = self.check_language(from_language, to_language, self.language_map)

        payload = {
            'content[]': query_text,
            'sourceLang': f'n{from_language}',
            'targetLang': f'n{to_language}',
        }
        payload = urllib.parse.urlencode(payload)
        r = self.session.post(self.api_url, data=payload, headers=self.api_headers, timeout=timeout, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else '\n'.join(
            ' '.join(p) for p in json.loads(data[0])['translation'][0]['translated'][0]['translation list'])


class TranslatorsServer:
    def __init__(self):
        self.cpu_cnt = os.cpu_count()
        self.server_region = GuestSeverRegion().get_server_region
        self._alibaba = AlibabaV2()
        self.alibaba = self._alibaba.alibaba_api
        self._apertium = Apertium()
        self.apertium = self._apertium.apertium_api
        self._argos = Argos()
        self.argos = self._argos.argos_api
        self._baidu = BaiduV1()  # V2
        self.baidu = self._baidu.baidu_api
        self._bing = Bing(server_region=self.server_region)
        self.bing = self._bing.bing_api
        self._caiyun = Caiyun()
        self.caiyun = self._caiyun.caiyun_api
        self._cloudYi = CloudYi()
        self.cloudYi = self._cloudYi.cloudYi_api
        self._deepl = Deepl()
        self.deepl = self._deepl.deepl_api
        self._elia = Elia()
        self.elia = self._elia.elia_api
        self._google = GoogleV2(server_region=self.server_region)
        self.google = self._google.google_api
        self._iciba = Iciba()
        self.iciba = self._iciba.iciba_api
        self._iflytek = IflytekV2()
        self.iflytek = self._iflytek.iflytek_api
        self._iflyrec = Iflyrec()
        self.iflyrec = self._iflyrec.iflyrec_api
        self._itranslate = Itranslate()
        self.itranslate = self._itranslate.itranslate_api
        self._judic = Judic()
        self.judic = self._judic.judic_api
        self._languageWire = LanguageWire()
        self.languageWire = self._languageWire.languageWire_api
        self._lingvanex = Lingvanex()
        self.lingvanex = self._lingvanex.lingvanex_api
        self._mglip = Mglip()
        self.mglip = self._mglip.mglip_api
        self._mirai = Mirai()
        self.mirai = self._mirai.mirai_api
        self._modernMt = ModernMt()
        self.modernMt = self._modernMt.modernMt_api
        self._myMemory = MyMemory()
        self.myMemory = self._myMemory.myMemory_api
        self._papago = Papago()
        self.papago = self._papago.papago_api
        self._qqFanyi = QQFanyi()
        self.qqFanyi = self._qqFanyi.qqFanyi_api
        self._qqTranSmart = QQTranSmart()
        self.qqTranSmart = self._qqTranSmart.qqTranSmart_api
        self._reverso = Reverso()
        self.reverso = self._reverso.reverso_api
        self._sogou = Sogou()
        self.sogou = self._sogou.sogou_api
        self._sysTran = SysTran()
        self.sysTran = self._sysTran.sysTran_api
        self._tilde = Tilde()
        self.tilde = self._tilde.tilde_api
        self._translateCom = TranslateCom()
        self.translateCom = self._translateCom.translateCom_api
        self._translateMe = TranslateMe()
        self.translateMe = self._translateMe.translateMe_api
        self._utibet = Utibet()
        self.utibet = self._utibet.utibet_api
        self._volcEngine = VolcEngine()
        self.volcEngine = self._volcEngine.volcEngine_api
        self._yandex = Yandex()
        self.yandex = self._yandex.yandex_api
        self._yeekit = Yeekit()
        self.yeekit = self._yeekit.yeekit_api
        self._youdao = YoudaoV3()
        self.youdao = self._youdao.youdao_api
        self._translators_dict = {
            'alibaba': self._alibaba, 'apertium': self._apertium, 'argos': self._argos, 'baidu': self._baidu,
            'bing': self._bing,
            'caiyun': self._caiyun, 'cloudYi': self._cloudYi, 'deepl': self._deepl, 'elia': self._elia,
            'google': self._google,
            'iciba': self._iciba, 'iflytek': self._iflytek, 'iflyrec': self._iflyrec, 'itranslate': self._itranslate,
            'judic': self._judic,
            'languageWire': self._languageWire, 'lingvanex': self._lingvanex,
            'mglip': self._mglip, 'mirai': self._mirai,
            'modernMt': self._modernMt, 'myMemory': self._myMemory, 'papago': self._papago, 'qqFanyi': self._qqFanyi,
            'qqTranSmart': self._qqTranSmart,
            'reverso': self._reverso, 'sogou': self._sogou, 'sysTran': self._sysTran, 'tilde': self._tilde,
            'translateCom': self._translateCom,
            'translateMe': self._translateMe, 'utibet': self._utibet, 'volcEngine': self._volcEngine,
            'yandex': self._yandex, 'yeekit': self._yeekit,
            'youdao': self._youdao,
        }
        self.translators_dict = {
            'alibaba': self.alibaba, 'apertium': self.apertium, 'argos': self.argos, 'baidu': self.baidu,
            'bing': self.bing,
            'caiyun': self.caiyun, 'cloudYi': self.cloudYi, 'deepl': self.deepl, 'elia': self.elia,
            'google': self.google,
            'iciba': self.iciba, 'iflytek': self.iflytek, 'iflyrec': self.iflyrec, 'itranslate': self.itranslate,
            'judic': self.judic,
            'languageWire': self.languageWire, 'lingvanex': self.lingvanex,
            'mglip': self.mglip, 'mirai': self.mirai,
            'modernMt': self.modernMt, 'myMemory': self.myMemory, 'papago': self.papago, 'qqFanyi': self.qqFanyi,
            'qqTranSmart': self.qqTranSmart,
            'reverso': self.reverso, 'sogou': self.sogou, 'sysTran': self.sysTran, 'tilde': self.tilde,
            'translateCom': self.translateCom,
            'translateMe': self.translateMe, 'utibet': self.utibet, 'volcEngine': self.volcEngine,
            'yandex': self.yandex, 'yeekit': self.yeekit,
            'youdao': self.youdao,
        }
        self.translators_pool = list(self.translators_dict.keys())
        self.not_en_langs = {'utibet': 'ti', 'mglip': 'mon'}
        self.not_zh_langs = {'languageWire': 'fr', 'tilde': 'fr', 'elia': 'fr', 'apertium': 'spa'}
        self.pre_acceleration_label = 0
        self.example_query_text = '你好。\n欢迎你！'
        self.success_translators_pool = []
        self.failure_translators_pool = []

    def translate_text(self,
                       query_text: str,
                       translator: str = 'bing',
                       from_language: str = 'auto',
                       to_language: str = 'en',
                       if_use_preacceleration: bool = False,
                       **kwargs: ApiKwargsType,
                       ) -> Union[str, dict]:
        """
        :param query_text: str, must.
        :param translator: str, default 'bing'.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param if_use_preacceleration: bool, default False.
        :param **kwargs:
                :param is_detail_result: bool, default False.
                :param professional_field: str, support alibaba(), baidu(), caiyun(), cloudYi(), elia(), sysTran(), youdao(), volcEngine() only.
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_use_cn_host: bool, default False. Support google(), bing() only.
                :param reset_host_url: str, default None. Support google(), argos(), yandex() only.
                :param if_check_reset_host_url: bool, default True. Support google(), yandex() only.
                :param if_ignore_empty_query: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param lingvanex_model: str, default 'B2C', choose from ("B2C", "B2B").
                :param myMemory_mode: str, default "web", choose from ("web", "api").
        :return: str or dict
        """

        if translator not in self.translators_pool:
            raise TranslatorError

        if not self.pre_acceleration_label and if_use_preacceleration:
            _ = self.preaccelerate()

        return self.translators_dict[translator](query_text=query_text, from_language=from_language,
                                                 to_language=to_language, **kwargs)

    def translate_html(self,
                       html_text: str,
                       translator: str = 'bing',
                       from_language: str = 'auto',
                       to_language: str = 'en',
                       n_jobs: int = -1,
                       if_use_preacceleration: bool = False,
                       **kwargs: ApiKwargsType,
                       ) -> str:
        """
        Translate the displayed content of html without changing the html structure.
        :param html_text: str, must.
        :param translator: str, default 'bing'.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param n_jobs: int, default -1, means os.cpu_cnt().
        :param if_use_preacceleration: bool, default False.
        :param **kwargs:
                :param is_detail_result: bool, default False.
                :param professional_field: str, support alibaba(), baidu(), caiyun(), cloudYi(), elia(), sysTran(), youdao(), volcEngine() only.
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_use_cn_host: bool, default False. Support google(), bing() only.
                :param reset_host_url: str, default None. Support google(), argos(), yandex() only.
                :param if_check_reset_host_url: bool, default True. Support google(), yandex() only.
                :param if_ignore_empty_query: bool, default False.
                :param if_ignore_limit_of_length: bool, default False.
                :param limit_of_length: int, default 20000.
                :param if_show_time_stat: bool, default False.
                :param show_time_stat_precision: int, default 2.
                :param if_print_warning: bool, default True.
                :param lingvanex_model: str, default 'B2C', choose from ("B2C", "B2B").
                :param myMemory_mode: str, default "web", choose from ("web", "api").
        :return: str
        """

        if translator not in self.translators_pool or kwargs.get('is_detail_result', False) or n_jobs > self.cpu_cnt:
            raise TranslatorError

        if not self.pre_acceleration_label and if_use_preacceleration:
            _ = self.preaccelerate()

        def _translate_text(sentence: str) -> Tuple[str, str]:
            return sentence, self.translators_dict[translator](query_text=sentence, from_language=from_language,
                                                               to_language=to_language, **kwargs)

        pattern = re.compile(
            "(?:^|(?<=>))([\\s\\S]*?)(?:(?=<)|$)")  # TODO: <code></code> <div class="codetext notranslate">
        sentence_list = list(set(pattern.findall(html_text)))

        n_jobs = self.cpu_cnt if n_jobs <= 0 else n_jobs
        with pathos.multiprocessing.ProcessPool(n_jobs) as pool:
            result_list = pool.map(_translate_text, sentence_list)

        result_dict = {text: ts_text for text, ts_text in result_list}
        _get_result_func = lambda k: result_dict.get(k.group(1), '')
        return pattern.sub(repl=_get_result_func, string=html_text)

    def _test_translate(self, _ts: str, timeout: Optional[float] = None, if_show_time_stat: bool = False) -> str:
        from_language = self.not_zh_langs[_ts] if _ts in self.not_zh_langs else 'auto'
        to_language = self.not_en_langs[_ts] if _ts in self.not_en_langs else 'en'
        result = self.translators_dict[_ts](
            query_text=self.example_query_text,
            translator=_ts,
            from_language=from_language,
            to_language=to_language,
            if_print_warning=False,
            timeout=timeout,
            if_show_time_stat=if_show_time_stat
        )
        return result

    def get_languages(self, translator: str = 'bing'):
        language_map = self._translators_dict[translator].language_map
        if language_map:
            return language_map

        _ = self._test_translate(_ts=translator)
        return self._translators_dict[translator].language_map

    def preaccelerate(self, timeout: Optional[float] = None, if_show_time_stat: bool = True, **kwargs: str) -> dict:
        if self.pre_acceleration_label > 0:
            raise TranslatorError('Preacceleration can only be performed once.')

        self.example_query_text = kwargs.get('example_query_text', self.example_query_text)

        sys.stderr.write('Preacceleration-Process will take a few minutes.\n')
        sys.stderr.write('Tips: The smaller `timeout` value, the fewer translators pass the test '
                         'and the less time it takes to preaccelerate. However, the slow speed of '
                         'preacceleration does not mean the slow speed of later translation.\n\n')

        for i in tqdm.tqdm(range(len(self.translators_pool)), desc='Preacceleration Process', ncols=80):
            _ts = self.translators_pool[i]
            try:
                _ = self._test_translate(_ts, timeout, if_show_time_stat)
                self.success_translators_pool.append(_ts)
            except:
                self.failure_translators_pool.append(_ts)

            self.pre_acceleration_label += 1
        return {'success': self.success_translators_pool, 'failure': self.failure_translators_pool}

    def speedtest(self, **kwargs: List[str]) -> None:
        if self.pre_acceleration_label < 1:
            raise TranslatorError('Preacceleration first.')

        test_translators_pool = kwargs.get('test_translators_pool', self.success_translators_pool)

        sys.stderr.write('SpeedTest-Process will take a few seconds.\n\n')
        for i in tqdm.tqdm(range(len(test_translators_pool)), desc='SpeedTest Process', ncols=80):
            _ts = test_translators_pool[i]
            try:
                _ = self._test_translate(_ts, timeout=None, if_show_time_stat=True)
            except:
                pass
        return

    def preaccelerate_and_speedtest(self, timeout: Optional[float] = None, **kwargs: str) -> dict:
        result = self.preaccelerate(timeout=timeout, **kwargs)
        sys.stderr.write('\n\n')
        self.speedtest()
        return result


tss = TranslatorsServer()

_alibaba = tss._alibaba
alibaba = tss.alibaba
_apertium = tss._apertium
apertium = tss.apertium
_argos = tss._argos
argos = tss.argos
_baidu = tss._baidu
baidu = tss.baidu
_bing = tss._bing
bing = tss.bing
_caiyun = tss._caiyun
caiyun = tss.caiyun
_cloudYi = tss._cloudYi
cloudYi = tss.cloudYi
_deepl = tss._deepl
deepl = tss.deepl
_elia = tss._elia
elia = tss.elia
_google = tss._google
google = tss.google
_iciba = tss._iciba
iciba = tss.iciba
_iflytek = tss._iflytek
iflytek = tss.iflytek
_iflyrec = tss._iflyrec
iflyrec = tss.iflyrec
_itranslate = tss._itranslate
itranslate = tss.itranslate
_judic = tss._judic
judic = tss.judic
_languageWire = tss._languageWire
languageWire = tss.languageWire
_lingvanex = tss._lingvanex
lingvanex = tss.lingvanex
_mglip = tss._mglip
mglip = tss.mglip
_mirai = tss._mirai
mirai = tss.mirai
_modernMt = tss._modernMt
modernMt = tss.modernMt
_myMemory = tss._myMemory
myMemory = tss.myMemory
_papago = tss._papago
papago = tss.papago
_qqFanyi = tss._qqFanyi
qqFanyi = tss.qqFanyi
_qqTranSmart = tss._qqTranSmart
qqTranSmart = tss.qqTranSmart
_reverso = tss._reverso
reverso = tss.reverso
_sogou = tss._sogou
sogou = tss.sogou
_sysTran = tss._sysTran
sysTran = tss.sysTran
_tilde = tss._tilde
tilde = tss.tilde
_translateCom = tss._translateCom
translateCom = tss.translateCom
_translateMe = tss._translateMe
translateMe = tss.translateMe
_utibet = tss._utibet
utibet = tss.utibet
_volcEngine = tss._volcEngine
volcEngine = tss.volcEngine
_yandex = tss._yandex
yandex = tss.yandex
_yeekit = tss._yeekit
yeekit = tss.yeekit
_youdao = tss._youdao
youdao = tss.youdao

translate_text = tss.translate_text
translate_html = tss.translate_html
translators_pool = tss.translators_pool
get_languages = tss.get_languages

preaccelerate = tss.preaccelerate
speedtest = tss.speedtest
preaccelerate_and_speedtest = tss.preaccelerate_and_speedtest
# sys.stderr.write(f'Support translators {translators_pool} only.\n')
