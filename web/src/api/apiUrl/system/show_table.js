import {GET, PUT, reUrl} from '../../axiosconfig/axiosconfig'

export default {
    // 获取表格要显示的列
    show_table: function(token, params) {
        return GET(reUrl + '/show_table/' + token + '/', params)
    },
    update_table: function(token, params) {
        return PUT(reUrl + '/show_table/' + token + '/', params)
    }
}
