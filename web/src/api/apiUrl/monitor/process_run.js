import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/process/run/', params)
    },
    create: function(params) {
        return POST(reUrl + '/process/run/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/process/run/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/process/run/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/process/run/' + JSON.stringify(id) + '/')
    },
    control: function(params) {
        return POST(reUrl + '/process/run/control/', params)
    },
    process_snapshot: function(params) {
        return GET(reUrl + '/process_snapshot/', params)
    },
    process_snapshot_id: function(id, params) {
        return GET(reUrl + '/process_snapshot/' + JSON.stringify(id) + '/', params)
    }
}
