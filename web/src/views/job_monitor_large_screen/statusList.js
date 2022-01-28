const statusList = [{
    label: '成功',
    key: 'success',
    fill: '#2DCB56'
}, {
    label: '正在执行',
    key: 'run',
    fill: '#3A84FF'
}, {
    label: '失败',
    key: 'fail',
    fill: '#FF9C01'
}, {
    label: '终止',
    key: 'stop',
    fill: '#A60505'
}, {
    label: '错误',
    key: 'error',
    fill: '#EA3636'
}, {
    label: '等待',
    key: 'wait',
    fill: '#FFFFFF'
}, {
    label: '就绪',
    key: 'positive',
    fill: '#94F5A4'
}, {
    label: '挂起',
    key: 'pause',
    fill: '#FD9C9C'
},
{
    label: '忽略',
    key: 'ignore',
    fill: '#aa557f'
}, {
    label: '正在执行(存在阻塞)',
    key: 'exists_error',
    fill: '#699DF4'
}, {
    label: '取消',
    key: 'cancel',
    fill: '#C4C6CC'
}, {
    label: '尚未实例化',
    key: 'no_instance',
    fill: '#A3C5FD'
}
]

export default statusList
