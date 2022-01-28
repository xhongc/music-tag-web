export default G6 => {
    G6.registerBehavior('active-edge', {
        getEvents() {
            return {
                'edge:click': 'onEdgeClick',
            };
        },
        onEdgeClick(e) {
            // 详情状态下，且该线条为分支，点击label打开分支连线的信息
            if(e.item.get('model').label && e.item.get('model').detail) {
                this.graph.emit('before-open-edge', e);
            }
            // // 将点击事件发送给 graph 实例
            if (!e.item.get('model').detail) {
                //点击删除按钮
                if(e.target.attr().hasOwnProperty('edgeDeleteBtn')) {
                    this.graph.emit('before-delete-edge', e);
                }
                //点击编辑按钮
                if(e.target.attr().hasOwnProperty('editEdgeBtn')) {
                    this.graph.emit('before-edit-edge', e);
                }
            }
        }
    })
}
