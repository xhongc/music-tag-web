<template>
    <div style="height: 100%;">
        <bk-steps ext-cls="custom-icon"
            :controllable="controllableSteps.controllable"
            :steps="controllableSteps.steps"
            :cur-step.sync="controllableSteps.curStep"
            @step-changed="stepChanged">
        </bk-steps>
        <div class="step-1" v-if="controllableSteps.curStep === 1">
            <single-job-flow></single-job-flow>
        </div>
        <div class="step-2" v-if="controllableSteps.curStep === 2">
            <div style="padding-top: 26px;padding-left: 30px;">
                <div style="font-size: 14px;color: #2b2929;">基础信息</div>
            </div>
            <bk-divider></bk-divider>

            <div style="padding: 30px;">
                <bk-form :label-width="100" :model="formData">
                    <bk-form-item label="任务名称" :required="true" :property="'name'">
                        <bk-input v-model="formData.name" style="width: 350px;"></bk-input>
                    </bk-form-item>
                </bk-form>
            </div>
            <div style="padding-top: 26px;padding-left: 30px;">
                <div style="font-size: 14px;color: #2b2929;">参数信息</div>
            </div>
            <bk-divider></bk-divider>
            <div style="padding: 30px;">
                <bk-form :label-width="100" :model="formData">
                    <bk-form-item label="测试1" :required="true" :property="'name'">
                        <bk-input v-model="formData.name1" style="width: 350px;"></bk-input>
                    </bk-form-item>
                    <bk-form-item label="测试2" :required="true" :property="'name'">
                        <bk-input v-model="formData.name2" style="width: 350px;"></bk-input>
                    </bk-form-item>
                    <bk-form-item label="测试3" :required="true" :property="'name'">
                        <bk-input v-model="formData.name3" style="width: 350px;"></bk-input>
                    </bk-form-item>
                </bk-form>
            </div>
        </div>
        <div class="step-2" v-if="controllableSteps.curStep === 3">
            <div style="padding-top: 26px;padding-left: 30px;">
                <div style="font-size: 14px;color: #2b2929;">执行方式</div>
            </div>
            <bk-divider></bk-divider>
            <div style="padding: 30px;">
                <bk-form :label-width="100" :model="formData">
                    <bk-form-item label="执行时间">
                        <bk-radio-group v-model="formItem.runtimeType">
                            <div style="margin-top: 8px;">
                                <bk-radio :value="'now'">立即</bk-radio>
                            </div>
                            <div style="margin-top: 16px;">
                                <bk-radio :value="'time'">定时</bk-radio>
                                <div style="display: inline-block;">
                                    <bk-date-picker
                                        :disabled="formItem.runtimeType !== 'time'"
                                        v-model="formItem.beginTime"
                                        style="width: 240px;margin-left: 20px;"
                                        :type="'datetime'"
                                        :options="disableTime"
                                        @change="changeTime"
                                        value-format="yyyy-MM-dd HH:mm:ss"
                                        placeholder="选择开始的日期时间">
                                    </bk-date-picker>
                                </div>
                            </div>
                            <div style="color: #EA3636;font-size: 12px;margin: 8px 0 0 68px" v-show="displayImmediate">请填写定时时间</div>
                            <div style="margin-top: 16px;height: 32px">
                                <bk-radio :value="'cycle'">周期</bk-radio>
                                <bk-date-picker
                                    :disabled="formItem.runtimeType !== 'cycle'"
                                    v-model="formItem.cyclebeginTime"
                                    style="width: 240px;margin-left: 20px;"
                                    :type="'datetime'"
                                    :options="disableTime"
                                    @change="changeTime"
                                    value-format="yyyy-MM-dd HH:mm:ss"
                                    placeholder="选择开始的日期时间">
                                </bk-date-picker>
                                <div style="margin-top: -32px;margin-left: 310px;">
                                    <bk-button style="float: left;border: none;background: transparent;width: 54px;padding: 0 8px;">每隔：</bk-button>
                                    <bk-input
                                        style="width:80px;float: left;"
                                        type="number"
                                        v-model="formItem.cycleDat"
                                        :min="1"
                                        :precision="0"
                                        ext-cls="interval-wrap"
                                        :disabled="formItem.runtimeType !== 'cycle'">
                                    </bk-input>
                                    <bk-select
                                        v-model="formItem.cycleType"
                                        :clearable="false"
                                        style="width:80px;float: left;margin-left: 10px;background-color: #fff;"
                                        :disabled="formItem.runtimeType !== 'cycle'">
                                        <bk-option name="分钟" key="min" id="min"></bk-option>
                                        <bk-option name="小时" key="hour" id="hour"></bk-option>
                                        <bk-option name="天" key="day" id="day"></bk-option>
                                    </bk-select>
                                    <span style="margin-left: 10px;">执行一次</span>
                                </div>
                                <div style="color: #EA3636;font-size: 12px;margin: 28px 0 0 68px;position: absolute;line-height: 32px;" v-show="displayCycle">请填写周期时间及间隔</div>
                            </div>
                            <div style="margin-top: 16px;">
                                <bk-radio :value="'cron'">自定义</bk-radio>
                                <LoopRuleSelect
                                    v-if="formItem.runtimeType === 'cron'"
                                    ref="loopRuleSelect"
                                    style="margin-left: 70px;margin-top: -20px;"
                                    :manual-input-value="periodicCron">
                                </LoopRuleSelect>
                            </div>
                        </bk-radio-group>
                    </bk-form-item>
                </bk-form>
            </div>
        </div>
        <div class="step-2" v-if="controllableSteps.curStep === 4">
        </div>
        <div class="step-footer">
            <bk-button :theme="'default'" :title="'主要按钮'" class="mr10" style="margin: 20px;width: 100px;" @click="lastStep">
                上一步
            </bk-button>
            <bk-button :theme="'primary'" :title="'主要按钮'" class="mr10" style="margin: 20px;width: 100px;" @click="nextStep">
                下一步
            </bk-button>
        </div>
    </div>
