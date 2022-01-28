import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    list: function(params) {
        return GET(reUrl + '/category/', params)
    },
    create: function(params) {
        return POST(reUrl + '/category/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/category/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/category/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/category/' + JSON.stringify(id) + '/')
    },
    get_topology: function(params) {
        return GET(reUrl + '/category/get_topology/', params)
    },
    set_topology: function(params) {
        // PARAMS： {'nodes': array}
        return POST(reUrl + '/category/set_topology/', params)
    }
}
