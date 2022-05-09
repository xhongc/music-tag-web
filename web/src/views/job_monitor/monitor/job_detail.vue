<template>
    <div id="jobDetail" v-bkloading="{ isLoading: jobDetailLoading, zIndex: 10 }">
        <div class="box">
            <p class="title">基本信息</p>
            <bk-container>
                <bk-form :label-width="130">
                    <bk-row>
                        <bk-col :span="6">
                            <bk-form-item label="作业名称:">{{form.name}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="作业状态:">
                                <span v-if="form.state !== ''">{{stateList[stateList.findIndex(e => e.name === form.state)].label}}</span>
                            </bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="启动人:">{{form.executor}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="Agent:">{{form.station}}</bk-form-item>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="6">
                            <bk-form-item label="计划开始时间:">{{form.eta}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="实际开始时间:">{{form.start_time}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="完成时间:">{{form.end_time}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="总共耗时:">{{form.total_time}}</bk-form-item>
                        </bk-col>
                    </bk-row>
                </bk-form>
            </bk-container>
        </div>
        <div class="box">
            <p class="title">执行日志</p>
            <editor :height="'200px'" ref="editorLog" :codes="form.log" :read-only="true" :language="'shell'"></editor>
            <!--            <bk-input :type="'textarea'" :rows="10" ext-cls="custom-textarea" v-model="form.log" :disabled="true"></bk-input> -->
        </div>
        <div class="box">
            <p class="title">执行脚本</p>
            <editor :height="'200px'" ref="editorScript" :codes="form.script_content" :read-only="true" :language="'shell'"></editor>
            <!-- <bk-input :type="'textarea'" :rows="10" ext-cls="custom-textarea" v-model="form.script_content" :disabled="true"></bk-input> -->
        </div>
        <div class="box">
            <p class="title">前置命令检测</p>
            <editor :height="'200px'" ref="editorPrecommd" :read-only="true" :language="'json'"></editor>
        </div>
    </div>
</template>

<script>
    import editor from '@/components/monacoEditor'
    export default {
        components: {
            editor
        },
        data() {
            return {
                timer: null, // 轮询定时器
                jobDetailLoading: false,
                form: {
                    name: '', // 作业名称
                    state: '', // 状态
                    executor: '', // 启动人
                    station: '', // agent
                    eta: '', // 计划开始时间
                    start_time: '', // 实际开始时间
                    end_time: '', // 完成时间
                    total_time: '', // 总共耗时
                    log: '', // 执行日志
                    script_content: '', // 执行脚本
                    upstream_nodes: [], // 先行作业/作业流
                    downstream_nodes: [] // 后续作业/作业流
                },
                stateList: [{
                                id: 1,
                                name: 'wait',
                                label: '等待'
                            },
                            {
                                id: 2,
                                name: 'run',
                                label: '正在执行'
                            },
                            {
                                id: 3,
                                name: 'fail',
                                label: '失败'
                            },
                            {
                                id: 4,
                                name: 'error',
                                label: '错误'
                            },
                            {
                                id: 5,
                                name: 'success',
                                label: '成功'
                            },
                            {
                                id: 6,
                                name: 'pause',
                                label: '挂起'
                            },
                            {
                                id: 7,
                                name: 'stop',
                                label: '终止'
                            },
                            {
                                id: 8,
                                name: 'cancel',
                                label: '取消'
                            },
                            {
                                id: 9,
                                name: 'need_confirm',
                                label: '待复核'
                            },
                            {
                                id: 10,
                                name: 'ignore',
                                label: '忽略'
                            }
                ]
            }
        },
        created() {
            // 首屏刷新
            this.handleLoad(true)
            this.timer = setInterval(() => {
                // 轮询刷新，非首屏
                this.handleLoad(false)
            }, 10000)
        },
        beforeDestroy() {
            clearInterval(this.timer)
        },
        methods: {
            handleLoad(first = false) {
                if (first) {
                    this.jobDetailLoading = true
                }
                this.$api.nodeRun.retrieve(parseInt(this.$route.query.id)).then(res => {
                    if (res.result) {
                        this.form = res.data
                        if (this.form.hasOwnProperty('log')) {
                            this.$refs.editorLog.monacoEditor.setValue(this.form.log)
                        }
                        if (this.form.hasOwnProperty('script_content')) {
                            this.$refs.editorScript.monacoEditor.setValue(this.form.script_content)
                        }
                        if (this.form.hasOwnProperty('pre_commands')) {
                            this.$refs.editorPrecommd.monacoEditor.setValue(JSON.stringify(this.form.pre_commands))
                        }
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.jobDetailLoading = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobDetail {
        padding: 20px;

        .box {
            .title {
                margin-bottom: 12px;
                font-size: 14px;
                color: #63656E;
                font-weight: bold;
                height: 22px;
                line-height: 22px;
            }

            .customTable {
                /deep/ .bk-table-empty-block {
                    background-color: #fff;
                }
            }

            .custom-textarea {
                /deep/ textarea {
                    padding: 20px;
                    background-color: rgb(49, 50, 56) !important;
                    color: #C4C6CC !important;
                }
            }

            margin-bottom: 24px;
        }
    }
</style>
