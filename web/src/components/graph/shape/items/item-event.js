// import defaultStyles from '../defaultStyles';

/**
 * @description 恢复节点/边/锚点默认样式
 */
function setStyle(item, nodeStyle, text, textStyle) {
    item.attr(nodeStyle);
    if (text) {
        text.attr(textStyle);
    }
}

function getItemStyle(type, group, state = 'hover') {
    const item = group.get('item');
    const attrs = group.getFirst().attr();
    const originStyle = type === 'node' ? item.get('originStyle') : item.get('originStyle')['edge-shape'];
    const activeStyle = attrs[`${type}State:${state}`];
    const defaultStyle = attrs[`${type}State:default`];
    if (type === 'edge' && defaultStyle && defaultStyle.lineWidth == null) {
        defaultStyle.lineWidth = 1;
    }

    return {
        activeStyle,
        defaultStyle,
        originStyle,
    };
}

const events = {
    /**
     * @description 锚点事件
     * 显示/隐藏锚点
     */
    anchorShow(value, group) {
        // 锚点全局开关
        // changeData 时由于实例没销毁, 这里需要处理异常
        if (group.get('children')) {
            const {
                anchorControls
            } = group.get('children')[0].cfg.attrs;

            if (anchorControls && anchorControls.hide) return false;
        }

        if (value) {
            group.showAnchor(group);
        } else {
            group.clearAnchor(group);
        }
    },
    /**
     * @description 节点删除按钮事件
     * 显示/隐藏节点删除按钮
     */
    deleteBtnShow(value, group) {
        // 删除按钮全局开关
        // changeData 时由于实例没销毁, 这里需要处理异常
        if (group.get('children')) {
            const {
                nodeDeleteBtn
            } = group.get('children')[0].cfg.attrs;

            if (nodeDeleteBtn && nodeDeleteBtn.hide) return false;
        }

        if (value) {
            group.showDeleteBtn(group)
        } else {
            group.clearDeleteBtn(group)
        }
    },
    /**
     * @description 边多状态事件
     */
    nodeState(value, group) {
        events[`nodeState:${value}`] && events[`nodeState:${value}`].call(this, value, group);
    },

    /**
     * @description 节点恢复默认状态事件
     */
    'nodeState:default'(value, group) {
        if (value) {
            const node = group.getChildByIndex(0);
            const text = group.getChildByIndex(1);
            const {
                defaultStyle
            } = getItemStyle.call(this, 'node', group);

            if (!defaultStyle) return;
            const textStyle = defaultStyle.labelCfg && defaultStyle.labelCfg.style ? defaultStyle.labelCfg.style : {};

            setStyle(node, defaultStyle, text, textStyle);
        }
    },

    /**
     * @description 节点selected事件
     */
    'nodeState:selected'(value, group) {
        const node = group.getChildByIndex(0);
        const text = group.getChildByIndex(1);
        const {
            activeStyle,
            defaultStyle
        } = getItemStyle.call(this, 'node', group, 'selected');
        if (!activeStyle) return;
        if (value) {
            const textStyle = activeStyle.labelCfg && activeStyle.labelCfg.style ? activeStyle.labelCfg.style : {};
            setStyle(node, activeStyle, text, textStyle);
        } else {
            const textStyle = defaultStyle.labelCfg && defaultStyle.labelCfg.style ? defaultStyle.labelCfg.style : {};

            setStyle(node, defaultStyle, text, textStyle);
        }
    },

    /**
     * @description 节点hover事件
     */
    'nodeState:hover'(value, group) {
        const node = group.getChildByIndex(0);
        const {
            activeStyle,
            defaultStyle
        } = getItemStyle.call(this, 'node', group, 'hover');
        if (!activeStyle) return;
        if (value) {
            setStyle(node, {
                cursor: 'pointer',
                shadowColor: '#ccc',
                shadowBlur: 10
            });
        } else {
            setStyle(node, {
                shadowColor: '#000',
                shadowBlur: 0
            });
        }
    },
};

export default events;
