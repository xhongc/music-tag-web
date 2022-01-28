export default {
    // node默认样式
    nodeStyles: {
        fill: '#fff', // 浅蓝
    },
    // node 交互样式
    nodeStateStyles: {
        'nodeState:default': {
            fill: '#ecf3ff',
        },
        // 鼠标 hover 上节点，即 hover 状态为 true 时的样式
        'nodeState:hover': {
            cursor: 'pointer',
            shadowOffsetX: 0,
            shadowOffsetY: 4,
            shadowBlur: 10,
            opacity: 0.8,
        },
        // 鼠标点击节点，即 selected 状态为 true 时的样式
        'nodeState:selected': {
            fill: 'red',
            stroke: '#1890FF',
            cursor: 'default',
        },
    },
    // node 文本默认样式
    nodeLabelStyles: {
        maxlength: 8,
        style: {
            fontSize: 12,
            fill: '#333333',
            // textAlign: 'center',
            textBaseline: 'middle',
            cursor: 'pointer',
        },
    },
    // node 文本交互样式
    nodeLabelStateStyles: {
        'nodeLabelState:default': {

        },
        'nodeLabelState:hover': {

        },
        'nodeLabelState:selected': {

        },
    },
    /* node图标默认样式 */
    iconStyles: {
        width: 20,
        height: 20,
        x: 0,
        y: 0,
    },
    // edge默认样式
    edgeStyles: {
        stroke: '#aab7c3',
        lineAppendWidth: 10,
        startArrow: {
            path: 'M 0,0 L 8,4 L 7,0 L 8,-4 Z',
            fill: '#aab7c3',
        },
        endArrow: {
            path: 'M 0,0 L 8,4 L 7,0 L 8,-4 Z',
            fill: '#aab7c3',
        },
    },
    // edge交互样式
    edgeStateStyles: {
        // 鼠标点击边，即 selected 状态为 true 时的样式
        selected: {
            stroke: '#aab7c3',
        },
        hover: {
            stroke: '#aab7c3',
        },
    },
    anchorPointStyles: {
        r: 1,
        // fill: '#fff',
        stroke: '#1890FF',
        lineWidth: 2,
    },
};
