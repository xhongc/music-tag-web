<template>
    <div id="jobView">
        <div class="header" v-if="auth.operate || auth.search">
            <div style="float: left;font-size: 0px;" v-if="auth.operate">
                <bk-button class="operationBtn" @click="handleOperation('pause')">挂起</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('resume')">恢复</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('stop')">终止</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('cancel')">取消</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('replay')">重新执行</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('release')">释放依赖</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('success')">强制成功</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('confirm')">复核</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;margin-right: 8px;" :placeholder="'请输入作业名称'"
                    :right-icon="'bk-icon icon-search'" v-model="searchForm.name" @right-icon-click="handleSearch"
                    @enter="handleSearch">
                </bk-input>
                <bk-button slot="dropdown-trigger" :theme="isDropdownShow === true ? 'primary' : 'default'" @click="handleOpenSeniorSearch"
                    :icon-right="isDropdownShow === true ? 'angle-double-up' : 'angle-double-down'">高级搜索</bk-button>
            </div>
            <div class="senior-search-box" v-if="isDropdownShow">
                <bk-container :margin="0">
                    <bk-form :label-width="110">
                        <bk-row>
                            <bk-col :span="6">
                                <bk-form-item label="作业名">
                                    <bk-input :placeholder="'请输入作业名称'" v-model="searchForm.name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="执行者">
                                    <bk-input :placeholder="'请输入执行者'" v-model="searchForm.executor" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="作业流名">
                                    <bk-input :placeholder="'请输入作业流名称'" v-model="searchForm.process_run_name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="状态">
                                    <bk-select class="header-select" :clearable="true" style="background-color: #fff;"
                                        v-model="searchForm.state">
                                        <bk-option v-for="(item, index) in stateList" :key="index" :id="item.name"
                                            :name="item.label">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 24px;">
                            <bk-col :span="6">
                                <bk-form-item label="Agent">
                                    <bk-input :placeholder="'请输入Agent'" v-model="searchForm.station" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="计划开始">
                                    <bk-date-picker :value="searchForm.eta" :placeholder="'选择日期时间'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleEtaChange"></bk-date-picker>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="实际开始">
                                    <bk-date-picker :value="searchForm.startTime" :placeholder="'选择日期时间'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleStartTimeChange"></bk-date-picker>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="完成时间">
                                    <bk-date-picker :value="searchForm.endTime" :placeholder="'选择日期时间'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleEndTimeChange"></bk-date-picker>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 24px;">
                            <bk-col :span="6">
                                <bk-form-item label="已复核人">
                                    <bk-input :placeholder="'请输入已复核人'" v-model="searchForm.confirm_users"></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="待复核人数">
                                    <bk-input :placeholder="'请输入待复核人数'" v-model="searchForm.need_confirm"></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="跑批系统">
                                    <bk-select :clearable="true" style="background-color: #fff;" v-model="searchForm.category"
                                        placeholder="请选择">
                                        <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id" :name="item.name">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="display: flex;justify-content: center;margin-top: 16px;">
                            <bk-button theme="primary" @click="handleSearch">查询</bk-button>
                            <bk-button style="margin-left: 8px;" @click="handleReset">重置</bk-button>
                            <bk-button style="margin-left: 8px;" @click="handleOpenSeniorSearch">取消</bk-button>
                        </bk-row>
                    </bk-form>
                </bk-container>
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable" @select="handleSelect" @select-all="handleSelectAll" :size="setting.size" :max-height="maxTableHeight">
                <bk-table-column type="selection" width="60"></bk-table-column>
                <bk-table-column :label="item.label" :prop="item.id" v-for="(item, index) in setting.selectedFields"
                    :key="index" :show-overflow-tooltip="item.overflowTooltip" :sortable="item.sortable">
                    <template slot-scope="props">
                        <div v-if="item.id === 'name'" style="color: #3a84ff;cursor: pointer;" @click="handleCheckDetail(props.row)">{{props.row.name}}</div>
                        <div v-else-if="item.id === 'state'">{{stateList[stateList.findIndex(e => e.name === props.row.state)].label}}</div>
                        <div v-else>
                            <span>{{(props.row[item.id] === '' || props.row[item.id] === null) ? '- -' : props.row[item.id]}}</span>
                        </div>
                    </template>
                </bk-table-column>
                <!--                <bk-table-column label="作业执行详情" width="150">
                    <template slot-scope="props">
                        <bk-button theme="primary" text @click="handleCheckDetail(props.row)">查看详情</bk-button>
                    </template>
                </bk-table-column> -->
                <bk-table-column type="setting">
                    <bk-table-setting-content :fields="setting.fields" :selected="setting.selectedFields"
                        @setting-change="handleSettingChange" :size="setting.size">
                    </bk-table-setting-content>
                </bk-table-column>
            </bk-table>
        </div>
    </div>
