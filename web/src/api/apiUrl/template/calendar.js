import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/calendar/', params)
    },
    create: function(params) {
        return POST(reUrl + '/calendar/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/calendar/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/calendar/' + JSON.stringify(id) + '/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/calendar/' + JSON.stringify(id) + '/')
    },
    post_calendar_file: function(params, config) {
        return POST(reUrl + '/calendar/post_calendar_file/', params)
    }
}
