import { GET, reUrl } from '../../axiosconfig/axiosconfig'

export default {
    getJobFlowReport: function(params) {
        return GET(reUrl + '/process_run/data_analyze/', params)
    },
    getJobFlowName: function(params) {
        return GET(reUrl + '/process/process_name/', params)
    },
    getJobReport: function(params) {
        return GET(reUrl + '/node_run/data_analyze/', params)
    },
    getJobName: function(params) {
        return GET(reUrl + '/node/node_name/', params)
    }
}
