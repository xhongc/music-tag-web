/*
 * flow:
 * 继承 edge => 绘制edge => 设置edge状态
 */

import itemEvents from './item-event';


// const {edgeStyles, edgeStateStyles} = style
function drawShape(cfg, group) {
    const attrs = this.getShapeStyle(cfg, group);
    // 当前配置覆盖全局配置
    const shapeStyle = Object.assign({},
        this.getShapeStyle(cfg), {
            ...cfg.edgeStateStyles,
        });

    const keyShape = group.addShape('path', {
        className: 'edge-shape',
        name: 'edge-shape',
        attrs
    });
    this.initDeleteBtn(cfg, group);
    this.initEditBtn(cfg, group);

    return keyShape;
}

function setState(name, value, item) {
    const buildInEvents = [
        'edgeState:hover',
        'deleteEdge',
        'editEdge'
    ];
    const group = item.getContainer();

    if (group.get('destroyed')) return;
    if (buildInEvents.includes(name)) {
        // 内部this绑定到了当前item实例
        itemEvents[name].call(this, value, group);
    } else {
        console.warn(`warning: edge ${name} 事件回调未注册!`);
    }
}

export default (G6) => {
    G6.registerEdge('polyline-edge', {
        showDeleteEdgeBtn(cfg, group) {
            const shape = group.get('children')[0];
            const midPoint = shape.getPoint(0.5);
            const deleteBtn = group.addShape('text', {
                attrs: {
                    fontFamily: 'iconfont',
                    text: '\ue6a5',
                    fontSize: 18,
                    x: midPoint.x - 5,
                    y: midPoint.y - 5,
                    cursor: 'pointer',
                    fill: 'red',
                    edgeDeleteBtn: true
                },
                zIndex: 99999,
                nodeId: group.get('id'),
                className: 'edge-delete',
            });
            group.DeleteEdgeBtn = deleteBtn
        },
        showEditEdgeBtn(cfg, group) {
            const shape = group.get('children')[0];
            const midPoint = shape.getPoint(0.5);
            const editBtn = group.addShape('text', {
                attrs: {
                    fontFamily: 'iconfont',
                    text: '\ue675',
                    fontSize: 18,
                    x: midPoint.x - 35,
                    y: midPoint.y - 5,
                    cursor: 'pointer',
                    // fill: 'rgb(176,189,213)',
                    fill: '#3a84ff',
                    editEdgeBtn: true
                },
                zIndex: 99999,
                nodeId: group.get('id'),
                className: 'edge-delete',
            });
            group.editEdgeBtn = editBtn
        },
        initDeleteBtn(cfg, group) {
            group.DeleteEdgeBtn = null
            group.showDeleteEdgeBtn = group => {
                this.showDeleteEdgeBtn(cfg, group)
            };
            group.clearDeleteEdgeBtn = group => {
                if (group.DeleteEdgeBtn) {
                    group.DeleteEdgeBtn.remove()
                    group.DeleteEdgeBtn = null
                }
            };
        },
        initEditBtn(cfg, group) {
            group.editEdgeBtn = null
            group.showEditEdgeBtn = group => {
                this.showEditEdgeBtn(cfg, group)
            };
            group.clearEditEdgeBtn = group => {
                if (group.editEdgeBtn) {
                    group.editEdgeBtn.remove()
                    group.editEdgeBtn = null
                }
            };
        },
        setState,
        drawShape
    }, 'polyline')
    G6.registerEdge('line-edge', {
        showDeleteEdgeBtn(cfg, group) {
            const shape = group.get('children')[0];
            const midPoint = shape.getPoint(0.5);
            const Btn = group.addShape('text', {
                attrs: {
                    fontFamily: 'iconfont',
                    text: '\ue6a5',
                    fontSize: 24,
                    x: midPoint.x - 5,
                    y: midPoint.y - 5,
                    cursor: 'pointer',
                    fill: 'red'
                },
                zIndex: 99999,
                nodeId: group.get('id'),
                className: 'edge-delete',
            });
            group.DeleteEdgeBtn = Btn
        },
        initDeleteBtn(cfg, group) {
            group.DeleteEdgeBtn = null
            group.showDeleteEdgeBtn = group => {
                this.showDeleteEdgeBtn(cfg, group)
            };
            group.clearDeleteEdgeBtn = group => {
                if (group.DeleteEdgeBtn) {
                    group.DeleteEdgeBtn.remove()
                    group.DeleteEdgeBtn = null
                }
            };
        },
        initEditBtn(cfg, group) {
            group.DeleteEdgeBtn = null
            group.showDeleteEdgeBtn = group => {
                this.showDeleteEdgeBtn(cfg, group)
            };
            group.clearDeleteEdgeBtn = group => {
                if (group.DeleteEdgeBtn) {
                    group.DeleteEdgeBtn.remove()
                    group.DeleteEdgeBtn = null
                }
            };
        },
        setState,
        drawShape
    }, 'line')
    G6.registerEdge('cubic-vertical-edge', {
        showDeleteEdgeBtn(cfg, group) {
            const shape = group.get('children')[0];
            const midPoint = shape.getPoint(0.5);
            const Btn = group.addShape('text', {
                attrs: {
                    fontFamily: 'iconfont',
                    text: '\ue68a',
                    fontSize: 24,
                    x: midPoint.x - 5,
                    y: midPoint.y - 5,
                    cursor: 'pointer',
                    fill: 'red'
                },
                zIndex: 99999,
                nodeId: group.get('id'),
                className: 'edge-delete',
            });
            group.DeleteEdgeBtn = Btn
        },
        initDeleteBtn(cfg, group) {
            group.DeleteEdgeBtn = null
            group.showDeleteEdgeBtn = group => {
                this.showDeleteEdgeBtn(cfg, group)
            };
            group.clearDeleteEdgeBtn = group => {
                if (group.DeleteEdgeBtn) {
                    group.DeleteEdgeBtn.remove()
                    group.DeleteEdgeBtn = null
                }
            };
        },
        setState,
        drawShape
    }, 'cubic-vertical')
};
