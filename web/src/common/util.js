/**
 * 对象深拷贝
 */

export const getObjType = obj => {
    const toString = Object.prototype.toString
    const map = {
        '[object Boolean]': 'boolean',
        '[object Number]': 'number',
        '[object String]': 'string',
        '[object Function]': 'function',
        '[object Array]': 'array',
        '[object Date]': 'date',
        '[object RegExp]': 'regExp',
        '[object Undefined]': 'undefined',
        '[object Null]': 'null',
        '[object Object]': 'object'
    }
    if (obj instanceof Element) {
        return 'element'
    }
    return map[toString.call(obj)]
}

export const deepClone = data => {
    const type = getObjType(data)
    let obj
    if (type === 'array') {
        obj = []
    } else if (type === 'object') {
        obj = {}
    } else {
        // 不再具有下一层次
        return data
    }
    if (type === 'array') {
        for (let i = 0, len = data.length; i < len; i++) {
            obj.push(deepClone(data[i]))
        }
    } else if (type === 'object') {
        for (const key in data) {
            obj[key] = deepClone(data[key])
        }
    }
    return obj
}

/**
 * 判断是否为空
 */
export function validatenull(val) {
    if (typeof val === 'boolean') {
        return false
    }
    if (typeof val === 'number') {
        return false
    }
    if (val instanceof Array) {
        if (val.length === 0) return true
    } else if (val instanceof Object) {
        if (JSON.stringify(val) === '{}') return true
    } else {
        if (val === 'null' || val === null || val === 'undefined' || val === undefined || val === '') return true
        return false
    }
    return false
}

/**
 * 判断是否为json
 */

export function isJson(str) {
    if (typeof str === 'string') {
        try {
            const obj = JSON.parse(str)
            if (typeof obj === 'object' && obj) {
                return true
            } else {
                return false
            }
        } catch (e) {
            return false
        }
    }
}

/**
 * 生成uuid
 */
export function getUUID(len, radix) {
    /*
           * 生成唯一标识符UUID
           * @param len 长度
           * @param radix 基数 二进制 八进制 十进制 十六进制
           * return uuid
           * 调用 let uuidstr = uuid(32,16) // 生成32 位长度的基数为16进制的uuid
           * 7FEA14A4722E273EE28C3F72E9E9141F
           * */
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('')
    const uuid = []
    radix = radix || chars.length
    if (len) {
        for (let i = 0; i < len; i++) uuid[i] = chars[0 | Math.random() * radix]
    } else {
        uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-'
        uuid[14] = '4'
        for (let i = 0; i < 36; i++) {
            if (!uuid[i]) {
                const r = 0 | Math.random() * 16
                uuid[i] = chars[(i === 19) ? (r & 0x3) | 0x8 : r]
            }
        }
    }
    return uuid.join('')
}
