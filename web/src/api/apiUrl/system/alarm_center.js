import {GET, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    list: function(params) {
        return GET(reUrl + '/alarm_center/', params)
    }
}
