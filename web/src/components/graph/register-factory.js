import shape from './shape/exports';
import behavior from './behavior/exports';
import registerEdges from './shape/edges/base-edge';

export default (G6) => {
    //注册图形
    shape(G6);
    //注册行为
    behavior(G6);
    // 注册边
    registerEdges(G6);
};
