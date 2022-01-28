import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/process_run/', params)
    },
    create: function(params) {
        return POST(reUrl + '/process_run/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/process_run/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/process_run/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/process_run/' + JSON.stringify(id) + '/')
    },
    control: function(params) {
        return POST(reUrl + '/process_run/control/', params)
    },
    process_snapshot: function(params) {
        return GET(reUrl + '/process_snapshot/', params)
    },
    process_snapshot_id: function(id, params) {
        return GET(reUrl + '/process_snapshot/' + JSON.stringify(id) + '/', params)
    }
}
