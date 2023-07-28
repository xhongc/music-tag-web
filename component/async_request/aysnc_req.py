# import asyncio
#
# import aiohttp
# from django.conf import settings
#
# concurrence_limit = 5
#
#
# def callback(future):  # 这里默认传入一个future对象
#     pass
#
#
# class AsyncRequest:
#     """
#     协程请求
#     """
#
#     # 限制同时打开的连接的数量 limit=0为不限制
#     limit = concurrence_limit
#     timeout = 60
#     raise_for_status = False
#
#     session = None
#     result = {}
#
#     @classmethod
#     def run(cls, main=None):
#         loop = asyncio.new_event_loop()
#         try:
#             asyncio.set_event_loop(loop)
#             asyncio.get_event_loop().run_until_complete(main)
#         finally:
#             try:
#                 if hasattr(loop, "shutdown_asyncgens"):
#                     loop.run_until_complete(loop.shutdown_asyncgens())
#             finally:
#                 asyncio.set_event_loop(None)
#                 loop.close()
#
#     @classmethod
#     async def async_request(cls, method, url_data_map, headers=None):
#         """
#         method : get,post
#         """
#         headers = headers or {}
#         conn = aiohttp.TCPConnector(limit=cls.limit, verify_ssl=False)
#         async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
#             cls.session = session
#             result_list = await cls.fetch_multi(url_data_map, method=method)
#             return result_list
#
#     @classmethod
#     def _request(cls, method, url=None, data_list=None, url_data_map=None, headers=None):
#         assert url or url_data_map
#         is_simple = False
#         if not url_data_map:
#             data_list = data_list or []
#             url_data_map = {url: data_list}
#             is_simple = True
#         main = cls.async_request(method, url_data_map, headers=headers)
#         cls.run(main)
#         if is_simple:
#             return cls.result.get(url, [])
#         else:
#             return cls.result
#
#     @classmethod
#     def get(cls, url=None, data_list=None, url_data_map=None, headers=None):
#         """
#         get请求
#         example: AsyncRequest.get('url', [{'params': i} for i in range(30)])
#                  AsyncRequest.get(url_data_map={'url':[{'params': i} for i in range(30)]})
#
#         :param url: 请求地址, 与url_data_map只需传一种
#         :param data_list: 参数列表 [{},{}]
#         :param url_data_map: url和data_list的映射表
#         :return: 结果集
#         """
#         return cls._request("get", url, data_list, url_data_map, headers)
#
#     @classmethod
#     def post(cls, url=None, data_list=None, url_data_map=None, headers=None):
#         return cls._request("post", url, data_list, url_data_map, headers)
#
#     @classmethod
#     async def fetch(cls, url, data, method, index):
#         post_data = [{"params": data}, {"data": data}][method == "post"]
#         try:
#             async with getattr(cls.session, method)(
#                     url, **post_data, timeout=cls.timeout, raise_for_status=cls.raise_for_status
#             ) as resp:
#                 ret_data = await resp.json()
#                 cls.result[url][index] = ret_data
#                 return ret_data
#         except Exception as e:
#             print("asd", e)
#
#     @classmethod
#     async def fetch_multi(cls, url_data_map, method):
#         tasks = []
#         for url, data_list in url_data_map.items():
#             cls.result[url] = [None] * len(data_list)
#             for index, data in enumerate(data_list):
#                 task = asyncio.ensure_future(cls.fetch(url, data, method, index))
#                 task.add_done_callback(callback)
#                 tasks.append(task)
#
#         # gather: 搜集所有future对象，并等待返回
#         results = await asyncio.wait(tasks)
#         return results
