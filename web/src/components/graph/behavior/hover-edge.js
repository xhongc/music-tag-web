export default G6 => {
    //注册自定义行为，鼠标悬浮节点
    G6.registerBehavior('hover-edge', {
        getEvents() {
            return {
                'edge:mouseenter': 'onEdgeEnter',
                'edge:mouseleave': 'onEdgeLeave'
            }
        },
        onEdgeEnter(e) {
            const model = e.item.get('model')
            const sourceNode = e.item.getSource().get('model')
            //将元素置为顶层
            e.item.toFront()
            e.item.setState('edgeState:hover', true)
            // 非详情状态下显示当前连线的删除按钮以及编辑按钮
            if (!model.detail) {
                e.item.setState('deleteEdge', true); // 二值状态
                // e.item.setState('editEdge', true); // 二值状态
                //若当前线的起始节点为作业流节点，不显示编辑按钮
                if (sourceNode.nodeType !== 3 && sourceNode.nodeType !== 0) {
                    e.item.setState('editEdge', true); // 二值状态
                }
            }
        },
        onEdgeLeave(e) {
            const model = e.item.get('model')
            const sourceNode = e.item.getSource().get('model')
            e.item.setState('edgeState:hover', false)
            // 将当前连线的删除按钮以及编辑按钮隐藏
            if (!model.detail) {
                e.item.setState('deleteEdge', false); // 二值状态
                // e.item.setState('editEdge', false); // 二值状态
                //若当前线的起始节点为作业流节点，不显示编辑按钮
                if (sourceNode.nodeType !== 3 || sourceNode.nodeType !== 0) {
                    e.item.setState('editEdge', false); // 二值状态
                }
            }
        }
    })
}
