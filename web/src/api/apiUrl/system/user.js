import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 系统用户
    login: function(params) {
        return GET(reUrl + '/user/login/', params)
    },
    list: function(params) {
        return GET(reUrl + '/user/', params)
    },
    create: function(params) {
        return POST(reUrl + '/user/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/user/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/user/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/user/' + JSON.stringify(id) + '/')
    },
    init_privilege: function(params) {
        return GET(reUrl + '/user/init_privilege/', params)
    },
    get_uncreated_users: function(params) {
        return GET(reUrl + '/user/get_uncreated_users/', params)
    }
}
