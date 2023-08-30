const common = {
    state: {
        defaultTableHeight: 800,
        userRole: '',
        fullPath: '',
        hasMsg: false
    },
    mutations: {
        setDefaultTableHeight: (state, val) => {
            state.defaultTableHeight = val
        },
        setUserRole: (state, val) => {
            state.userRole = val
        },
        setFullPath: (state, val) => {
            state.fullPath = val
        },
        setHasMsg: (state, val) => {
            state.hasMsg = val
        }
    }
}

export default common
