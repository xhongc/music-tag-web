import {GET, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 系统审计日志
    list: function(params) {
        return GET(reUrl + '/audit_log/', params)
    },
    retrieve: function(id) {
        return GET(reUrl + '/audit_log/' + JSON.stringify(id) + '/')
    }
}
