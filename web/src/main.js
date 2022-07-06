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
import 'view-design/dist/styles/iview.css'
// 按需引入iview
import './components/iview/index'
// 几何图
import * as Echarts from 'echarts'
// 引用API文件
import api from './api/index'
// 时间格式化插件
import moment from 'moment'
// filter统一引入
import './fiter/index.js'
// 统一样式引入
import './assets/index'
import cwMessage from './common/message'
// 引入自定义组件
import Component from './components/index.js'
// vuex
import '@/vuex/index' // 全局
// import './promission.js' // 路由后台获取
import {hasPermission} from './promission.js' // 路由后台获取
// 引入jquery
// import $ from 'jquery'
// 引入字体图标库
import 'font-awesome/css/font-awesome.min.css'
// 引入lodash
import lodash from 'lodash'
// 引入自定义icon 图标
import './assets/custom_icon/iconfont.css'
// import '../static/cw-icon/iconfont.css'
import 'echarts/dist/extension/dataTool'
import VeeValidate, {Validator} from 'vee-validate'

const config = {
    errorBagName: 'veeErrors',
    fieldsBagName: 'veeFields'
}
Vue.use(VeeValidate, config)
Vue.use(bkMagic)
Vue.use(Echarts)
Vue.use(Component)
Vue.use(axios)
Vue.prototype.$echarts = Echarts
Vue.prototype.$moment = moment
Vue.prototype.$cwMessage = cwMessage
// 将API方法绑定到全局
Vue.prototype.$http = axios
Vue.prototype.$api = api
const headTheme = 'light' // 选择 light 或 blue
Vue.prototype.headTheme = headTheme
Vue.prototype.$lodash = lodash
Vue.prototype.hasPerm = hasPermission
Vue.config.productionTip = false
Vue.prototype.cloneDeep = function(data) {
    return lodash.cloneDeep(data)
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
