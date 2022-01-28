import {
    setStore,
    getStore
} from '@/common/store'

const history = {
    state: {
        tabActive: 'jobflowviewhistory', // 默认tab为作业流视图
        jobFlowHistorySearchForm: getStore({ name: 'jobFlowHistorySearchForm' }) || {}, // 作业监视，作业流视图搜索缓存
        jobHistorySearchForm: getStore({ name: 'jobHistorySearchForm' }) || {} // 作业监视，作业视图搜索缓存
    },
    action: {},
    mutations: {
        changeTabActive: (state, data) => {
            state.tabActive = data
        },
        getJobFlowHistorySearch: (state, data) => {
            state.jobFlowHistorySearchForm = data
            setStore({
                name: 'jobFlowHistorySearchForm',
                content: state.jobFlowHistorySearchForm
            })
        },
        getJobHistorySearch: (state, data) => {
            state.jobHistorySearchForm = data
            setStore({
                name: 'jobHistorySearchForm',
                content: state.jobHistorySearchForm
            })
        }
    }
}

export default history
