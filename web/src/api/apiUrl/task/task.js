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
    },
    fileList: function(params) {
        return POST(reUrl + '/api/file_list/', params)
    },
    musicId3: function(params) {
        return POST(reUrl + '/api/music_id3/', params)
    },
    updateId3: function(params) {
        return POST(reUrl + '/api/update_id3/', params)
    },
    batchUpdateId3: function(params) {
        return POST(reUrl + '/api/batch_update_id3/', params)
    },
    fetchId3Title: function(params) {
        return POST(reUrl + '/api/fetch_id3_by_title/', params)
    },
    fetchLyric: function(params) {
        return POST(reUrl + '/api/fetch_lyric/', params)
    }
}
