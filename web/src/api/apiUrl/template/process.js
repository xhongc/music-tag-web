import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/process/flow/', params)
    },
    create: function(params) {
        return POST(reUrl + '/process/flow/', params)
    },
    retrieve: function(id) {
        return GET(reUrl + '/process/flow/' + JSON.stringify(id) + '/')
    },
    update: function(id, params) {
        return PUT(reUrl + '/process/flow/' + JSON.stringify(id) + '/', params)
    },
    clone: function(params) {
        return POST(reUrl + '/process/clone/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/process/flow/' + JSON.stringify(id) + '/')
    },
    execute: function(params) {
        return POST(reUrl + '/process/flow/execute/', params)
    },
    get_process_node: function(params) {
        return GET(reUrl + '/process/get_process_node/', params)
    },
    get_topology: function(params) {
        return GET(reUrl + '/process/get_topology/', params)
    },
    set_topology: function(params) {
        // PARAMS： {'is_global': bool, 'nodes': array}
        return POST(reUrl + '/process/set_topology/', params)
    },
    upload_process: function(params, config) {
        return POST(reUrl + '/process/upload_process/', params, config)
    },
    serialize_process: function(params, config) {
        return POST(reUrl + '/process/serialize_process/', params, config)
    },
    save_process: function(params, config) {
        return POST(reUrl + '/process/save_process/', params, config)
    }
}