</template>

<script>
    import singleJobFlow from '../job_flow_mgmt/single_job_flow'
    import LoopRuleSelect from '@/components/time_crontab/crontab'

    export default {
        name: 'task-create',
        components: {
            'single-job-flow': singleJobFlow,
            'LoopRuleSelect': LoopRuleSelect
        },
        data() {
            return {
                controllableSteps: {
                    controllable: false,
                    steps: [
                        { title: '节点选择', icon: 1 },
                        { title: '参数填写', icon: 2 },
                        { title: '执行方式', icon: 3 },
                        { title: '任务执行', icon: 4 }
                    ],
                    curStep: 1
                },
                formData: {
                    name: '',
                    name1: '',
                    name2: '',
                    name3: ''
                },
                formItem: {
                    taskName: '', // 任务名称
                    notifier: [], // 当前通知人
                    runtimeType: 'now', // 立即:now/定时:time/周期:cycle
                    beginTime: '', // 定时任务
                    cyclebeginTime: '', // 周期任务
                    cycleDat: '', // 每隔多少cycleType执行一次
                    cycleType: 'day',
                    modelList: [], // 当前选中模块集合
                    disabledGroup: [], // 当前选中业务的集合 *
                    nowModalData: [],
                    single: false

                },
                disableTime: {
                    disabledDate: function(val) {
                        const nowTime = new Date(new Date().toLocaleDateString()).getTime()
                        const calendarTime = new Date(val.toLocaleDateString()).getTime()
                        return calendarTime < nowTime
                    }
                },
                displayImmediate: false,
                displayCycle: false,
                periodicCron: '*/5 * * * *'
            }
        },
        methods: {
            stepChanged(index) {
                this.controllableSteps.curStep = index
            },
            changeTime(val) {
                if (this.formItem.runtimeType === 'now' || this.formItem.runtimeType === 'cron') return
                if (this.formItem.runtimeType === 'time') {
                    this.formItem.beginTime = val
                }
                if (this.formItem.runtimeType === 'cycle') {
                    this.formItem.cyclebeginTime = val
                }
            },
            lastStep() {
                if (this.controllableSteps.curStep === 1 || this.controllableSteps.curStep === 4) {
                    return false
                } else {
                    this.controllableSteps.curStep = this.controllableSteps.curStep - 1
                }
            },
            nextStep() {
                if (this.controllableSteps.curStep < 3) {
                    this.controllableSteps.curStep = this.controllableSteps.curStep + 1
                } else if (this.controllableSteps.curStep === 3) {
                    this.$bkInfo({
                        title: '确认要执行吗？',
                        confirmLoading: false,
                        confirmFn: async() => {
                            this.tableLoading = true
                            this.$api.process.execute({
                                process_id: this.$route.query.job_flow_data
                            }).then(res => {
                                if (res.result) {
                                    this.$cwMessage('执行成功!', 'success')
                                    this.$store.commit('changeTabActive', 'jobflowview')
                                    this.$router.push({
                                        path: '/jobflowview'
                                    })
                                } else {
                                    this.$cwMessage(res.message, 'error')
                                }
                                this.tableLoading = false
                            })
                        }
                    })
                }
            }
        }
    }
</script>

<style scoped>
.custom-icon {
    margin: 20px 30px 30px 20px;
    width: 90%;
}
.step-1 {
    margin: 20px 30px 30px 20px;
    height: 80%;
}
.step-2 {
    margin: 20px 30px 30px 20px;
    height: 80%;
    background: #ffffff;
}
.step-footer {
    background: #ffffff;
    margin-bottom: -50px;
    height: 100px;
    border-top: 1px solid #cacedb;
}
</style>
