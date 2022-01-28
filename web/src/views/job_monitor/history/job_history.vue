<template>
    <div id="jobHistory">
        <bk-tab :active.sync="$store.state.history.tabActive" type="card" @tab-change="handleTabChange">
            <bk-tab-panel v-for="(panel, index) in panels" v-bind="panel" :key="index">
                <router-view v-if="panel.name === $store.state.history.tabActive"></router-view>
            </bk-tab-panel>
        </bk-tab>
        <div style="height: 20px;"></div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                panels: [{
                             name: 'jobflowviewhistory',
                             label: '作业流视图'
                         },
                         {
                             name: 'jobviewhistory',
                             label: '作业视图'
                         }
                ]
            }
        },
        created() {
            if (this.$route.name === 'JobViewHistory') {
                this.$store.commit('changeTabActive', 'jobviewhistory')
            }
        },
        methods: {
            handleTabChange(name) {
                this.$store.commit('changeTabActive', name)
                this.$store.commit('getJobFlowHistorySearch', {})
                this.$store.commit('getJobHistorySearch', {})
                this.$router.push({
                    path: `/${name}`
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobHistory {
        padding: 20px 20px 0 20px;
        height: 100%;

        /deep/ .bk-tab-section {
            background-color: #fff;
        }
    }
</style>
