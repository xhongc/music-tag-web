const baseNodes = [{
    detail: false,
    // id: getUUID(32, 16),
    label: '开始',
    name: '开始',
    type: 'circle-node',
    icon: 'dian',
    content: null,
    // state: 'wait',
    // newState: '等待',
    node_data: {
        node_name: '开始',
        description: '我是开始',
        fail_retry_count: 0,
        node_type: 0,
        is_skip_fail: false,
        is_timeout_alarm: false,
        inputs: {},
        outputs: {}
    },
    nodeType: 0,
    endUuid: '',
    labelCfg: {
        style: {
            textAlign: 'center'
        }
    },
    style: {
        fill: '#fff',
        r: 24
    },
    x: 600,
    y: 300
}, {
    detail: false,
    // id: getUUID(32, 16),
    label: '结束',
    name: '结束',
    nodeType: 1,
    endUuid: '',
    icon: 'dian',
    content: null,
    // state: 'wait',
    // newState: '等待',
    node_data: {
        node_name: '结束',
        description: '我是结束',
        fail_retry_count: 0,
        node_type: 0,
        is_skip_fail: false,
        is_timeout_alarm: false,
        inputs: {},
        outputs: {}
    },
    type: 'circle-node',
    labelCfg: {
        style: {
            textAlign: 'center'
        }
    },
    style: {
        fill: '#fff',
        r: 24
    },
    x: 800,
    y: 300
}]

export default baseNodes
