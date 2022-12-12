import Vue from 'vue'

const vm = new Vue()

const cwMessage = function(data, theme) {
    if (typeof data === 'string') {
        vm.$bkMessage({
            theme: theme,
            message: data,
            delay: 1000
        })
    }
}
const types = [{
    key: 'info',
    theme: 'primary'
},
{
    key: 'primary',
    theme: 'primary'
},
{
    key: 'error',
    theme: 'error'
},
{
    key: 'success',
    theme: 'success'
},
{
    key: 'warning',
    theme: 'warning'
}
]
types.forEach(t => {
    cwMessage[t.key] = (data) => {
        return cwMessage(data, t)
    }
})
export default cwMessage
