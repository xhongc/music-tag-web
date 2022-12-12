import {GET, POST, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    list: function(params) {
        return GET(reUrl + '/task/task/', params)
    },
    weixinLogin: function(params) {
        return GET(reUrl + '/get_public_qr_code/', params)
    },
    login: function(params) {
        return POST(reUrl + '/login/', params)
    },
    logout: function(params) {
        return POST(reUrl + '/logout/', params)
    },
    userInfo: function(params) {
        return GET(reUrl + '/user/myinfo/', params)
    },
    userUpdate: function(params) {
        return POST(reUrl + '/user/update/', params)
    },
    products: function(params) {
        return GET(reUrl + '/products/', params)
    },
    createOrder: function(params) {
        return POST(reUrl + '/orders/', params)
    },
    orderStatus: function(orderNo, params) {
        return GET(reUrl + `/orders/${orderNo}/status/`, params)
    },
    getOrders: function(params) {
        return GET(reUrl + '/orders/', params)
    },
    deleteOrders: function(orderNo, params) {
        return DELETE(reUrl + `/orders/${orderNo}/`, params)
    },
    cardPay: function(params) {
        return POST(reUrl + '/account/card/', params)
    },
    webRewrite: function(params) {
        return POST(reUrl + '/api/web_rewrite/', params)
    },
    rewriteRecord: function(params) {
        return GET(reUrl + '/record/', params)
    }
}
