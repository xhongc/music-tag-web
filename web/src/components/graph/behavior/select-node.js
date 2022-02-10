// 点选项目
export default G6 => {
    G6.registerBehavior('select-node', {
        // 默认配置
        getDefaultCfg() {
            return {
                // 多选
                multiple: false,
            };
        },
        // 事件映射
        getEvents() {
            return {
                'node:click': 'onNodeClick',
                'canvas:click': 'onCanvasClick',
            };
        },
        // 点击事件
        onNodeClick(e) {
            const model = e.item.get('model');
            // 点击的部分含有可删除标识，表明此时进行的是删除操作
            if(e.target.attr().hasOwnProperty('nodeDeleteBtn')) {
                this.graph.emit('before-delete-node', e)
                return
            }
            //开始节点,结束节点, 作业流节点不做处理
            if (model.nodeType === 0 || model.nodeType === 1) {
                return
            }
            //先将所有当前是 click 状态的节点/edge 置为非 selected 状态
            this._clearSelected();
            e.item.toFront();
            // 获取被点击的节点元素对象, 设置当前节点的 click 状态为 selected
            e.item.setState('nodeState', 'selected');
            // 将点击事件发送给 graph 实例
            this.graph.emit('after-node-selected', e);
        },
        onCanvasClick(e) {
            this._clearSelected();
        },
        // 清空已选
        _clearSelected() {
            const selectedNodes = this.graph.findAllByState('node', 'nodeState:selected');

            selectedNodes.forEach(node => {
                node.clearStates(['nodeState:selected', 'nodeState:hover']);
            });

            // const selectedEdges = this.graph.findAllByState('edge', 'edgeState:selected');

            // selectedEdges.forEach(edge => {
            //     edge.clearStates(['edgeState:selected', 'edgeState:hover']);
            // });
            // this.graph.emit('after-node-selected');
        },
    });
};
