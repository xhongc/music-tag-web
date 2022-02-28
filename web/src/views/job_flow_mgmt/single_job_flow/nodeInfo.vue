<template>
    <div id="nodeInfo">
        <div class="content">
            <div class="box">
                <p class="title">节点设置</p>
                <div class="info">
                    <bk-form ref="form" :label-width="144" :rules="rules" :model="form">
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
                        <bk-form-item v-for="(item,index) in form.inputs_component" :label="item.label" :key="index">
                            <div v-if="item.type === 'textarea'">
                                <bk-input v-model="form.inputs[item.key]" type="textarea" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                            </div>
                            <div v-else-if="item.type === 'select'">
                                <bk-select :clearable="true" style="background-color: #fff;width: 130px;margin-right: 14px;" v-model="form.inputs[item.key]" placeholder="请选择" :disabled="disabled">
                                    <bk-option v-for="(item2, index2) in item.choices || []" :key="index2" :id="item2.value" :name="item2.label">
                                    </bk-option>
                                </bk-select>
                            </div>
                            <div v-else-if="item.type === 'dict_map'">
                                <div v-for="(item3, index3) in form.inputs[item.key]" class="pre-commands" :key="index3" style="margin-bottom: 12px;">
                                    <bk-compose-form-item>
                                        <bk-input v-model="item3.key" type="text" style="width: 130px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                                        <bk-input v-model="item3.value" type="text" style="width: 130px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                                    </bk-compose-form-item>
                                    <i class="iconfont icon-changyongtubiao-chahao btn" style="margin-left: 8px;" @click="handleDeleteCommand(index3)"
                                        v-if="!disabled && form.inputs[item.key].length > 1"></i>
                                    <i class="iconfont icon-changyongtubiao-jiahao btn" @click="handleAddCommand" v-if="!disabled"></i>
                                </div>
                            </div>
                            <div v-else-if="item.type === 'number'">
                                <bk-input v-model="form.inputs[item.key]" type="number" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                            </div>
                            <div v-else-if="item.type === 'text'">
                                <bk-input v-model="form.inputs[item.key]" type="text" style="width: 350px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                            </div>
                            <div v-else>
                                <div style="color: red">ERROR:不支持的类型</div>
                            </div>
                        </bk-form-item>
                        <bk-divider style="width: 540px;position: relative;right: 20px;border-color: #dcdee5;"></bk-divider>
                    </bk-form>
                </div>
            </div>
            <div class="box">
                <p class="title">输出参数</p>
                <bk-table :data="tableList">
                    <bk-table-column label="名称" prop="name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="KEY" prop="key" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="引用">
                        <template>
                            <bk-checkbox :disabled="disabled">
                            </bk-checkbox>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>

        </div>
        <div class="footer" v-if="!disabled">
            <bk-button theme="primary" @click="handleConfim" style="margin-right: 8px;" :loading="isChecking">确定</bk-button>
            <bk-button @click="handleCancel">保存为模板</bk-button>
        </div>
    </div>
</template>

<script>
    export default {
        // props: ['nodeData'],
        props: {
            nodeData: {
                type: Object,
                default: {}
            }
        },
        inject: ['father_this'],
        data() {
            return {
                disabled: false,
                isChecking: false,
                rules: {
                    node_name: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        }
                    ],
                    fail_retry_count: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        }
                    ]
                },
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
                    label: '正常运行',
                    value: 0
                }, {
                    label: '禁止运行',
                    value: 1
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
                checkPointTypeList: [
                    {
                        value: 'status_code',
                        label: '默认响应码'
                    },
                    {
                        value: 'code',
                        label: '自定义响应码'
                    },
                    {
                        value: 'content',
                        label: '返回内容'
                    }
                ],
                checkPointConditionList: [
                    {
                        value: 'equal',
                        label: '等于'
                    },
                    {
                        value: 'not_equal',
                        label: '不等于'
                    },
                    {
                        value: 'contain',
                        label: '包含'
                    },
                    {
                        value: 'not_contain',
                        label: '不包含'
                    }
                ],
                form: {
                    inputs: {
                        url: '',
                        method: '',
                        header: [
                            {
                                key: '',
                                value: ''
                            }],
                        body: '',
                        timeout: '',
                        check_point: {
                            key: '',
                            condition: '',
                            values: ''
                        }
                    },
                    node_name: '',
                    run_mark: 0,
                    description: '',
                    fail_retry_count: 0,
                    fail_offset: '',
                    fail_offset_unit: 'seconds',
                    is_skip_fail: false,
                    is_timeout_alarm: false
                }
            }
        },
        created() {
            console.log('222', this.nodeData)
            this.form = this.nodeData.data
            this.form.inputs = JSON.parse(this.form.inputs)
            this.form.inputs_component = JSON.parse(this.form.inputs_component)
            this.controlType = this.father_this.controlType
            if (this.$route.query.type === 'detail') {
                this.disabled = true
            }
        },
        methods: {
            handleEtaChange(e) {
                this.form.eta = e
            },
            handleTimePointChange(e) {
                // this.form.inputs.time_point = e
            },
            // 处理确定
            handleConfim() {
                this.isChecking = true
                this.$refs.form.validate().then(validator => {
                    this.isChecking = false
                    this.$emit('update-node-data', this.form, this.nodeData.id)
                    this.$cwMessage('保存成功！', 'success')
                    this.$emit('node-drawer-close', true)
                }, validator => {
                    this.isChecking = false
                    // alert(`${validator.field}：${validator.content}`)
                })
            },
            // 处理取消
            handleCancel() {
                this.isChecking = true
                this.$refs.form.validate().then(validator => {
                    this.isChecking = false
                    this.$emit('update-node-data', this.form, this.nodeData.id)
                    this.form['name'] = this.form['node_name']
                    this.form['component_code'] = 'http_request'
                    this.$api.content.create(this.form).then(res => {
                        if (res.result) {
                            this.$cwMessage('保存成功！', 'success')
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                    })
                    this.$emit('node-drawer-close', true)
                }, validator => {
                    this.isChecking = false
                    // alert(`${validator.field}：${validator.content}`)
                })
            },
            // 处理删除前置条件检测命令
            handleDeleteCommand(index) {
                this.form.inputs.header.splice(index, 1)
            },
            // 处理添加前置条件检测命令
            handleAddCommand() {
                this.form.inputs.header.push({
                    key: '',
                    value: ''
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #nodeInfo {
        height: 100%;

        .content {
            padding: 16px 20px 0 16px;
            height: calc(100% - 54px);
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

                            &:active {
                                color: rgb(58,132,255);
                            }
                        }

                    }
                }
            }
        }

        .footer {
            border-top: 1px solid #DCDEE5;
            height: 54px;
            line-height: 54px;
            font-size: 0;
            background: #FAFBFD;
            padding-left: 16px;
        }
    }
</style>
