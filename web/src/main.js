// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
// import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
// 全量引入 bk-magic-vue
import bkMagic from 'bk-magic-vue'
// 全量引入 bk-magic-vue 样式
import 'bk-magic-vue/dist/bk-magic-vue.min.css'
import store from './vuex'
import axios from 'axios'
// 引用API文件
import api from './api/index'
// filter统一引入
import './fiter/index.js'
import cwMessage from './common/message'
// vuex
import '@/vuex/index' // 全局
import {hasPermission} from './promission.js' // 路由后台获取
// 引入jquery
// import $ from 'jquery'
// 引入字体图标库
import 'font-awesome/css/font-awesome.min.css'
// 引入lodash
// import lodash from 'lodash'
// 引入自定义icon 图标
import './assets/custom_icon/iconfont.css'
// import '../static/cw-icon/iconfont.css'
// import 'echarts/dist/extension/dataTool'
import VeeValidate, {Validator} from 'vee-validate'

const config = {
    errorBagName: 'veeErrors',
    fieldsBagName: 'veeFields'
}
Vue.use(VeeValidate, config)
Vue.use(bkMagic)
Vue.use(axios)
Vue.prototype.$cwMessage = cwMessage
// 将API方法绑定到全局
Vue.prototype.$http = axios
Vue.prototype.$api = api
const headTheme = 'light' // 选择 light 或 blue
Vue.prototype.headTheme = headTheme
// Vue.prototype.$lodash = lodash
Vue.prototype.hasPerm = hasPermission
Vue.config.productionTip = false
// Vue.prototype.cloneDeep = function(data) {
//     return lodash.cloneDeep(data)
// }
Vue.prototype.setCookie = function(name, value, day) {
    if (day !== 0) {
        const curDate = new Date()
        const curTamp = curDate.getTime()
        const curWeeHours = new Date(curDate.toLocaleDateString()).getTime() - 1
        const passedTamp = curTamp - curWeeHours
        const leftTamp = 24 * 60 * 60 * 1000 - passedTamp
        const leftTime = new Date()
        leftTime.setTime(leftTamp + curTamp)
        document.cookie = name + '=' + escape(value) + ';expires=' + leftTime.toGMTString()
    } else {
        document.cookie = name + '=' + escape(value)
    }
}
Vue.prototype.getCookie = function(name) {
    const reg = new RegExp('(^| )' + name + '=([^;]*)(;|$)')
    const arr = document.cookie.match(reg)
    if (arr) {
        return unescape(arr[2])
    } else {
        return null
    }
}
Validator.extend('integer', {
    getMessage: (field, args) => args + '间隔时间必须是正整数',
    validate: value => Number(value) >= 1 && Number(value) % 1 === 0
})
/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    store,
    components: {App},
    data() {
        return {
            website: '我是全局变量'
        }
    },
    template: '<App/>'
})
