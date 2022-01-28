import selectNode from './select-node'; // 选中节点行为
import activeEdge from './active-edge'; // 激活边
import hoverNode from './hover-node'; // hover节点
// import dragNode from './drag-node'; // 拖拽节点
import hoverEdge from './hover-edge'

export default G6 => {
    selectNode(G6);
    activeEdge(G6);
    hoverEdge(G6);
    hoverNode(G6);
    // dragNode(G6);
};
