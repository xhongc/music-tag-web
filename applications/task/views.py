from django.http import JsonResponse
from rest_framework import mixins, status
from rest_framework.response import Response

from applications.task.models import Task
from component.drf.viewsets import GenericViewSet
from django.core.cache import caches
from rest_framework.decorators import action


class TaskViewSets(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        # cache = caches["default"]
        # result = cache.get("task_2")
        # if result:
        #     return Response({"name": result})
        # else:
        #     task = Task.objects.filter(id=2).first()
        #     cache.set("task_2", task.name)
        #     return Response({"name": task.name})

        # task = Task.objects.filter(id=2).first()
        # return Response({"name": task.name})

        return Response({"name": "："})

    @action(methods=['GET'], detail=False)
    def get_public_qr_code(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "SUCCESS",
            "data": {
                "token": "XXX_0021ac1f-9566-4bde-8534-fdfed6b71e17",
                "url": "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=gQGR7zwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyd185dEV0R0FmUkUxb3ZRRU56Y2MAAgSfYmdjAwSAUQEA"
            }
        }
        )

    @action(methods=['POST'], detail=False)
    def login(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "login success",
            "data": {
                "uid": "636604c",
                "nickname": "oWAZO5r7",
                "sid": "0a45ab0"
            }
        }
        )

    @action(methods=['GET'], detail=False, url_path="user/myinfo")
    def user_info(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "susccess",
            "data": {
                "uid": "635d57ec4e8c",
                "nickname": "XXX",
                "email": "test@XXX.com",
                "headimgurl": "/avt.jpg",
                "coins": 99998.0,
                "time_create": "2022-10-29"
            }
        }
        )

    @action(methods=['GET'], detail=False)
    def products(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "success",
            "data": {
                "pagination": {
                    "total": 1,
                    "previous": "",
                    "current": 1,
                    "next": "",
                    "pages": 1,
                    "per_page": 20
                },
                "items": [
                    {
                        "title": "降重字数（6千字）",
                        "desc": "100%保证过查重保证语句内容通顺计费为5元/千字",
                        "price": "29.8",
                        "type": "coin",
                        "name": "coin",
                        "product_id": "5c494d980"
                    },
                    {
                        "title": "降重字数（6千字）",
                        "desc": "100%保证过查重保证语句内容通顺计费为5元/千字",
                        "price": "29.8",
                        "type": "coin",
                        "name": "coin",
                        "product_id": "5c494d980"
                    },
                    {
                        "title": "降重字数（6千字）",
                        "desc": "100%保证过查重保证语句内容通顺计费为5元/千字",
                        "price": "29.8",
                        "type": "coin",
                        "name": "coin",
                        "product_id": "5c494d980",
                        "commend": True,
                        "level": 1
                    }
                ]
            }
        }
        )

    @action(methods=['GET'], detail=False)
    def orders(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "success",
            "data": {
                "pagination": {
                    "total": 13,
                    "previous": "",
                    "current": 1,
                    "next": 2,
                    "pages": 3,
                    "per_page": 5
                },
                "items": [
                    {
                        "order_no": 1668066927232838,
                        "account_id": "635d57ec4e8cc9b",
                        "title": "1积分",
                        "detail": "购买XXX-1积分 * 1个, 共计: 0.01元",
                        "product_id": "5c494d9801cb",
                        "product_price": 1,
                        "product_num": 1,
                        "pay_type": "wxpay",
                        "trade_type": "NATIVE",
                        "time_create": "2022-11-10 15:55:27",
                        "status": "Created",
                        "pay_url": "weixin://wxpay/bizpayurl?pr=X1F9vvBzz"
                    },
                    {
                        "order_no": 1667718391139384,
                        "account_id": "635d57ec4e8c",
                        "title": "1积分",
                        "detail": "通过充值卡[6367b98e0224b1ec526856d0]购买XXX-1积分 * 1个",
                        "product_id": "5c494d9801c",
                        "product_price": 1,
                        "product_num": 1,
                        "pay_type": "card",
                        "trade_type": "card",
                        "time_create": "2022-11-06 15:06:31",
                        "status": "Paid",
                        "pay_url": ""
                    }
                ]
            }
        }

        )

    @action(methods=['POST'], detail=False)
    def web_rewrite(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "请求成功",
            "coin": 99997,
            "last_coin": 99998,
            "result": [
                {
                    "text": "你",
                    "similarity": 0.5,
                    "length": 1,
                    "name": "超级降重"
                },
                {
                    "text": "你",
                    "similarity": 0.5,
                    "length": 1,
                    "name": "智能降重"
                }
            ]
        }
        )

    @action(methods=['GET'], detail=False)
    def record(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 0,
            "msg": "success",
            "data": {
                "pagination": {
                    "total": 3,
                    "previous": "",
                    "current": 1,
                    "next": "",
                    "pages": 1,
                    "per_page": 20
                },
                "items": [
                    {
                        "account_id": "635d57ec4e",
                        "title": "web_rewrite",
                        "record_id": "20221110162253161443",
                        "time_update": "2022-11-10 16:22:53",
                        "coin": 1,
                        "last_coin": 99997.0,
                        "user_coin": 99996.0,
                        "text": "你超级降重超级降重超级降重超级降重超级降重",
                        "length": 1,
                        "result": [
                            {
                                "text": "你超级降重超级降重超级降重超级降重超级降重超级降重超级降重",
                                "similarity": 0.5,
                                "length": 1,
                                "name": "超级降重"
                            },
                            {
                                "text": "你超级123",
                                "similarity": 0.5,
                                "length": 1,
                                "name": "智能降重"
                            }
                        ]
                    },
                    {
                        "account_id": "635d57ec4e",
                        "title": "web_rewrite",
                        "record_id": "20221110162225907942",
                        "time_update": "2022-11-10 16:22:25",
                        "coin": 1,
                        "last_coin": 99998.0,
                        "user_coin": 99997.0,
                        "text": "你",
                        "length": 1,
                        "result": [
                            {
                                "text": "你",
                                "similarity": 0.5,
                                "length": 1,
                                "name": "超级降重"
                            },
                            {
                                "text": "你",
                                "similarity": 0.5,
                                "length": 1,
                                "name": "智能降重"
                            }
                        ]
                    }
                ]
            }
        }
        )
