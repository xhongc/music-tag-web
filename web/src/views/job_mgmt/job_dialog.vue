<template>
    <div id="jobDialog">
        <bk-form ref="form" :label-width="144" :model="form">
            <bk-form-item label="节点名称:" :required="true" :error-display-type="'normal'" :property="'node_name'">
                <bk-input v-model="form.name" type="text" style="width: 350px;margin-right: 9px;" :disabled="disabled"></bk-input>
            </bk-form-item>
            <bk-form-item label="运行标志:" :required="true" :error-display-type="'normal'" :property="'run_mark'">
                <bk-radio-group v-model="form.run_mark">
                    <bk-radio :value="item.value" v-for="(item, index) in reviewList" :key="index" style="margin-right: 24px;" :disabled="disabled">
                        {{ item.label }}
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
                    <bk-input v-model="form.fail_offset" type="number" style="width: 139px;margin-right: 9px;" :disabled="disabled" :min="0"></bk-input>
                    <bk-select :clearable="true" style="background-color: #fff;width: 138px;margin-right: 14px;" v-model="form.fail_offset_unit" placeholder="请选择" :disabled="disabled">
                        <bk-option v-for="(item, index) in timeTypeList" :key="index" :id="item.value" :name="item.label">
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
                        <i class="iconfont icon-changyongtubiao-chahao btn" style="margin-left: 8px;" v-if="!disabled && form.inputs[item.key].length > 1"></i>
                        <i class="iconfont icon-changyongtubiao-jiahao btn" v-if="!disabled"></i>
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
</template>

<script>
    export default {
        // props: ['jobFrom'],
        props: {
            jobFrom: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                formLoading: false,
                form: {},
                disabled: true,
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
                reviewList: [{ // 执行前人工复核单选列表
                    label: '正常运行',
                    value: 0
                }, {
                    label: '禁止运行',
                    value: 1
                }],
                scriptTypeList: [{
                                     key: 1,
                                     label: 'Shell(Linux)',
                                     value: 'shell-linux-1'
                                 },
                                 {
                                     key: 2,
                                     label: 'Bat(Windows)',
                                     value: 'bat-win-2'
                                 },
                                 {
                                     key: 3,
                                     label: 'perl',
                                     value: 'perl-3'
                                 },
                                 {
                                     key: 4,
                                     label: 'Python(Linux)',
                                     value: 'python-linux-4'
                                 },
                                 {
                                     key: 5,
                                     label: 'PowerShell(Windows)',
                                     value: 'powershell-win-5'
                                 },
                                 {
                                     key: 6,
                                     label: 'HTTP',
                                     value: 'HTTP'
                                 }
                                 // {
                                 //     key: 7,
                                 //     label: 'Java',
                                 //     value: 'Java'
                                 // },
                                 // {
                                 //     key: 8,
                                 //     label: 'SQL',
                                 //     value: 'SQL'
                                 // }
                ] // 脚本类型下拉列表
            }
        },
        created() {
            this.form = this.jobFrom
            // console.log(this.form)
        },
        methods: {
            checkFormValue(val) {
                let str = val
                if (val === undefined || val === '' || val === null) {
                    str = '--'
                }
                return str
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobDialog {
        // height: 700px;
        // padding-right: 20px;
        padding: 20px;
        overflow: scroll;

        .form {
            .form-item {
                display: flex;
                align-items: center;
                margin-bottom: 24px;

                span {
                    flex-basis: 180px;
                    color: rgb(150,155,165);
                }
                p {
                    width: 280px;
                    color: rgb(90,92,101);
                    white-space:nowrap;
                    overflow:hidden;
                    text-overflow:ellipsis;
                }
                &:last-of-type {
                    margin-bottom: 0;
                }
            }
        }
    }
</style>
