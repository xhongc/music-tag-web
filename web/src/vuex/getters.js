const getters = {
    jobFlowViewSearchForm: state => state.monitor.jobFlowViewSearchForm, // 作业监视，作业流视图搜索缓存
    jobViewSearchForm: state => state.monitor.jobViewSearchForm, // 作业监视，作业流视图搜索缓存
    jobFlowHistorySearchForm: state => state.history.jobFlowHistorySearchForm, // 作业历史，作业流视图搜索缓存
    jobHistorySearchForm: state => state.history.jobHistorySearchForm, // 作业历史，作业流视图搜索缓存
    btnPermission: state => state.permission.btnPermission // 按钮权限
}
export default getters
