<template>
    <div id="report">
        <bk-tab :active.sync="tabActive" type="card" ext-cls="custom-tab">
            <bk-tab-panel v-for="(panel, index) in panels" v-bind="panel" :key="index">
            </bk-tab-panel>
        </bk-tab>
        <div class="section">
            <div class="report-content">
                <jobFlowViewReport v-if="tabActive === 'jobflowviewreport'" :run-sys-list="runSysList"></jobFlowViewReport>
                <jobViewReport v-else-if="tabActive === 'jobviewreport'" :run-sys-list="runSysList"></jobViewReport>
            </div>
        </div>
        <div style="height: 20px;"></div>
    </div>
</template>

<script>
    import jobFlowViewReport from './job_flow_view_report.vue'
    import jobViewReport from './job_view_report.vue'
    export default {
        components: {
            jobFlowViewReport,
            jobViewReport
        },
        data() {
            return {
                runSysList: [],
                tabActive: 'jobflowviewreport',
                panels: [
                    {
                        name: 'jobflowviewreport',
                        label: '作业流视图'
                    },
                    {
                        name: 'jobviewreport',
                        label: '作业视图'
                    }
                ]
            }
        },
        created() {
            this.getRunSysList()
        },
        methods: {
            // 处理生成报表
            handleCreateReport() {
                console.log('生成报表分析')
            },
            // 获取跑批系统
            getRunSysList() {
                this.runSysList = []
            }
        }
    }
</script>

<style lang="scss" scoped>
    #report {
        padding: 20px 20px 0 20px;
        height: 100%;
        .custom-tab {
            /deep/ .bk-tab-section {
                display: none;
            }
        }

        .section {
            padding: 20px 24px;
            // padding: 20px 24px 0px 24px;
            background-color: #fff;
            border: 1px solid #dcdee5;
            border-top: 0;
            // height: calc(100% - 42px);
        }
    }
</style>
