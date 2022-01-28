import itemEvents from './item-event';
import anchorEvent from './anchor-event';
import defaultStyles from '../defaultStyle';
import colorList from './colorList'


const {
    iconStyles,
    nodeStyles,
    anchorPointStyles,
    nodeLabelStyles,
} = defaultStyles;

function getStyle(options, cfg) {
    return {
        ...cfg,
        // 自定义默认样式
        ...nodeStyles,
        ...options,
        // 当前节点样式
        ...cfg.style,
        // 文本配置
        labelCfg: {
            ...nodeLabelStyles,
            ...cfg.labelCfg,
        },
        // 图标样式
        iconStyles: {
            ...iconStyles,
            ...cfg.iconStyles,
        },
        // 锚点样式
        anchorPointStyles: {
            ...anchorPointStyles,
            ...cfg.anchorPointStyles,
        },
        ...cfg.nodeStateStyles,
        // 锚点高亮样式
        anchorHotsoptStyles: cfg.anchorHotsoptStyles,
    };
}

/*
 * 注册基础node => 添加锚点/图标 => 绘制node => 初始化node状态 => node动画(设置交互动画)
 */
export default G6 => {
    G6.registerNode('base-node', {
        getShapeStyle(cfg) {
            const width = cfg.style.width || 80;
            const height = cfg.style.height || 40;

            return getStyle.call(this, {
                width,
                height,
                radius: 5,
                // 将图形中心坐标移动到图形中心, 用于方便鼠标位置计算
                x: -width / 2,
                y: -height / 2,
            }, cfg);
        },
        // 绘制图标
        drawIcon(cfg, group, attrs) {
            // if(attrs.hasOwnProperty('state') && attrs.state !== '') {
            //     labelCfg.style.fill = colorList[attrs.state].color
            // }
            const item = group.get('children')[0];
            //当前节点拥有icon且不为开始和结束节点
            if (item.attrs.hasOwnProperty('icon') && (attrs.nodeType != 0 || attrs.nodeType != 1)) {
                //分支节点和作业节点显示同一个icon
                if (attrs.nodeType === 2 || attrs.nodeType === 4) {
                    const icon = group.addShape('text', {
                        attrs: {
                            fontFamily: 'iconfont',
                            text: '\ue6d9',
                            fontSize: 24,
                            x: -60,
                            y: 12,
                            cursor: 'pointer',
                            fill: (attrs.hasOwnProperty('state') && attrs.state !== '') ? colorList[
                                attrs.state].color : attrs.style.iconCfg.fill
                        },
                        draggable: true,
                    })
                }
                //表明是作业流节点
                if (attrs.nodeType === 3) {
                    const icon = group.addShape('text', {
                        attrs: {
                            fontFamily: 'iconfont',
                            text: '\ue6d4',
                            fontSize: 24,
                            x: -60,
                            y: 12,
                            cursor: 'pointer',
                            fill: (attrs.hasOwnProperty('state') && attrs.state !== '') ? colorList[
                                attrs.state].color : attrs.style.iconCfg.fill
                        },
                        draggable: true,
                    })
                }
                if (attrs.nodeType === 5) {
                    const icon = group.addShape('text', {
                        attrs: {
                            fontFamily: 'iconfont',
                            text: '\ue6d6',
                            fontSize: 24,
                            x: -60,
                            y: 12,
                            cursor: 'pointer',
                            fill: (attrs.hasOwnProperty('state') && attrs.state !== '') ? colorList[
                                attrs.state].color : attrs.style.iconCfg.fill
                        },
                        draggable: true,
                    })
                }
            }
        },
        // 绘制锚点
        initAnchor(cfg, group) {
            group.anchorShapes = [];
            //显示锚点方法
            group.showAnchor = group => {
                this.drawAnchor(cfg, group);
            };
            //情空锚点方法
            group.clearAnchor = group => {
                group.anchorShapes && group.anchorShapes.forEach(a => a.remove());
                group.anchorShapes = [];
            };
        },
        //绘制节点删除按钮
        initDeleteBtn(cfg, group) {
            group.deleteBtn = null
            //显示删除按钮方法
            group.showDeleteBtn = group => {
                this.drawDeleteBtn(cfg, group);
            };
            group.clearDeleteBtn = group => {
                if (group.deleteBtn) {
                    group.deleteBtn.remove()
                    group.deleteBtn = null
                }
            };
        },
        drawDeleteBtn(cfg, group) {
            const item = group.get('children')[0];
            const bBox = item.getBBox();
            const btn = group.addShape('text', {
                attrs: {
                    fontFamily: 'iconfont',
                    text: '\ue67d',
                    cursor: 'pointer',
                    fill: 'red',
                    fontSize: 16,
                    x: bBox.width / 2,
                    y: -(bBox.height / 2),
                    nodeDeleteBtn: true
                },
                zIndex: 999998,
                nodeId: group.get('id'),
                className: 'node-delete'
            })
            // btn.on('click', (e) => {
            //     console.log(e)
            // })
            group.deleteBtn = btn
        },
        drawAnchor(cfg, group) {
            const {
                type,
                direction,
                anchorPointStyles
            } = group.getFirst().attr();
            const item = group.get('children')[0];
            const bBox = item.getBBox();
            const anchors = this.getAnchorPoints(cfg);
            // 绘制锚点坐标
            anchors && anchors.forEach((p, i) => {
                const diff = type === 'triangle-node' ? (direction === 'up' ? 1 : 0) : 0.5;
                const x = bBox.width * (p[0] - 0.5);
                const y = bBox.height * (p[1] - diff);

                /**
                 * 绘制三层锚点
                 * 最底层: 锚点bg
                 * 中间层: 锚点
                 * 最顶层: 锚点group, 用于事件触发
                 */
                // 视觉锚点
                const anchor = group.addShape('circle', {
                    attrs: {
                        x,
                        y,
                        ...anchorPointStyles,
                    },
                    zIndex: 1,
                    nodeId: group.get('id'),
                    className: 'node-anchor',
                    draggable: true,
                    isAnchor: true,
                    index: i,
                });

                // 锚点事件触发的元素
                const anchorGroup = group.addShape('circle', {
                    attrs: {
                        x,
                        y,
                        r: 11,
                        fill: '#000',
                        opacity: 0,
                    },
                    zIndex: 2,
                    nodeId: group.get('id'),
                    className: 'node-anchor-group',
                    draggable: true,
                    isAnchor: true,
                    index: i,
                });

                /**
                 * ! 添加锚点事件绑定
                 */
                anchorEvent(anchorGroup, group, p);

                group.anchorShapes.push(anchor);
                group.anchorShapes.push(anchorGroup);
            });

            // 查找所有锚点
            group.getAllAnchors = () => {
                return group.anchorShapes.filter(c => c.get('isAnchor') === true);
            };
            // 查找指定锚点
            group.getAnchor = (i) => {
                return group.anchorShapes.filter(c => c.get('className') === 'node-anchor' && c.get(
                    'index') === i);
            };
            // 查找所有锚点背景
            group.getAllAnchorBg = () => {
                return group.anchorShapes.filter(c => c.get('className') === 'node-anchor-bg');
            };
        },
        /* 添加文本节点 */
        /* https://g6.antv.vision/zh/docs/manual/advanced/keyconcept/shape-and-properties/#%E6%96%87%E6%9C%AC-text */
        addLabel(cfg, group, attrs) {
            const {
                label,
                labelCfg,
            } = attrs;
            if (attrs.hasOwnProperty('state') && attrs.state !== '') {
                labelCfg.style.fill = colorList[attrs.state].color
            }
            // const {
            //     maxlength
            // } = labelCfg;
            // //如果超出文本最大限制，截取文本，超出部分...
            // let text = maxlength ? label.substr(0, maxlength) : label || '';

            // if (label.length > maxlength) {
            //     text = `${text}...`;
            // }
            // console.log(text)
            group.addShape('text', {
                attrs: {
                    text: label,
                    // x: 20,
                    // y: 20,
                    x: (attrs.nodeType === 0 || attrs.nodeType === 1) === true ? 0 : -32,
                    y: (attrs.nodeType === 0 || attrs.nodeType === 1) === true ? 0 : 1,
                    ...labelCfg,
                    ...labelCfg.style,
                },
                className: 'node-text',
                draggable: true,
            });
        },
        /* 绘制节点，包含文本 */
        draw(cfg, group) {
            return this.drawShape(cfg, group);
        },
        /* 绘制节点，包含文本 */
        drawShape(cfg, group) { // 元素分组
            // 合并外部样式和默认样式
            const attrs = this.getShapeStyle(cfg, group);
            if (attrs.hasOwnProperty('state') && attrs.state !== '') {
                attrs.fill = colorList[attrs.state].fill
            }
            // 添加节点，视觉节点
            const shape = group.addShape(this.shapeType, { // shape 属性在定义时返回
                className: `${this.shapeType}-shape`,
                draggable: true,
                attrs,
            });
            // const v = group.get('children')[0];
            // const midPoint = v.getPoint(0.5);
            // // 将节点的选择范围扩大
            group.addShape(this.shapeType, { // shape 属性在定义时返回
                className: `${this.shapeType}-shape`,
                draggable: true,
                attrs: {
                    ...attrs,
                    opacity: 0,
                    lineWidth: 60,
                    stroke: 'blue',
                    cursor: 'pointer'
                }
            });

            // 按className查找元素
            group.getItem = className => {
                return group.get('children').find(item => item.get('className') === className);
            };
            // 添加文本节点
            this.addLabel(cfg, group, attrs);
            // 添加图标
            this.drawIcon(cfg, group, attrs);
            // 添加锚点
            if (!attrs.detail) {
                this.initAnchor(cfg, group);
            }
            //添加删除按钮
            this.initDeleteBtn(cfg, group)
            return shape;
        },
        /* 更新节点，包含文本 */
        update(cfg, node) {
            const model = node.get('model');
            // const group = node.get('group');
            const {
                attrs
            } = node.get('keyShape');
            const text = node.get('group').getItem('node-text');
            const item = node.get('group').get('children')[0];
            setTimeout(() => {
                // 更新文本内容
                text && text.attr({
                    text: model.label,
                    labelCfg: attrs.labelCfg,
                });
                // 更新节点属性
                item.attr({
                    ...attrs,
                    ...model.style
                });
            });
        },
        /* 设置节点的状态，主要是交互状态，业务状态请在 draw 方法中实现 */
        setState(name, value, item) {
            const buildInEvents = [
                'deleteBtnShow',
                'anchorShow',
                'nodeState',
                'nodeState:default',
                'nodeState:selected',
                'nodeState:hover',
                'nodeOnDragStart',
                'nodeOnDrag',
                'nodeOnDragEnd',
            ];
            const group = item.getContainer();

            if (group.get('destroyed')) return false;
            if (buildInEvents.includes(name)) {
                // 内部this绑定到了当前item实例
                itemEvents[name].call(this, value, group);
            }
            //  else if (this.stateApplying) {
            //     this.stateApplying.call(this, name, value, item);
            // } else {
            //     console.warn(`warning: ${name} 事件回调未注册!\n可继承该节点并通过 stateApplying 方法进行注册\n如已注册请忽略 (-_-!)`);
            // }
        },
        /* 获取锚点（相关边的连入点） */
        getAnchorPoints(cfg) {
            return cfg.anchorPoints || [
                [0.5, 0],
                [1, 0.5],
                [0.5, 1],
                [0, 0.5],
            ];
        },
    }, 'single-node');
};
