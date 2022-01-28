export default G6 => {
    //注册自定义行为，鼠标悬浮节点
    G6.registerBehavior('hover-node', {
        getEvents() {
            return {
                'node:mouseenter': 'onNodeEnter',
                'node:mouseleave': 'onNodeLeave',
            }
        },
        onNodeEnter(e) {
            // 显示当前节点的锚点
            e.item.setState('nodeState:hover', true)
            if (!e.item.get('model').detail) {
                e.item.setState('anchorShow', true); // 二值状态
                // 开始节点和结束节点不做处理
                if(e.item.get('model').nodeType === 0 || e.item.get('model').nodeType === 1) {
                    return false
                }
                e.item.setState('deleteBtnShow', true); // 二值状态
            }
        },
        onNodeLeave(e) {
            // 将锚点再次隐藏
            e.item.setState('nodeState:hover', false)
            if (!e.item.get('model').detail) {
                e.item.setState('anchorShow', false); // 二值状态
                // 开始节点和结束节点不做处理
                if(e.item.get('model').nodeType === 0 || e.item.get('model').nodeType === 1) {
                    return false
                }
                e.item.setState('deleteBtnShow', false); // 二值状态
            }
        },
    })
}
