// 表单验证
import Vue from 'vue'
import VeeValidate, {
    Validator
} from 'vee-validate'
import VueI18n from 'vue-i18n'
import zhCN from 'vee-validate/dist/locale/zh_CN'

// 国际化
Vue.use(VueI18n)
const i18n = new VueI18n({
    locale: 'zh_CN'
})

// 自定义validate
const Dictionary = {
    zhCN: {
        messages: {
            required: field => '请输入' + field
        },
        attributes: {
            name: '账号'
        }
    }
}

// 自定义validate error 信息
Validator.localize(Dictionary)

// 自定义表单
Validator.extend('phone', {
    messages: {
        zhCN: field => field + '必须是11位手机号码'
    },
    validate: value => {
        return value.length === 11 && /^((13|14|15|17|18)[0-9]{1}\d{8})$/.test(value)
    }
})

Vue.use(VeeValidate, {
    i18n,
    // events:'', // 添加校验事件
    i18nRootKey: 'validation',
    dictionary: {
        zhCN
    },
    fieldsBagName: 'fieldBags' // fields重命名，和ElementUI冲突
})
