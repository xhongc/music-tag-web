<template>
    <div id="nodeInfo">
        <div class="content">
            <div class="box">
                <p class="title">基本信息</p>
                <div class="info">
                    <bk-form ref="form" :label-width="144" :model="form">
                        <bk-form-item label="节点名称:" :required="true" :error-display-type="'normal'" :property="'node_name'">
                            <bk-input v-model="form.node_name" type="text" style="width: 350px;margin-right: 9px;" :disabled="disabled"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="运行标志:" :required="true" :error-display-type="'normal'" :property="'run_mark'">
                            <bk-radio-group v-model="form.run_mark">
                                <bk-radio :value="item.value" v-for="(item, index) in reviewList" :key="index" style="margin-right: 24px;"
                                    :disabled="disabled">
                                    {{item.label}}
                                </bk-radio>
                            </bk-radio-group>
                        </bk-form-item>
                        <bk-form-item label="描述:">
                            <bk-input v-model="form.description" type="textarea" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="失败重试次数:" :required="true" :error-display-type="'normal'" :property="'fail_retry_count'">
                            <bk-input v-model="form.fail_retry_count" type="number" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="失败重试间隔:">
                            <bk-compose-form-item>
                                <bk-input v-model="form.fail_offset" type="number" style="width: 139px;margin-right: 9px;"
                                    :disabled="disabled" :min="0"></bk-input>
                                <bk-select :clearable="true" style="background-color: #fff;width: 138px;margin-right: 14px;"
                                    v-model="form.fail_offset_unit" placeholder="请选择" :disabled="disabled">
                                    <bk-option v-for="(item, index) in timeTypeList" :key="index" :id="item.value"
                                        :name="item.label">
                                    </bk-option>
                                </bk-select>
                                <span>产生重试</span>
                            </bk-compose-form-item>
                        </bk-form-item>
                        <bk-form-item label="忽略失败:">
                            <bk-switcher v-model="form.is_skip_fail" :disabled="disabled"></bk-switcher>
                        </bk-form-item>
                        <bk-form-item label="超时告警:">
                            <bk-switcher v-model="form.is_timeout_alarm" :disabled="disabled"></bk-switcher>
                        </bk-form-item>
                        <bk-divider style="width: 540px;position: relative;right: 20px;border-color: #dcdee5;"></bk-divider>
                        <p class="title">输入参数</p>
                        <bk-form-item label="请求地址:">
                            <bk-input v-model="form.inputs.url" type="textarea" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="请求类型:">
                            <bk-select :clearable="true" style="background-color: #fff;width: 130px;margin-right: 14px;" v-model="form.inputs.method" placeholder="请选择" :disabled="disabled">
                                <bk-option v-for="(item, index) in requestTypeList" :key="index" :id="item.value" :name="item.label">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item label="Header:">
                            <div v-for="(item, index) in form.inputs.header" class="pre-commands" :key="index" style="margin-bottom: 12px;">
                                <bk-compose-form-item>
                                    <bk-input v-model="item.key" type="text" style="width: 130px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                                    <bk-input v-model="item.value" type="text" style="width: 130px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                                </bk-compose-form-item>
                                <i class="iconfont icon-changyongtubiao-chahao btn" style="margin-left: 8px;" @click="handleDeleteCommand(index)"
                                    v-if="!disabled && form.inputs.header.length > 1"></i>
                                <i class="iconfont icon-changyongtubiao-jiahao btn" @click="handleAddCommand" v-if="!disabled"></i>
                            </div>
                        </bk-form-item>
                        <bk-form-item label="Body:">
                            <bk-input v-model="form.inputs.body" type="textarea" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="超时时间:">
                            <bk-input v-model="form.inputs.timeout" type="number" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                        </bk-form-item>
                        <bk-divider style="width: 540px;position: relative;right: 20px;border-color: #dcdee5;"></bk-divider>
                        <p class="title">输出结果</p>
                        <bk-form-item label="输出日志:">
                            <editor :height="'200px'" ref="editor" :codes="form.outputs" :read-only="true" :language="'shell'"></editor>
                        </bk-form-item>
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
    import statusList from './statusList.js'
    import editor from '@/components/monacoEditor'

    export default {
        components: {
            editor
        },
        // props: ['nodeData'],
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
                timeTypeList: [
                    { // 执行时长告警时间类型下拉列表
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
                requestTypeList: [
                    {
                        value: 'get',
                        label: 'GET'
                    },
                    {
                        value: 'post',
                        label: 'POST'

                    },
                    {
                        value: 'put',
                        label: 'PUT'
                    },
                    {
                        value: 'head',
                        label: 'HEAD'
                    },
                    {
                        value: 'delete',
                        label: 'DELETE'
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
                const item = this.timeTypeList1.find(item => item.value === this.form.nodeData.alarm_policy.duration.unit)
                if (item) {
                    return item.label
                } else {
                    return ''
                }
            },
            getUnit2() {
                const item = this.timeTypeList1.find(item => item.value === this.form.nodeData.file_dependence.cycle.type)
                if (item) {
                    return item.label
                } else {
                    return ''
                }
            }
        },
        created() {
            this.form = this.nodeData.data
            this.form.state = this.nodeData.state
            this.form.start_time = this.nodeData.start_time
            this.form.end_time = this.nodeData.end_time
            this.form.script_content = this.nodeData.script_content
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
