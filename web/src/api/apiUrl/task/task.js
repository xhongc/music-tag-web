import {GET, POST, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    login: function(params) {
        return POST(reUrl + '/api/token/', params)
    },
    loginInfo: function(params) {
        return GET(reUrl + '/user/info/', params)
    },
    logout: function(params) {
        return POST(reUrl + '/logout/', params)
    }
}
