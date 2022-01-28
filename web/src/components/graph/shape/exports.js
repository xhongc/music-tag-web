import registerBaseNode from './items/base-node';
import registerNode from './node';

export default (G6) => {
    // 先注册基础节点, 之后自定义节点基于基础节点继承
    registerBaseNode(G6);
    registerNode(G6);
};
