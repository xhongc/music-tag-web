export default G6 => {
    G6.registerBehavior('drag-node', {
        getDefaultCfg() {
            return {
                sourceAnchorIndex: 0,
                // 记录当前拖拽模式(拖拽目标可能是节点也可能是锚点)
                dragTarget: 'node',
                dragStartNode: {},
                distance: [], // 鼠标距离节点中心位置的距离
            };
        },
        getEvents() {
            return {
                'node:mousedown': 'onMousedown',
                'node:mouseup': 'onMouseup',
                'node:dragstart': 'onDragStart',
                'node:drag': 'onDrag',
                'node:dragend': 'onDragEnd',
                'node:drop': 'onDrop',
            };
        },
        // 鼠标按下显示锚点光圈
        onMousedown(e) {
            this._clearSelected(e);
            if (e.target.cfg.isAnchor) {
                // 拖拽锚点
                this.dragTarget = 'anchor';
                this.dragStartNode = {
                    ...e.item._cfg,
                    anchorIndex: e.target.cfg.index,
                };
                const nodes = this.graph.findAll('node', node => node);

                nodes.forEach(node => {
                    // this.graph.setItemState(node, 'anchorActived', true);
                    node.setState('anchorActived', true);
                });
            }
            this.graph.emit('on-node-mousedown', e);
        },
        onMouseup(e) {
            if (this.dragTarget === 'anchor') {
                const nodes = this.graph.findAll('node', node => node);

                nodes.forEach(node => {
                    node.clearStates('anchorActived');
                });
            }
            this.graph.emit('on-node-mouseup', e);
        },
        // 拖拽开始
        onDragStart(e) {
            if (e.target.get('isAnchor')) {
                // 拖拽锚点, 记录当前点击的锚点 index
                this.sourceAnchorIndex = e.target.get('index');
            } else {
                // 拖拽节点
                e.item.toFront();
                this.dragTarget = 'node';
                this._nodeOnDragStart(e, e.item.getContainer());
            }
            this.graph.emit('on-node-dragstart', e);
        },
        // 拖拽中
        onDrag(e) {
            if (this.dragTarget === 'node') {
                this._nodeOnDrag(e, e.item.getContainer());
            }
            this.graph.emit('on-node-drag', e)
        },
        // 拖拽结束
        onDragEnd(e) {
            const group = e.item.getContainer();

            if (this.dragTarget === 'anchor') {
                const nodes = this.graph.findAll('node', node => node);

                nodes.forEach(node => {
                    node.clearStates('anchorActived');
                });
            } else if (this.dragTarget === 'node') {
                this._nodeOnDragEnd(e, group);
            }
            this.graph.emit('on-node-dragend', e);
        },
        // 锚点拖拽结束添加边
        onDrop(e) {
            //当前为节点拖拽后释放，不做处理
            if (this.dragTarget === 'node') {
                return false
            } else {
                //当前为锚点拖拽后释放
                const targetNode = e.item.getContainer().get('item') //目标节点
                const sourceNode = this.dragStartNode.group.get('item'); //起始节点
                //自己连自己
                if (targetNode._cfg.id === sourceNode._cfg.id) {
                    return this.graph.emit('before-edge-add', false, {msg: '无效的操作！'})
                }
                //开始节点直连结束节点
                if (targetNode._cfg.model.nodeType === 1 && sourceNode._cfg.model.nodeType === 0) {
                    return this.graph.emit('before-edge-add', false, {msg: '禁止开始节点直连结束节点！'})
                }
                //结束节点直连开始节点
                if (targetNode._cfg.model.nodeType === 0 && sourceNode._cfg.model.nodeType === 1) {
                    return this.graph.emit('before-edge-add', false, {msg: '禁止结束节点直连开始节点！'})
                }
                //从结束节点开始
                if (sourceNode._cfg.model.nodeType === 1) {
                    return this.graph.emit('before-edge-add', false, {msg: '禁止从结束节点开始！'})
                }
                //从开始节点结束
                if (targetNode._cfg.model.nodeType === 0 && sourceNode._cfg.model.nodeType !== 3) {
                    return this.graph.emit('before-edge-add', false, {msg: '禁止从开始节点结束！'})
                }
                //从作业流节点结束
                if (targetNode._cfg.model.nodeType === 3) {
                    return this.graph.emit('before-edge-add', false, {msg: '禁止从作业流节点结束！'})
                }
                let msg = ''
                this.graph.getEdges().forEach(line => {
                    //重复连线
                    if(line._cfg.model.source === sourceNode._cfg.id && line._cfg.model.target === targetNode._cfg.id) {
                        msg = '禁止重复连线'
                    }
                    //回环连线
                    if(sourceNode._cfg.id === line._cfg.model.target && targetNode._cfg.id === line._cfg.model.source) {
                        msg = '禁止回环连线'
                    }
                })
                //重复连线
                if(msg) {
                    return this.graph.emit('before-edge-add', false, {msg: msg})
                }
                return this.graph.emit('before-edge-add', true, {
                    targetNode,
                    sourceNode
                })
            }
        },

        /**
         * @description 节点拖拽开始事件
         */
        _nodeOnDragStart(e, group) {
            const item = group.get('item');
            const {
                radius
            } = item.get('originStyle');
            const currentShape = item.get('currentShape');
            const {
                width,
                height,
                centerX,
                centerY
            } = item.getBBox();

            let {
                shapeType
            } = item.get('shapeFactory')[currentShape];

            let attrs = {
                fillOpacity: 0.1,
                fill: '#1890FF',
                stroke: '#1890FF',
                cursor: 'move',
                lineDash: [4, 4],
                width,
                height,
            };

            switch (shapeType) {
                case 'circle':
                    this.distance = [e.x - centerX, e.y - centerY];
                    attrs = {
                        ...attrs,
                        x: 0,
                        y: 0,
                        r: width / 2,
                    };
                    break;
                case 'rect':
                    this.distance = [e.x - centerX + width / 2, e.y - centerY + height / 2];
                    attrs = {
                        ...attrs,
                        x: -width / 2,
                        y: -height / 2,
                        r: width / 2,
                    };
                    if (radius) attrs.radius = radius;
                    break;
                case 'ellipse':
                    this.distance = [e.x - centerX, e.y - centerY];
                    attrs = {
                        ...attrs,
                        x: 0,
                        y: 0,
                        rx: width / 2,
                        ry: height / 2,
                    };
                    break;
                case 'path':
                    this.distance = [e.x - centerX, e.y - centerY];
                    attrs.path = item.get('keyShape').attrs.path;
                    attrs.size = [width, height];
                    attrs.x = 0;
                    attrs.y = 0;
                    break;
                case 'modelRect':
                    this.distance = [e.x - centerX + width / 2, e.y - centerY + height / 2];
                    attrs = {
                        ...attrs,
                        x: -width / 2,
                        y: -height / 2,
                        r: width / 2,
                    };
                    shapeType = 'rect';
                    break;
            }

            const shadowNode = group.addShape(shapeType, {
                className: 'shadow-node',
                attrs,
            });

            shadowNode.toFront();
        },

        /**
         * @description 节点拖拽事件
         */
        _nodeOnDrag(e, group) {
            // 记录鼠标拖拽时与图形中心点坐标的距离
            const item = group.get('item');
            const pathAttrs = group.getFirst();
            const {
                width,
                height,
                centerX,
                centerY
            } = item.getBBox();
            const currentShape = item.get('currentShape');
            const {
                shapeType
            } = item.get('shapeFactory')[currentShape];
            const shadowNode = group.getItem ? group.getItem('shadow-node') : null;

            if (!shadowNode) {
                return console.warn('暂未支持拖拽内置节点');
            }
            if (shapeType === 'path') {
                const {
                    type,
                    direction
                } = pathAttrs.get('attrs');
                const dx = e.x - centerX - this.distance[0];
                const dy = e.y - centerY - this.distance[1];
                const path = [
                    ['Z']
                ];

                switch (type) {
                    case 'diamond-node':
                        path.unshift(
                            ['M', dx, dy - height / 2], // 上顶点
                            ['L', dx + width / 2, dy], // 右侧顶点
                            ['L', dx, dy + height / 2], // 下顶点
                            ['L', dx - width / 2, dy], // 左侧顶点
                        );
                        break;
                    case 'triangle-node':
                        path.unshift(
                            ['L', dx + width / 2, dy], // 右侧顶点
                            ['L', dx - width / 2, dy], // 左侧顶点
                        );
                        if (direction === 'up') {
                            path.unshift(
                                ['M', dx, dy - height], // 上顶点
                            );
                        } else {
                            path.unshift(
                                ['M', dx, dy + height], // 下顶点
                            );
                        }
                        break;
                }

                shadowNode.attr({
                    path,
                });
            } else {
                shadowNode.attr({
                    x: e.x - centerX - this.distance[0],
                    y: e.y - centerY - this.distance[1],
                });
            }
            shadowNode.toFront();
        },

        /**
         * @description 节点拖拽结束事件
         */
        _nodeOnDragEnd(e, group) {
            const node = group.get('item');
            const {
                width,
                height
            } = node.getBBox();
            const shadowNode = group.getItem ? group.getItem('shadow-node') : null;
            const currentShape = node.get('currentShape');
            const {
                shapeType
            } = node.get('shapeFactory')[currentShape];
            const {
                type,
                direction
            } = group.getFirst().get('attrs');
            const coords = {
                x: 0,
                y: 0,
            };

            switch (shapeType) {
                case 'ellipse':
                case 'circle':
                    coords.x = e.x - this.distance[0];
                    coords.y = e.y - this.distance[1];
                    break;
                case 'rect':
                    coords.x = e.x - this.distance[0] + width / 2;
                    coords.y = e.y - this.distance[1] + height / 2;
                    break;
                case 'path':
                    coords.x = e.x - this.distance[0];
                    coords.y = e.y - this.distance[1];
                    if (type === 'triangle-node') {
                        if (direction === 'up') {
                            coords.y += height / 2;
                        } else {
                            coords.y -= height / 2;
                        }
                    }
                    break;
            }

            shadowNode && shadowNode.remove();

            /* 添加移动动画? */
            // 更新坐标
            node.updatePosition(coords);

            // 当节点位置发生变化时，刷新所有节点位置，并重计算边的位置
            // console.log(this.graph.refreshPositions())
            this.graph.emit('after-node-drop', e)
            this.graph.refreshPositions();
        },
        // 清空已选的边
        _clearSelected(e) {
            const selectedEdges = this.graph.findAllByState('edge', 'edgeState:selected');

            selectedEdges.forEach(edge => {
                edge.clearStates(['edgeState:selected', 'edgeState:hover']);
            });
        },
    });
};
