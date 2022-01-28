import Vue from 'vue'
import Router from 'vue-router'

const originalPush = Router.prototype.push
Router.prototype.push = function(location) {
    return originalPush.call(this, location).catch(err => err)
}
Vue.use(Router)

const constantRouterMap = []

export default new Router({
    routes: constantRouterMap
})
