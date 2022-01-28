import Vue from 'vue'
import Vuex from 'vuex'
import monitor from './module/monitor.js'
import history from './module/history.js'
import permission from './module/permission.js'
import common from './module/common.js'
import getters from './getters.js'

Vue.use(Vuex)

const store = new Vuex.Store({
    modules: {
        monitor, // 作业监视
        history, // 作业历史
        permission, // 操作权限
        common // 公共属性
    },
    getters
})

export default store
