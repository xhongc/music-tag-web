import {
    validatenull
} from './util.js'

/**
 * 存储localStorage
 */
export const setStore = (params = {}) => {
    const {
        name,
        content
    } = params
    const obj = {
        dataType: typeof content,
        content: content,
        datetime: new Date().getTime()
    }
    window.localStorage.setItem(name, JSON.stringify(obj))
}
/**
 * 获取localStorage
 */

export const getStore = (params = {}) => {
    const {
        name
    } = params
    let obj = {}
    obj = window.localStorage.getItem(name)
    if (validatenull(obj)) return
    obj = JSON.parse(obj)
    // if (obj.dataType == 'string') {
    //     content = obj.content;
    // } else if (obj.dataType == 'number') {
    //     content = Number(obj.content);
    // } else if (obj.dataType == 'boolean') {
    //     content = eval(obj.content);
    // } else if (obj.dataType == 'object') {
    //     content = obj.content;
    // }
    return obj.content
}
/**
 * 删除localStorage
 */
export const removeStore = (params = {}) => {

}

/**
 * 获取全部localStorage
 */
export const getAllStore = (params = {}) => {

}

/**
 * 清空全部localStorage
 */
export const clearStore = (params = {}) => {
    window.localStorage.clear()
}
