import {GET, POST, PUT, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 系统设置
    list: function(params) {
        return GET(reUrl + '/setting/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/setting/' + JSON.stringify(id) + '/', params)
    },
    get_logo: function(params) {
        return GET(reUrl + '/setting/get_logo/', params)
    },
    reset_logo: function(params) {
        return GET(reUrl + '/setting/reset_logo/', params)
    },
    update_logo: function(params) {
        return POST(reUrl + '/setting/update_logo/', params)
    },
    batch_update: function(params) {
        return POST(reUrl + '/setting/batch_update/', params)
    }
}
