let dragLog = []; // 记录鼠标坐标

let anchorNodeId = null; // dragover 也会发生在拖拽的锚点上, 用于记录当前拖拽的节点id

export default (anchor, group, p) => {
    // 鼠标移入事件
    anchor.on('mouseenter', () => {
        // 可以传入多个键值对
        anchor.attr({
            cursor: 'crosshair',
        });
    });

    // 拖拽事件
    anchor.on('dragstart', e => {
        if (anchorNodeId == null) {
            const {
                type,
                direction
            } = group.getFirst().attr();
            const diff = type === 'triangle-node' ? (direction === 'up' ? 1 : 0) : 0.5;
            const bBox = group.get('item').getBBox();
            const id = group.get('item').get('id');
            const point = [
                bBox.width * (p[0] - 0.5), // x
                bBox.height * (p[1] - diff), // y
            ];

            dragLog = [e.x, e.y];

            // 添加线条
            const line = group.addShape('path', {
                attrs: {
                    stroke: '#1890FF',
                    lineDash: [5, 5],
                    path: [
                        ['M', ...point],
                        ['L', ...point],
                    ],
                },
                className: 'dashed-line',
                pointStart: point,
            });

            // 置于顶层
            group.toFront();
            line.toFront(); // 最后把这条线层级提升至最高
            anchorNodeId = id;
        }
    });
};
