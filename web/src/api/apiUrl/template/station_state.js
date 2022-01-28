import {GET, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 作业台
    list: function(params) {
        return GET(reUrl + '/station_state/', params)
    }
}
