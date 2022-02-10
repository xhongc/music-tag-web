import {GET, POST, PUT, DELETE, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/node/template/', params)
    },
    create: function(params) {
        return POST(reUrl + '/node/template/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/node/template/' + JSON.stringify(id) + '/', params)
    },
    update: function(id, params) {
        return PUT(reUrl + '/node/template/' + JSON.stringify(id) + '/', params)
    },
    clone: function(params) {
        return POST(reUrl + '/node/template/clone/', params)
    },
    delete: function(id) {
        return DELETE(reUrl + '/node/template/' + JSON.stringify(id) + '/')
    },
    execute: function(params) {
        return POST(reUrl + '/content/execute/', params)
    },
    upload_job: function(params) {
        return POST(reUrl + '/content/upload_contents/', params)
    },
    check_job: function(params) {
        return POST(reUrl + '/content/check_job/', params)
    },
    save_job_data: function(params) {
        return POST(reUrl + '/content/save_job_data/', params)
    }
}
