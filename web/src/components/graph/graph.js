import registerFactory from './register-factory';
let dragStartNode = {}
export default (G6, config) => {
    const options = Object.assign({
        container: 'main',
        width: window.innerWidth,
        height: window.innerHeight,
        fitViewPadding: 20,
        animate: true,
        animateCfg: {
            duration: 500,
            easing: 'easeLinear',
        },
        // layout: {
        //     type: 'dagre',
        //     // rankdir: 'LR',
        //     nodesep: 30,
        //     ranksep: 30,
        // },
        modes: {
            // 允许拖拽画布、缩放画布、拖拽节点
            default: [
                'drag-canvas', // 官方内置的行为
                'zoom-canvas',
                // 'canvas-event', // 自定义行为
                // 'delete-item',
                'select-node',
                'hover-node',
                'active-edge',
                'hover-edge'
            ],
        },
        //默认节点样式
        defaultNode: {
            type: 'rect-node',
            style: {
                radius: 10,
            },
        },
        //默认边样式
        defaultEdge: {
            type: 'polyline-edge', // polyline
            style: {
                radius: 6,
                offset: 15,
                stroke: '#aab7c3',
                lineAppendWidth: 10, // 防止线太细没法点中
                endArrow: {
                    path: 'M 0,0 L 8,4 L 7,0 L 8,-4 Z',
                    fill: '#aab7c3',
                    stroke: '#aab7c3',
                },
            },
        },
        // 默认节点不同状态下的样式集合
        nodeStateStyles: {
            'nodeState:default': {
                fill: '#E7F7FE',
                stroke: '#1890FF',
            },
            'nodeState:hover': {
                fill: '#d5f1fd',
            },
            'nodeState:selected': {
                fill: '#caebf9',
                stroke: '#1890FF',
            },
        },
        // 默认边不同状态下的样式集合
        edgeStateStyles: {
            'edgeState:default': {
                stroke: '#aab7c3',
                endArrow: {
                    path: 'M 0,0 L 8,4 L 7,0 L 8,-4 Z',
                    fill: '#aab7c3',
                    stroke: '#aab7c3',
                },
            },
            'edgeState:selected': {
                stroke: '#1890FF',
            },
            'edgeState:hover': {
                stroke: '#1890FF',
            },
        }
    }, config)
    registerFactory(G6);
    return options;
}
