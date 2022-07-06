// 给action注册事件处理函数 当函数被触发的时候，将该状态提交到mutations中处理好多
export function modifyAName({commit}, name) {
    return commit('modifyName', name)
}
