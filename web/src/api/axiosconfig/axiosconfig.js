// axios基础配置
import axios from 'axios'

axios.defaults.baseURL = window.siteUrl
axios.defaults.withCredentials = true
axios.defaults.timeout = 200000
axios.defaults.crossDomain = true

axios.interceptors.request.use((config) => {
    config.headers['X-Requested-With'] = 'XMLHttpRequest'
    const name = 'AUTHORIZATION'
    let cookieValue = 'NOTPROVIDED'
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    config.headers['AUTHORIZATION'] = cookieValue

    return config
})

axios.interceptors.response.use(response => {
    const status = response.status
    if (status > 300 || status < 200) {
        return {
            code: response.status,
            message: '请求异常，请刷新重试',
            result: false
        }
    }
    return response.data
}, error => {
    return {
        code: 500,
        message: error.response.data.message,
        error: error,
        result: false
    }
})

// 发送请求 (接口路径，参数，请求配置)
export function POST(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.post(url, params, config).then(
            res => {
                resolve(res)
            },
            err => {
                reject(err)
            }
        )
            .catch(err => {
                reject(err)
            })
    })
}

export function GET(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.get(url, {
            params: params,
            config: config
        })
            .then(res => {
                resolve(res)
            })
            .catch(err => {
                reject(err)
            })
    })
}
export function PUT(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.put(url, params, config).then(
            res => {
                resolve(res)
            },
            err => {
                reject(err)
            }
        )
            .catch(err => {
                reject(err)
            })
    })
}
export function DELETE(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.delete(url, {
            params: params,
            config: config
        })
            .then(res => {
                resolve(res)
            })
            .catch(err => {
                reject(err)
            })
    })
}
// 前后端分离开发时重定向配置
// reUrl = '';  不需要重定向
// todo do
export const reUrl = process.env.NODE_ENV === 'production' ? '' : '/api-proxy'
