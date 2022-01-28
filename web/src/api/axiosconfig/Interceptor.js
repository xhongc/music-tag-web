// 拦截配置
import Vue from 'vue'

// 请求拦截
export function requestFunc(request) {
    // if (request.config.showLoad) Vue.prototype.$showLoading();
    return request
}

// axios 响应成功回调函数
export function responseSuccessFunc(response) {
    // Vue.prototype.$CloseLoading();
    const data = response.data.message
    if (data) {
        if (typeof (data) === 'string') {
            console.log(123)
        } else {
            const midstr = []
            for (const i in data) {
                midstr.push(data[i])
            }
            response.data.message = midstr.join(',')
        }
    }
    // let data = response.data.message
    // // if (typeof (data) == 'string') {
    // // } else {
    // try {
    //     let midstr = []
    //     for (let i in data) {
    //         midstr.push(data[i])
    //     }
    //     response.data.message = midstr.join(',')
    // } catch {
    // }
    // }
    return response.data
}

// axios 响应失败回调函数
export function responseFailFunc(error) {
    // Vue.prototype.$CloseLoading();
    if (error.response) {
        switch (error.response.status) {
            case 404:
                break
            case 500:
                Vue.prototype.$Message.error('服务器错误，请联系管理员')
        }
    } else if (error.request) {
        if (error.code === 'ECONNABORTED') {
            Vue.prototype.$Message.error('远程主机拒绝网络连接')
        }
    } else {
        console.log(456)
    }
    return Promise.reject(error)
}