</template>

<script>
    import {
        deepClone
    } from '../../../common/util.js'
    import {
        mapGetters
    } from 'vuex'
    export default {
        data() {
            const fields = [{
                id: 'name',
                label: '作业名',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'process',
                label: '所属作业流名',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'state',
                label: '状态',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'category_name',
                label: '跑批系统',
                overflowTooltip: false,
                sortable: true
            }, {
                id: 'need_confirm',
                label: '待复核人数',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'confirm_users',
                label: '已复核人',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'station',
                label: 'Agent',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'executor',
                label: '执行者',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'eta',
                label: '计划开始时间',
                overflowTooltip: true,
                sortable: true
            }, {
                id: 'start_time',
                label: '实际开始时间',
                overflowTooltip: true,
                sortable: true
            }, {
                id: 'end_time',
                label: '完成时间',
                overflowTooltip: true,
                sortable: true
            }]
            return {
                maxTableHeight: '',
                setting: {
                    size: 'small', // 表格大小
                    fields: fields, // 表格所有列
                    selectedFields: fields // 表格当前显示列
                },
                opreateFlag: false,
                midSearchForm: {},
                auth: {},
                timer: null, // 轮询定时器
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                runSysList: [], // 跑批系统下拉
                tableLoading: false,
                selectionList: [],
                tableList: [],
                searchForm: {
                    name: '', // 作业名
                    executor: '', // 执行者
                    process_run_name: '', // 作业流名
                    state: '', // 状态
                    station: '', // agent
                    eta: ['', ''], // 计划开始时间
                    startTime: ['', ''], // 实际开始时间
                    endTime: ['', ''], // 完成时间
                    confirm_users: '', // 已复核人
                    need_confirm: '', // 待复核人数
                    category: '' // 跑批系统
                },
                isDropdownShow: false,
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
                                name: 'positive',
                                label: '就绪'
                            },
                            {
                                id: 9,
                                name: 'cancel',
                                label: '取消'
                            },
                            {
                                id: 10,
                                name: 'need_confirm',
                                label: '待复核'
                            },
                            {
                                id: 11,
                                name: 'ignore',
                                label: '忽略'
                            }
                ]
            }
        },
        computed: mapGetters(['jobViewSearchForm']),
        created() {
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 143
            // 初始化搜索
            this.initSearch()
            // 获取跑批系统
            this.getRunSysList()
            // 首屏刷新
            this.handleLoad(true)
            this.timer = setInterval(() => {
                // 轮询刷新，非首屏
                this.handleLoad(false)
            }, 15000)
        },
        beforeDestroy() {
            clearInterval(this.timer)
        },
        methods: {
            // 处理表格字段显隐
            handleSettingChange({
                fields,
                size
            }) {
                this.setting.size = size
                this.setting.selectedFields = fields
            },
            handleEtaChange(e) {
                this.searchForm.eta = e
            },
            handleStartTimeChange(e) {
                this.searchForm.startTime = e
            },
            handleEndTimeChange(e) {
                this.searchForm.endTime = e
            },
            // 处理表格size切换
            handlePageLimitChange(val) {
                this.pagination.current = 1
                this.pagination.limit = val
                // 首屏刷新
                this.handleLoad(true)
            },
            // 处理页面跳转
            handlePageChange(page) {
                this.pagination.current = page
                // 首屏刷新
                this.handleLoad(true)
            },
            // 处理操作
            handleOperation(str) {
                if (this.selectionList.length === 0) {
                    return this.$cwMessage('至少选择一条数据', 'warning')
                }
                const ids = []
                // 数组去重
                this.selectionList.forEach(item => {
                    if (ids.indexOf(item.id) < 0) {
                        ids.push(item.id)
                    }
                })
                const contentMap = {
                    'pause': {
                        preState: '等待',
                        content: '作业暂停执行，不会继续后面的执行',
                        width: 400
                    },
                    'resume': {
                        preState: '挂起',
                        content: '恢复挂起作业',
                        width: 400
                    },
                    'stop': {
                        preState: '进行中',
                        content: '终止后不会继续后面的执行，并且无法恢复。会强制终止此作业',
                        width: 550
                    },
                    'cancel': {
                        preState: '除了正在执行，忽略，就绪',
                        content: '将作业状态置为取消，可以继续往下执行',
                        width: 500
                    },
                    'replay': {
                        preState: '已完成、错误、失败，终止、取消',
                        content: '复制一份该作业，并放入原作业流中。如果新的作业成功，那么对作业流就是成功了',
                        width: 650
                    },
                    'release': {
                        preState: '未执行',
                        content: '释放此作业的被依赖关系（包括时间依赖）',
                        width: 400
                    },
                    'success': {
                        preState: '错误，失败，终止',
                        content: '针对错误，失败，终止的作业，设置为成功',
                        wdith: 400
                    },
                    'confirm': {
                        preState: '待复核',
                        content: '针对待复核的作业，设置为等待',
                        width: 400
                    }
                }
                this.$bkInfo({
                    type: 'primary',
                    title: `执行前状态：${contentMap[str].preState}`,
                    subTitle: `功能说明：${contentMap[str].content}`,
                    width: contentMap[str].width,
                    // width: 600,
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.tableLoading = true
                        this.opreateFlag = true
                        this.$api.nodeRun.control({
                            'event': str,
                            'ids': ids
                        }).then(res => {
                            this.loading = false
                            if (res.result) {
                                // 首屏刷新
                                // 这里如果不请空已选的selection。在按某些条件查询下。当页面刷新时，因为是按条件查询。之前已选的selection中状态已改变可是因为默认selection的关系还存在选择列中，可是实际上页面是看不到这些的。所以会导致错误
                                if (this.jobViewSearchForm.state || this.jobViewSearchForm.need_confirm) {
                                    this.selectionList = []
                                }
                                this.opreateFlag = false
                                this.handleLoad(true)
                                this.$cwMessage('操作成功！', 'success')
                            } else {
                                // if (this.searchForm.state !== '') {
                                //     this.selectionList = []
                                // }
                                this.opreateFlag = false
                                this.handleLoad(true)
                                this.$cwMessage(res.message, 'error')
                            }
                            this.tableLoading = false
                        })
                    }
                })
            },
            // 处理全选
            handleSelectAll(selection) {
                if (selection.length > 0) {
                    this.selectionList = this.selectionList.concat(selection)
                } else {
                    this.tableList.forEach(ms => {
                        this.selectionList = this.selectionList.filter(item => item.id !== ms.id)
                    })
                }
            },
            // 处理单选
            handleSelect(selection, row) {
                const isHaveItem = this.selectionList.find(item => item.id === row.id)
                if (isHaveItem) {
                    this.selectionList = this.selectionList.filter(item => item.id !== isHaveItem.id)
                } else {
                    this.selectionList.push(row)
                }
            },
            // 查看详情
            handleCheckDetail(row) {
                this.$router.push({
                    path: '/jobdetail',
                    query: {
                        id: row.id
                    }
                })
            },
            // 处理查询重置
            handleReset() {
                this.searchForm = {
                    name: '', // 作业名
                    executor: '', // 执行者
                    process_run_name: '', // 作业流名
                    state: '', // 状态
                    station: '', // agent
                    eta: ['', ''], // 计划开始时间
                    startTime: ['', ''], // 实际开始时间
                    endTime: ['', ''], // 完成时间
                    confirm_users: '', // 已复核人
                    need_confirm: '', // 待复核人数
                    category: '' // 跑批系统
                }
            },
            handleSearch() {
                // 更新查询缓存
                this.selectionList = []
                this.$store.commit('getJobViewSearch', this.searchForm)
                this.midSearchForm = deepClone(this.searchForm)
                this.pagination.current = 1
                // 首屏刷新
                this.handleLoad(true)
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
                // this.handleReset()
            },
            // 获取跑批系统
            getRunSysList() {
                this.runSysList = []
            },
            // 搜索值初始化
            initSearch() {
                const catchForm = this.jobViewSearchForm
                // 作业名
                if (catchForm.hasOwnProperty('name')) {
                    this.searchForm.name = catchForm.name
                }
                // 执行者
                if (catchForm.hasOwnProperty('executor')) {
                    this.searchForm.executor = catchForm.executor
                }
                // 计划开始时间
                if (catchForm.hasOwnProperty('eta')) {
                    this.searchForm.eta[0] = catchForm.eta[0]
                    this.searchForm.eta[1] = catchForm.eta[1]
                }
                // 实际开始时间
                if (catchForm.hasOwnProperty('startTime')) {
                    this.searchForm.startTime[0] = catchForm.startTime[0]
                    this.searchForm.startTime[1] = catchForm.startTime[1]
                }
                // 完成时间
                if (catchForm.hasOwnProperty('endTime')) {
                    this.searchForm.endTime[0] = catchForm.endTime[0]
                    this.searchForm.endTime[1] = catchForm.endTime[1]
                }
                // 作业流名
                if (catchForm.hasOwnProperty('process_run_name')) {
                    this.searchForm.process_run_name = catchForm.process_run_name
                }
                // 待复核人数
                if (catchForm.hasOwnProperty('need_confirm')) {
                    this.searchForm.need_confirm = catchForm.need_confirm
                }
                // 已复核人
                if (catchForm.hasOwnProperty('confirm_users')) {
                    this.searchForm.confirm_users = catchForm.confirm_users
                }
                // agent
                if (catchForm.hasOwnProperty('station')) {
                    this.searchForm.station = catchForm.station
                }
                // 跑批系统
                if (catchForm.hasOwnProperty('category')) {
                    this.searchForm.category = catchForm.category
                }
                // 状态
                if (catchForm.hasOwnProperty('state')) {
                    this.searchForm.state = catchForm.state
                }
                // 使用midSearchForm来查询表格，为了避免轮询调接口因为v-model双向绑定searchForm引起用户未点击查询而表格也会根据当前条件获取
                this.midSearchForm = deepClone(this.searchForm)
            },
            // 处理表格默认选择
            defaultCheck() {
                this.tableLoading = true
                this.$nextTick(() => {
                    this.selectionList.forEach(item1 => {
                        this.tableList.forEach(item2 => {
                            if (item1.id === item2.id) {
                                this.$refs.table.toggleRowSelection(item2, true)
                            }
                        })
                    })
                    this.tableLoading = false
                })
            },
            handleLoad(first = false) {
                // 当前页面在等待操作结果，不做轮询
                if (this.opreateFlag) {
                    return false
                }
                if (first) {
                    this.tableLoading = true
                }
                const params = {
                    name: this.midSearchForm.name, // 作业名
                    executor: this.midSearchForm.executor, // 执行者
                    eta_gte: this.midSearchForm.eta[0], // 计划开始时间
                    eta_lte: this.midSearchForm.eta[1], // 计划开始时间
                    start_time_gte: this.midSearchForm.startTime[0], // 实际开始时间
                    start_time_lte: this.midSearchForm.startTime[1], // 实际开始时间
                    end_time_gte: this.midSearchForm.endTime[0], // 完成时间
                    end_time_lte: this.midSearchForm.endTime[1], // 完成时间
                    process_run_name: this.midSearchForm.process_run_name, // 作业流名
                    need_confirm: this.midSearchForm.need_confirm, // 待复核人数
                    confirm_users: this.midSearchForm.confirm_users, // 已复核人
                    station_name: this.midSearchForm.station, // agent
                    state: this.midSearchForm.state, // 状态
                    category: this.midSearchForm.category, // 跑批系统
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }
                if (this.$route.query.hasOwnProperty('job_flow_id')) {
                    params.process_run = this.$route.query.job_flow_id
                }
                this.$api.nodeRun.list(params).then(res => {
                    if (res.result) {
                        this.tableList = res.data.items
                        this.pagination.count = res.data.count
                        if (this.selectionList.length) {
                            this.defaultCheck()
                        }
                        this.tableLoading = false
                    } else {
                        this.$cwMessage(res.message, 'error')
                        this.tableLoading = false
                    }
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobView {
        height: 100%;
        overflow: auto;

        .header {
            width: 100%;
            font-size: 0;
            margin-bottom: 20px;
            float: left;
            // position: relative;

            .operationBtn {
                margin-right: 8px;
            }

            .senior-search-box {
                background-color: #fff;
                padding: 20px;
                width: 100%;
                margin-top: 20px;
                float: left;
                box-shadow: 0px 4px 8px 0px rgba(0, 0, 0, .1);
                border: 1px solid rgba(0, 0, 0, .2);
            }
        }

        .content {

            .customTable {
                /deep/ .bk-table-pagination-wrapper {
                    background-color: #fff;
                }
            }
        }
    }
</style>
