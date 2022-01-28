<template>
    <div id="baseInfo" v-bkloading="{ isLoading: baseInfoLoading, zIndex: 999999 }">
        <bk-form ref="form" :label-width="110" :rules="rules" :model="form">
            <bk-form-item label="作业流名称" :error-display-type="'normal'" :required="true" :property="'jobFlowName'">
                <bk-input placeholder="请输入作业流名称" v-model="form.jobFlowName" :disabled="disabled"></bk-input>
            </bk-form-item>
            <bk-form-item label="作业流描述">
                <bk-input placeholder="请输入作业流描述" v-model="form.jobFlowDescribe" :disabled="disabled"></bk-input>
            </bk-form-item>
            <bk-form-item label="分类">
                <bk-tag-input
                    v-model="form.category"
                    placeholder="placeholder"
                    :trigger="'focus'"
                    :allow-next-focus="false"
                    :list="categoryList"
                    :allow-create="true"
                    :allow-auto-match="true"
                    :has-delete-icon="true"
                    :disabled="disabled">
                </bk-tag-input>
            </bk-form-item>
            <bk-form-item label="调度方式" :error-display-type="'normal'" :required="true" :property="'type'">
                <bk-radio-group v-model="form.run_type" @change="handleControlChange">
                    <bk-radio :value="item.value" v-for="(item, index) in controlList" :key="index"
                        style="margin-right: 24px;" :disabled="disabled">
                        {{item.label}}
                    </bk-radio>
                </bk-radio-group>
            </bk-form-item>
            <bk-form-item label="开始" v-if="form.run_type && form.run_type !== 'null'" :required="true">
                <!-- 调度方式为日历 -->
                <div v-if="form.run_type === 'calendar'">
                    <bk-compose-form-item head-background-color="#fff">
                        <bk-select :clearable="false" style="width: 108px;margin-right: 5px;"
                            v-model="form.calendarValue" placeholder="请选择" :disabled="disabled">
                            <bk-option v-for="(item, index) in calendarList" :key="index" :id="item.id"
                                :name="item.name">
                            </bk-option>
                        </bk-select>
                        <bk-time-picker v-model="form.calendarTime" :placeholder="'选择时间'" style="width: 267px;"
                            format="HH:mm:ss" @change="handleCalendarTimeChange" :disabled="disabled"></bk-time-picker>
                    </bk-compose-form-item>
                </div>
                <!-- 调度方式为定时 -->
                <div v-else-if="form.run_type === 'time'">
                    <bk-date-picker :value="form.fixedTime" :placeholder="'选择日期时间'" :type="'datetime'"
                        style="width: 100%;" format="yyyy-MM-dd HH:mm:ss" @change="handleFixedTimeChange"
                        :disabled="disabled"></bk-date-picker>
                </div>
                <!-- 调度方式为周期 -->
                <div v-else-if="form.run_type === 'cycle'">
                    <bk-date-picker :value="form.periodTime" :placeholder="'选择日期时间'" :type="'datetime'"
                        style="width: 100%;" format="yyyy-MM-dd HH:mm:ss" @change="handlePeriodTimeChange"
                        :disabled="disabled"></bk-date-picker>
                </div>
            </bk-form-item>
            <!-- 调度方式为周期 -->
            <bk-form-item label="每隔" v-if="form.run_type === 'cycle'" :required="true">
                <bk-compose-form-item>
                    <bk-input v-model="form.cycleDat" style="width: 80px;margin-right: 6px;" type="number"
                        :disabled="disabled" :min="0"></bk-input>
                    <bk-select style="background-color: #fff;width: 108px;" v-model="form.timeOption"
                        placeholder="请选择" :disabled="disabled">
                        <bk-option v-for="(item, index) in timeTypeList1" :key="index" :id="item.value"
                            :name="item.label">
                        </bk-option>
                    </bk-select>
                    <span style="margin-left: 11px;">执行</span>
                </bk-compose-form-item>
            </bk-form-item>
            <bk-form-item label="跨日依赖" v-if="form.run_type === 'cycle' || form.run_type === 'calendar'" :style="{ marginTop: form.run_type === 'calendar' ? '10px' : '20px' }">
                <div style="position: relative;">
                    <bk-checkbox v-model="form.cross_day_dependence" :disabled="disabled">
                    </bk-checkbox>
                    <span class="iconfont icon-mianxingtubiao-wenti" style="margin-left: 12px;color: #979BA5;position: absolute;top: 2px;" v-bk-tooltips="crossDayTipConfig"></span>
                </div>
            </bk-form-item>
            <bk-divider style="width: 536px;position: relative;right: 20px;border-color: #e8eaec;"></bk-divider>
            <!-- 这个地方是为了解决在一个bk-form-item的情况下组合两个表单项如何做校验，默认渲染所有的校验项，然后动态改变rules的规则即可 -->
            <!-- 调度方式为定时 -->
            <bk-form-item :property="'fixedTime'" :required="true" ext-cls="custom-form-item">
            </bk-form-item>
            <!-- 调度方式为周期 -->
            <bk-form-item :property="'periodTime'" :required="true" ext-cls="custom-form-item">
            </bk-form-item>
            <bk-form-item :property="'cycleDat'" :required="true" ext-cls="custom-form-item">
            </bk-form-item>
            <bk-form-item :property="'timeOption'" :required="true" ext-cls="custom-form-item">
            </bk-form-item>
            <!-- 调度方式为日历 -->
            <bk-form-item :property="'calendarValue'" :required="true" ext-cls="custom-form-item">
            </bk-form-item>
            <bk-form-item :property="'calendarTime'" :required="true" ext-cls="custom-form-item">
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    export default {
        inject: ['father_this'],
        data() {
            return {
                crossDayTipConfig: {
                    content: '跨日依赖: 指作业流在周期性或日历的调度方式下,作业流如果在前一次的执行中未成功执行,则当时间点到达后一次的计划开始时间时,该作业流不进行自动调度执行。',
                    placement: 'right',
                    width: 300
                },
                pageKey: 0,
                runSysList: [],
                agentList: [],
                agentShow: true,
                baseInfoLoading: false,
                disabled: false,
                midType: '', // 调度方式切换缓冲值
                timeTypeList1: [ // 每隔xxx时间类型下拉选择
                    {
                        value: 'days',
                        label: '天'
                    },
                    {
                        value: 'hours',
                        label: '时'

                    },
                    {
                        value: 'minutes',
                        label: '分'
                    }
                ],
                timeTypeList2: [ // 巡检每隔xxx时间类型下拉选择
                    {
                        value: 'hour',
                        label: '时'
                    },
                    {
                        value: 'min',
                        label: '分'
                    },
                    {
                        value: 'second',
                        label: '秒'
                    }
                ],
                valList: [], // 变量表下拉列表
                calendarList: [], // 日历下拉列表
                controlList: [{ // 调度方式单选列表
                    label: '无',
                    value: 'null'
                }, {
                    label: '定时',
                    value: 'time'
                }, {
                    label: '周期',
                    value: 'cycle'
                }, {
                    label: '日历',
                    value: 'calendar'
                }], // 调度方式单选列表
                varList: [], // 变量表下拉列表
                categoryList: [
                    { id: 'shenzhen', name: '深圳' },
                    { id: 'guangzhou', name: '广州' },
                    { id: 'beijing', name: '北京' },
                    { id: 'shanghai', name: '上海' },
                    { id: 'hangzhou', name: '杭州' },
                    { id: 'nanjing', name: '南京' },
                    { id: 'chognqing', name: '重庆' },
                    { id: 'taibei', name: '台北' },
                    { id: 'haikou', name: '海口' }
                ],
                form: {
                    jobFlowName: '', // 作业流名称
                    jobFlowDescribe: '', // 作业流描述
                    var_table: '', // 变量表
                    category: [],
                    run_type: '', // 调度方式
                    calendarValue: '', // 调度方式为日历，日历值
                    calendarTime: '', // 调度方式为日历，日历时间值
                    fixedTime: '', // 调度方式为定时，开始时间
                    periodTime: '', // 调度方式为周期， 开始时间
                    cycleDat: '', // 调度方式为周期，每隔xxx
                    timeOption: '', // 调度方式为周期，时间类型
                    cross_day_dependence: '', // 跨日依赖
                    pre_category: '', // 前置跑批id
                    pre_agent: '', // 前置agent
                    pre_commands: [{ // 前置依赖命令检测
                        key: '',
                        value: ''
                    }],
                    file_dependence: {
                        file_path: '', // 前置文件路径
                        max_num: '', // 巡检次数
                        cycle: { // 巡检周期
                            type: '', // 时间类型
                            value: '' // 时间值
                        }
                    }
                },
                rules: {
                    jobFlowName: [{
                        required: true,
                        message: '作业流名称不能为空，请检查您的输入！',
                        trigger: 'blur'
                    }],
                    run_type: [{
                        required: true,
                        message: '调度方式不能为空，请检查您的选择！',
                        trigger: 'blur'
                    }]
                }
            }
        },
        created() {
            this.initValList()
            this.getRunSysList()
            this.initCalendarList()
        },
        mounted() {
            if (this.$route.query.type !== 'add') {
                this.baseInfoLoading = true
                if (this.$route.query.type === 'detail') {
                    this.disabled = true
                }
                setTimeout(() => {
                    // if (this.father_this.jobFlowFrom.hasOwnProperty('cross_day_dependence')) {
                    //     this.form.cross_day_dependence = true
                    // }
                    this.form.cross_day_dependence = this.father_this.jobFlowFrom.cross_day_dependence
                    this.form.run_type = this.father_this.jobFlowFrom.run_type // 调度方式初始化
                    this.handleChangeRules()
                    this.form.var_table = this.father_this.jobFlowFrom.var_table // 表量表值初始化
                    this.midType = this.form.run_type
                    this.form.jobFlowName = this.father_this.jobFlowFrom.name // 作业流名称初始化
                    this.form.jobFlowDescribe = this.father_this.jobFlowFrom.description // 作业流描述初始化
                    // this.form.calendarTime = this.father_this.jobFlowFrom.trigger_data.eta // 调度方式为日历，开始时间初始化
                    this.form.calendarTime = '' // 调度方式为日历，开始时间初始化
                    if (this.father_this.jobFlowFrom.pre_commands !== null) {
                        this.form.pre_commands = this.father_this.jobFlowFrom.pre_commands // 作业流前置依赖初始化
                    }
                    if (this.father_this.jobFlowFrom.hasOwnProperty('pre_category')) {
                        this.form.pre_category = this.father_this.jobFlowFrom.pre_category // 作业流前置跑批id初始化
                    }
                    if (this.father_this.jobFlowFrom.hasOwnProperty('pre_agent')) {
                        this.form.pre_agent = this.father_this.jobFlowFrom.pre_agent // 作业流前置agnet初始化
                    }
                    // 调度方式为定时
                    if (this.form.run_type === 'time') {
                        this.form.fixedTime = this.father_this.jobFlowFrom.trigger_data.eta // 调度方式为定时，开始时间初始化
                    }
                    // 调度方式为周期
                    if (this.form.run_type === 'cycle') {
                        this.form.periodTime = this.father_this.jobFlowFrom.trigger_data.eta // 调度方式为周期，开始时间初始化
                        this.form.cycleDat = this.father_this.jobFlowFrom.trigger_data.cycle // 调度方式为周期，每隔XXX初始化
                        this.form.timeOption = this.father_this.jobFlowFrom.trigger_data
                            .unit // 调度方式为周期， 时间类型初始化
                    }
                    // 调度方式为日历
                    if (this.form.run_type === 'calendar') {
                        this.form.calendarValue = this.father_this.jobFlowFrom.trigger_data
                            .calendar_id // 调度方式为日历，日历值初始化
                        this.form.calendarTime = this.father_this.jobFlowFrom.trigger_data
                            .eta // 调度方式为日历，开始时间初始化
                    }
                    this.baseInfoLoading = false
                }, 2000)
            }
        },
        methods: {
            // 获取作业库跑批系统
            getRunSysList() {
                this.runSysList = []
            },
            handleRunIdChange() {
                if (this.form.pre_category === '') {
                    this.agentList = []
                    this.form.pre_agent = ''
                    return false
                }
                this.getAgentList()
            },
            // 获取agent列表
            getAgentList() {
                // pageKey用于处理首次加载页面时假如前置agent有值而由于前置跑批id初始化改变触发change事件使其清空。
                if (this.pageKey !== 0) {
                    this.form.pre_agent = ''
                    this.agentList = []
                }
                this.baseInfoLoading = true
                this.agentShow = false
                this.$api.station.list({
                    'category': this.form.pre_category
                }).then(res => {
                    if (res.result) {
                        this.agentList = res.data.items
                        this.agentShow = true
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.pageKey += 1
                    this.baseInfoLoading = false
                })
            },
            // 处理删除前置条件检测命令
            handleDeleteCommand(index) {
                this.form.pre_commands.splice(index, 1)
            },
            // 处理添加前置条件检测命令
            handleAddCommand() {
                this.form.pre_commands.push({
                    key: '',
                    value: ''
                })
            },
            // 初始化日历下拉
            initCalendarList() {
                this.calendarList = []
            },
            // 初始化变量表下拉
            initValList() {
                this.varList = []
            },
            handleCalendarTimeChange(e) {
                this.form.calendarTime = e
            },
            handleFixedTimeChange(e) {
                this.form.fixedTime = e
            },
            handlePeriodTimeChange(e) {
                this.form.periodTime = e
            },
            // 处理动态切换表单校验规则
            handleChangeRules() {
                if (this.form.run_type === 'null') {
                    this.rules = {
                        jobFlowName: [{
                            required: true,
                            message: '作业流名称不能为空，请检查您的输入！',
                            trigger: 'blur'
                        }],
                        run_type: [{
                            required: true,
                            message: '调度方式不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }]
                    }
                }
                if (this.form.run_type === 'time') {
                    this.rules = {
                        jobFlowName: [{
                            required: true,
                            message: '作业流名称不能为空，请检查您的输入！',
                            trigger: 'blur'
                        }],
                        run_type: [{
                            required: true,
                            message: '调度方式不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }],
                        fixedTime: [{
                            required: true,
                            trigger: 'blur',
                            message: '定时调度方式下，开始时间不能为空，请检查您的选择！'
                        }, {
                            required: true,
                            trigger: 'change',
                            message: '定时调度方式下，开始时间不能小于当前时间，请检查您的选择！',
                            validator: (e) => {
                                const data1 = new Date(e)
                                const data2 = new Date()
                                if (data1 < data2) {
                                    return false
                                }
                                return true
                            }
                        }]
                    }
                }
                if (this.form.run_type === 'cycle') {
                    this.rules = {
                        jobFlowName: [{
                            required: true,
                            message: '作业流名称不能为空，请检查您的输入！',
                            trigger: 'blur'
                        }],
                        run_type: [{
                            required: true,
                            message: '调度方式不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }],
                        periodTime: [{
                            required: true,
                            message: '周期调度方式下，开始时间不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }],
                        cycleDat: [{
                            required: true,
                            message: '周期调度方式下，每隔多少时间不能为空，请检查您的输入！',
                            trigger: 'blur'
                        }],
                        timeOption: [{
                            required: true,
                            message: '周期调度方式下，时间类型不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }]
                    }
                }
                if (this.form.run_type === 'calendar') {
                    this.rules = {
                        jobFlowName: [{
                            required: true,
                            message: '作业流名称不能为空，请检查您的输入！',
                            trigger: 'blur'
                        }],
                        run_type: [{
                            required: true,
                            message: '调度方式不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }],
                        calendarValue: [{
                            required: true,
                            message: '日历调度方式下，日历值不能为空，前检查您的选择！',
                            trigger: 'blur'
                        }],
                        calendarTime: [{
                            required: true,
                            message: '日历调度方式下，日历开始时间时间不能为空，请检查您的选择！',
                            trigger: 'blur'
                        }]
                    }
                }
            },
            // 处理调度方式切换确认
            confim(e) {
                this.midType = e
                this.form.calendarValue = ''
                this.form.calendarTime = ''
                this.form.fixedTime = ''
                this.form.periodTime = ''
                this.form.cycleDat = ''
                this.form.timeOption = ''
                this.form.cross_day_dependence = ''
                this.handleChangeRules()
            },
            // 处理调度方式改变
            handleControlChange(e) {
                if (this.midType === '') {
                    this.midType = e
                }
                // 其他切日历
                if (e === 'calendar' && this.midType !== 'calendar') {
                    return this.$bkInfo({
                        type: 'primary',
                        title: '此操作将请空画布及任务编排, 确认吗？',
                        width: 500,
                        confirmLoading: false,
                        confirmFn: async() => {
                            this.$emit('empty-task-make', true)
                            this.confim(e)
                        },
                        cancelFn: async() => {
                            this.form.run_type = this.midType
                        }
                    })
                }
                if (this.midType === 'calendar' && e !== 'calendar') {
                    return this.$bkInfo({
                        type: 'primary',
                        title: '此操作将请空画布及任务编排, 确认吗？',
                        width: 500,
                        confirmLoading: false,
                        confirmFn: async() => {
                            this.$emit('empty-task-make', true)
                            this.confim(e)
                        },
                        cancelFn: async() => {
                            this.form.run_type = this.midType
                        }
                    })
                }
                this.confim(e)
            }
        }
    }
</script>

<style lang="scss" scoped>
    #baseInfo {
        /deep/ .custom-form-item {
            display: none;
        }

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
                    color: rgb(58, 132, 255);
                }
            }
        }
    }
</style>
