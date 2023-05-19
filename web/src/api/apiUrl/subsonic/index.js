import {POST, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    login: function(params) {
        return POST(reUrl + '/api/token/', params)
    }
}
