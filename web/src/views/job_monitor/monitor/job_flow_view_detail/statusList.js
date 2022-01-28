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
},
{
    label: '取消',
    key: 'cancel',
    fill: '#C4C6CC'
},
{
    label: '待复核',
    key: 'need_confirm',
    fill: '#aa55ff'
}, {
    label: '正在执行（存在审核）',
    key: 'exists_need_confirm',
    fill: '#ffaaff'
}, {
    label: '正在执行（存在错误）',
    key: 'exists_error',
    fill: '#ff0000'
}, {
    label: '正在执行（存在失败）',
    key: 'exists_fail',
    fill: '#c30d0d'
}, {
    label: '正在执行（存在终止）',
    key: 'exists_stop',
    fill: '#5500ff'
}, {
    label: '正在执行（存在挂起）',
    key: 'exists_pause',
    fill: '#00557f'
}
]

export default statusList
