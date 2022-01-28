<template>
    <div id="nodeInfo">
        <div class="content">
            <div class="box">
                <p class="title">基本信息</p>
                <div class="info">
                    <bk-form ref="form" :label-width="144">
                        <bk-form-item label="开始时间:">
                            <span>{{form.nodeData.eta}}</span>
                        </bk-form-item>
                        <bk-form-item label="执行前人工复核:">
                            <span v-if="form.nodeData.need_confirm === 0">无</span>
                            <span v-else-if="form.nodeData.need_confirm === 1">单人复核</span>
                            <span v-else-if="form.nodeData.need_confirm === 2">双人复核</span>
                        </bk-form-item>
                        <bk-form-item label="执行后自动暂停:">
                            <bk-switcher v-model="form.nodeData.is_book_pause" theme="primary" :disabled="disabled"></bk-switcher>
                        </bk-form-item>
                        <bk-form-item label="执行时长告警:">
                            <bk-compose-form-item>
                                <span>{{form.nodeData.alarm_policy.duration.period}}</span>
                                <span>{{getUnit1}}</span>
                                <span v-if="form.nodeData.alarm_policy.duration.period && getUnit1">产生告警</span>
                            </bk-compose-form-item>
                        </bk-form-item>
                        <bk-form-item label="执行时间点告警:">
                            <span style="margin-right: 12px;" v-if="form.nodeData.alarm_policy.time_point">时间点超过</span>
                            <span>{{form.nodeData.alarm_policy.time_point}}</span>
                            <span v-if="form.nodeData.alarm_policy.time_point">产生告警</span>
                        </bk-form-item>
                        <bk-form-item label="前置文件路径:">
                            <span>{{form.nodeData.file_dependence.file_path}}</span>
                        </bk-form-item>
                        <bk-form-item label="巡检次数:">
                            <span>{{form.nodeData.file_dependence.max_num}}</span>
                        </bk-form-item>
                        <bk-form-item label="巡检周期:">
                            <span>{{form.nodeData.file_dependence.cycle.value}}</span>
                            <span>{{getUnit2}}</span>
                        </bk-form-item>
                        <bk-form-item label="前置条件检测命令:">
                            <div v-for="(item, index) in form.nodeData.pre_commands" class="pre-commands" :key="index"
                                style="margin-bottom: 12px;">
                                <span>{{item.key}}</span>
                            </div>
                        </bk-form-item>
                        <bk-form-item label="状态:">{{statusList[statusList.findIndex(item => item.key === form.state)].label}}</bk-form-item>
                        <bk-form-item label="执行时间:">{{form.start_time}}</bk-form-item>
                        <bk-form-item label="结束时间:">{{form.end_time}}</bk-form-item>
                        <bk-form-item label="执行脚本:">
                            <editor :height="'200px'" ref="editor" :codes="form.script_content" :read-only="true" :language="'shell'"></editor>
                        </bk-form-item>
                        <bk-form-item label="执行日志:">{{form.log}}</bk-form-item>
                    </bk-form>
                </div>
            </div>
            <!--            <div class="box">
                <p class="title">输出参数</p>
                <bk-table :data="tableList">
                    <bk-table-column label="名称" prop="name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="KEY" prop="key" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="引用">
                        <template slot-scope="props">
                            <bk-checkbox :disabled="disabled">
                            </bk-checkbox>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div> -->
        </div>
    </div>
</template>

<script>
    import editor from '@/components/monacoEditor'
    import statusList from './statusList.js'
    export default {
        components: {
            editor
        },
        props: {
            nodeData: {
                type: Object,
                default: () => {}
            }
        },
        data() {
            return {
                statusList: statusList,
                disabled: true,
                controlType: '', // 当前调度方式值
                tableList: [{ // 输出参数表格
                                name: '执行结果',
                                key: '_result',
                                reference: '1'
                            },
                            {
                                name: '作业输出变量',
                                key: '_log_outputs',
                                reference: '2'
                            }
                ],
                reviewList: [{ // 执行前人工复核单选列表
                    label: '无',
                    value: 0
                }, {
                    label: '单人复核',
                    value: 1
                }, {
                    label: '双人复核',
                    value: 2
                }],
                timeTypeList: [{ // 执行时长告警时间类型下拉列表
                                   value: 'hours',
                                   label: '时'
                               },
                               {
                                   value: 'minutes',
                                   label: '分'

                               },
                               {
                                   value: 'seconds',
                                   label: '秒'
                               }
                ],
                form: {
                    nodeData: {
                        alarm_policy: { // 告警策略
                            duration: {
                                period: '', // 执行XXX时长告警
                                unit: '' // 执行XXX时长告警类型
                            },
                            time_point: '' // 执行时间点超过XXX产生告警
                        },
                        eta: '', // 开始时间，
                        is_book_pause: false, // 执行后自动暂停
                        need_confirm: '', // 执行前人工复核
                        pre_commands: [{ // 命令前置依赖检测
                            key: '',
                            value: ''
                        }]
                    }
                },
                log: '', // 执行日志
                state: '', // 状态
                start_time: '', // 执行时间
                end_time: '', // 结束时间
                script_content: '' // 执行脚本
            }
        },
        computed: {
            getUnit1() {
                const item = this.timeTypeList.find(item => item.value === this.form.nodeData.alarm_policy.duration.unit)
                if (item) {
                    return item.label
                } else {
                    return ''
                }
            },
            getUnit2() {
                const item = this.timeTypeList.find(item => item.value === this.form.nodeData.file_dependence.cycle.type)
                if (item) {
                    return item.label
                } else {
                    return ''
                }
            }
        },
        created() {
            this.form.nodeData = this.nodeData.data
            if (!Object.keys(this.form.nodeData.file_dependence).length) {
                this.form.nodeData.file_dependence = {
                    file_path: '', // 前置文件路径
                    max_num: '', // 巡检次数
                    cycle: { // 巡检周期
                        type: '', // 时间类型
                        value: '' // 时间值
                    }
                }
            }
            this.form.log = this.nodeData.log
            this.form.state = this.nodeData.state
            this.form.start_time = this.nodeData.start_time
            this.form.end_time = this.nodeData.end_time
            this.form.script_content = this.nodeData.script_content
            if (this.form.nodeData.pre_commands.length === 0) {
                this.form.pre_commands = [{ // 命令前置依赖检测
                    key: '',
                    value: ''
                }]
            }
        }
    }
</script>

<style lang="scss" scoped>
    #nodeInfo {
        height: 100%;

        .content {
            padding: 16px 20px 0 16px;
            height: 100%;
            overflow: auto;

            .box {
                margin-bottom: 14px;

                .title {
                    font-size: 14px;
                    height: 22px;
                    line-height: 22px;
                    color: #313238;
                    font-weight: bold;
                    margin-bottom: 16px;
                }

                .info {
                    .pre-commands {
                        display: flex;

                        i {
                            font-size: 32px;
                            color: #979BA5;
                            width: 32px;
                            text-align: center;
                            height: 32px;
                            line-height: 32px;
                            cursor: pointer;
                        }
                    }

                    .custom-textarea {
                        /deep/ textarea {
                            padding: 20px;
                            background-color: rgb(49, 50, 56) !important;
                            color: #C4C6CC !important;
                        }
                    }
                }
            }
        }
    }
</style>
