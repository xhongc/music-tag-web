import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/var_table/', params)
    },
    create: function(params) {
        return POST(reUrl + '/var_table/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/var_table/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/var_table/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/var_table/' + JSON.stringify(id) + '/')
    }
}
