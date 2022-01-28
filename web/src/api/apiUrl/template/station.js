import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/station/', params)
    },
    create: function(params) {
        return POST(reUrl + '/station/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/station/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/station/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/station/' + JSON.stringify(id) + '/')
    },
    get_biz: function(params) {
        return GET(reUrl + '/station/get_biz/', params)
    },
    search_host: function(params) {
        return POST(reUrl + '/station/search_host/', params)
    },
    get_os_account: function(params) {
        return POST(reUrl + '/station/get_os_account/', params)
    }
}
