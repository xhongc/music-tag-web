import {GET, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    list: function(params) {
        return GET(reUrl + '/node_history/', params)
    },
    retrieve: function(id, params) {
        return GET(reUrl + '/node_history/' + JSON.stringify(id) + '/', params)
    }
}
