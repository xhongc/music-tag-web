import {GET, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    overview: function(params) {
        return GET(reUrl + '/home/overview/', params)
    },
    weekly_job: function(params) {
        return GET(reUrl + '/home/weekly_job/', params)
    },
    today_job: function(params) {
        return GET(reUrl + '/home/today_job/', params)
    },
    top5_agent: function(params) {
        return GET(reUrl + '/home/top5_agent/', params)
    },
    job_dynamic: function(params) {
        return GET(reUrl + '/home/job_dynamic/', params)
    }
}
