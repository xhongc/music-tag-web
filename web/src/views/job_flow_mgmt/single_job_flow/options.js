const options = {
    defaultNode: {
        type: 'rect-node',
        style: {
            radius: 10
        },
        labelCfg: {
            fontSize: 20
        }
    },
    defaultEdge: {
        type: 'polyline-edge', // 扩展了内置边, 有边的事件
        // type: 'cubic-vertical-edge', // 扩展了内置边, 有边的事件
        labelCfg: {
            refY: -15,
            style: {
                fill: '#1890ff',
                fontSize: 14,
                cursor: 'pointer',
                background: {
                    fill: '#ffffff',
                    stroke: '#9EC9FF',
                    padding: [4, 4, 4, 4],
                    radius: 2
                }
            }
        },
        style: {
            radius: 0, // 拐弯弧度
            offset: 15, // 拐弯处距离节点的最小距离
            stroke: '#aab7c3',
            lineAppendWidth: 30, // 防止线太细没法点中
            // endArrow: true,
            endArrow: {
                path: 'M 0,0 L 4,3 L 3,0 L 4,-3 Z',
                fill: '#aab7c3',
                stroke: '#aab7c3'
            },
            zIndex: 999999
        }
    },
    // 覆盖全局样式
    nodeStateStyles: {
        'nodeState:default': {
            opacity: 1,
            fill: '#fff',
            stroke: '#DCDEE5',
            labelCfg: {
                style: {
                    fill: '#333333'
                }
            }
        },
        'nodeState:hover': {
            opacity: 0.8
        },
        'nodeState:selected': {
            opacity: 0.9,
            stroke: 'rgb(58,132,255)',
            labelCfg: {
                style: {
                    fill: 'rgb(58,132,255)'
                }
            }
        }
    },
    // 默认边不同状态下的样式集合
    edgeStateStyles: {
        'edgeState:default': {
            stroke: '#aab7c3'
        },
        'edgeState:selected': {
            stroke: '#1890FF'
        },
        'edgeState:hover': {
            animate: true,
            animationType: 'dash',
            stroke: '#1890FF'
        }
    },
    modes: [
        'drag-canvas', // 官方内置的行为
        'zoom-canvas',
        'select-node',
        'hover-node',
        'active-edge',
        'hover-edge'
    ]
}

export default options
