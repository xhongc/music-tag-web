import {
    setStore,
    getStore
} from '@/common/store'

const monitor = {
    state: {
        tabActive: 'jobflowview', // 默认tab为作业流视图
        jobFlowViewSearchForm: getStore({ name: 'jobFlowViewSearchForm' }) || {}, // 作业监视，作业流视图搜索缓存
        jobViewSearchForm: getStore({ name: 'jobViewSearchForm' }) || {} // 作业监视，作业视图搜索缓存
    },
    action: {},
    mutations: {
        changeTabActive: (state, data) => {
            state.tabActive = data
        },
        getJobFlowViewSearch: (state, data) => {
            state.jobFlowViewSearchForm = data
            setStore({
                name: 'jobFlowViewSearchForm',
                content: state.jobFlowViewSearchForm
            })
        },
        getJobViewSearch: (state, data) => {
            state.jobViewSearchForm = data
            setStore({
                name: 'jobViewSearchForm',
                content: state.jobViewSearchForm
            })
        }
    }
}

export default monitor
