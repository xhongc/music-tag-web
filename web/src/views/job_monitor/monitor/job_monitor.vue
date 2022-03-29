<template>
    <div id="jobMonitor">
        <bk-tab :active.sync="$store.state.monitor.tabActive" type="card" @tab-change="handleTabChange">
            <bk-tab-panel v-for="(panel, index) in panels" v-bind="panel" :key="index">
                <router-view v-if="panel.name === $store.state.monitor.tabActive"></router-view>
            </bk-tab-panel>
        </bk-tab>
        <div style="height: 20px;"></div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                panels: [
                    {
                        name: 'jobflowview',
                        label: '作业流视图'
                    }
                ]
            }
        },
        created() {
            if (this.$route.name === 'JobView') {
                this.$store.commit('changeTabActive', 'jobview')
            }
        },
        methods: {
            // 点击tab切换不需要传参数
            handleTabChange(name) {
                this.$store.commit('changeTabActive', name)
                this.$store.commit('getJobFlowViewSearch', {})
                this.$store.commit('getJobViewSearch', {})
                this.$router.push({
                    path: `/${name}`
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobMonitor {
        padding: 20px 20px 0 20px;
        height: 100%;

        /deep/ .bk-tab-section {
            background-color: #fff;
        }
    }
</style>
