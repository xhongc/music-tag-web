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
    'edgeState:hover'(value, group) {
        const path = group.getChildByIndex(0);
        const {
            endArrow,
            startArrow
        } = path.get('attrs');
        const {
            activeStyle,
            defaultStyle,
            originStyle
        } = getItemStyle.call(this, 'edge', group, 'hover');

        if (!activeStyle) return;
        if (value) {
            setStyle(path, {
                stroke: '#3a84ff',
            });
            path.attr('endArrow', {
                path: endArrow.path,
                fill: '#3a84ff',
                stroke: '#3a84ff'
            });
        } else {
            setStyle(path, {
                stroke: '#aab7c3'
            });
            path.attr('endArrow', {
                path: endArrow.path,
                fill: '#aab7c3',
                stroke: '#aab7c3',
            });
        }
    },
    deleteEdge: function(value, group) {
        if (value) {
            group.showDeleteEdgeBtn(group);
        } else {
            group.clearDeleteEdgeBtn(group);
        }
    },
    editEdge: function(value, group) {
        if (value) {
            group.showEditEdgeBtn(group);
        } else {
            group.clearEditEdgeBtn(group);
        }
    }
}

export default events;
