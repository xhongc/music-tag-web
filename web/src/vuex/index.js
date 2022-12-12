import Vue from 'vue'
import Vuex from 'vuex'
import common from './module/common.js'
import getters from './getters.js'

Vue.use(Vuex)

const store = new Vuex.Store({
    modules: {
        common // 公共属性
    },
    getters
})

export default store
