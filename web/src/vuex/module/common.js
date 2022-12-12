const common = {
    state: {
        defaultTableHeight: 800,
        userRole: ''
    },
    mutations: {
        setDefaultTableHeight: (state, val) => {
            state.defaultTableHeight = val
        },
        setUserRole: (state, val) => {
            state.userRole = val
        }
    }
}

export default common
