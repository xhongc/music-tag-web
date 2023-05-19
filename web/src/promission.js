import router from './router'
import store from '@/vuex/index'
import Home from '@/views/home/home'
import User from '@/views/user/index'
import Login from '@/views/user/login'
import Music from '@/views/music/index'

// const _import = require('./router/_import_' + process.env.NODE_ENV) // 获取组件的方法

let getRouter // 用来获取后台拿到的路由
// let getMenuList // 用来获取后台拿到的菜单
saveObjArr('router', '')

router.beforeEach((to, from, next) => {
    // console.log(getRouter)
    if (!getRouter) { // 不加这个判断，路由会陷入死循环
        if (!getObjArr('router')) {
            getRouter = [
                {
                    'path': '/',
                    'name': 'home',
                    'component': 'Home',
                    'meta': {
                        'title': '音乐标签Web版'
                    }
                },
                {
                    'path': '/music',
                    'name': 'music',
                    'component': 'Music',
                    'meta': {
                        'title': '音乐标签Web版'
                    }
                },
                {
                    'path': '/user',
                    'name': 'user',
                    'component': 'User',
                    'meta': {
                        'title': '用户信息'
                    }
                },
                {
                    'path': '/login',
                    'name': 'login',
                    'component': 'Login',
                    'meta': {
                        'title': '登录'
                    }
                }
            ]
            saveObjArr('router', getRouter) // 存储路由到localStorage
            routerGo(to, next) // 执行路由跳转方法
        } else { // 从localStorage拿到了路由
            getRouter = getObjArr('router') // 拿到路由
            routerGo(to, next)
        }
    } else {
        next()
    }
})

function routerGo(to, next) {
    getRouter = filterAsyncRouter(getRouter) // 过滤路由
    router.addRoutes(getRouter) // 动态添加路由
    store.state.antRouter = getRouter // 将路由数据传递给全局变量
    // store.state.displayMenu = getMenuList //将菜单数据传递给全局变量，做侧边栏菜单渲染工作
    // store.state.displayButton = getButton // 将按钮权限数据传递给全局变量，做页面按钮权限渲染工作
    next({
        ...to,
        replace: true
    })
}

function saveObjArr(name, data) { // localStorage 存储数组对象的方法
    localStorage.setItem(name, JSON.stringify(data))
}

function getObjArr(name) { // localStorage 获取数组对象的方法
    return JSON.parse(window.localStorage.getItem(name))
}

const ROUTER_MAP = {
    'Home': Home,
    'User': User,
    'Login': Login,
    'Music': Music
}

function filterAsyncRouter(asyncRouterMap) { // 遍历后台传来的路由字符串，转换为组件对象
    const accessedRouters = asyncRouterMap.filter(route => {
        if (route.component) {
            route.component = ROUTER_MAP[route.component]
        }
        if (route.children && route.children.length) {
            route.children = filterAsyncRouter(route.children)
        }
        return true
    })
    return accessedRouters
}

// 用来控制按钮的显示与否
export function hasPermission(permission) {
    const myBtns = store.state.permission.btnPermission
    for (let i = 0; i < myBtns.length; i++) {
        if (myBtns[i].url === permission) {
            return myBtns[i].auth
        }
    }
}
