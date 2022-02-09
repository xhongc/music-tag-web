<template>
    <div id="jobFlowView">
        <div class="header" v-if="auth.operate || auth.search">
            <div style="float: left;" v-if="auth.operate">
                <bk-button class="operationBtn" @click="handleOperation('pause')">挂起</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('resume')">恢复</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('cancel')">取消</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('replay')">重新执行</bk-button>
                <bk-button class="operationBtn" @click="handleOperation('release')">释放依赖</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;margin-right: 8px;" :placeholder="'请输入作业流名称'"
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
                                <bk-form-item label="作业流名">
                                    <bk-input :placeholder="'请输入作业流名称'" v-model="searchForm.name" clearable></bk-input>
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
                            <bk-col :span="6">
                                <bk-form-item label="计划开始">
                                    <bk-date-picker :value="searchForm.eta" :placeholder="'选择日期时间'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleEtaChange"></bk-date-picker>
                                </bk-form-item>
                            </bk-col>
                            <!-- 未支持 -->
                            <bk-col :span="6">
                                <bk-form-item label="作业总数">
                                    <bk-input :placeholder="'请输入作业总数'" v-model="searchForm.total_job_count" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 24px;">
                            <bk-col :span="6">
                                <bk-form-item label="未执行作业数">
                                    <bk-input :placeholder="'请输入未执行作业数'" v-model="searchForm.total_not_execute_job_count"
                                        clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="释放依赖">
                                    <bk-select class="header-select" :clearable="true" style="background-color: #fff;"
                                        v-model="searchForm.is_release_dependency">
                                        <bk-option v-for="(item, index) in replyList" :key="index" :id="item.value"
                                            :name="item.label">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="实际开始">
                                    <bk-date-picker :value="searchForm.start_time" :placeholder="'选择日期时间'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleStartTimeChange"></bk-date-picker>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="完成时间">
                                    <bk-date-picker :value="searchForm.end_time" :placeholder="'选择日期时间'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleEndTimeChange"></bk-date-picker>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 24px;">
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
                        <div v-else-if="item.id === 'type'">
                            <span v-if="props.row.type === 'null'">无</span>
                            <span v-else-if="props.row.type === 'time'">定时</span>
                            <span v-else-if="props.row.type === 'cycle'">周期</span>
                            <span v-else-if="props.row.type === 'calendar'">日历</span>
                        </div>
                        <div v-else-if="item.id === 'is_release_dependency'">
                            <span v-if="props.row.is_release_dependency === false">否</span>
                            <span v-if="props.row.is_release_dependency === true">是</span>
                        </div>
                        <div v-else>
                            <span>{{(props.row[item.id] === '' || props.row[item.id] === null) ? '- -' : props.row[item.id]}}</span>
                        </div>
                    </template>
                </bk-table-column>
                <bk-table-column label="作业流情况" width="150">
                    <template slot-scope="props">
                        <!-- <bk-button theme="primary" text style="margin-right: 12px;display: inline-block;" @click="handleCheckDetail(props.row)">查看详情</bk-button> -->
                        <bk-button theme="primary" text @click="handleCheckJob(props.row)">查看作业</bk-button>
                    </template>
                </bk-table-column>
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
                label: '作业流名',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'category_name',
                label: '跑批系统',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'state',
                label: '状态',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'total_job_count',
                label: '作业总数',
                overflowTooltip: false,
                sortable: true
            }, {
                id: 'type',
                label: '调度方式',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'total_not_execute_job_count',
                label: '未执行作业数',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'is_release_dependency',
                label: '是否释放依赖',
                overflowTooltip: true,
                sortable: true
            }, {
                id: 'eta',
                label: '计划开始时间',
                overflowTooltip: true,
                sortable: true
            }, {
                id: 'start_time',
                label: '实际开始时间',
                overflowTooltip: false,
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
                    selectedFields: fields.slice(0, 1) // 表格当前显示列
                },
                opreateFlag: false,
                midSearchForm: {},
                auth: {},
                timer: null, // 轮询定时器
                selectionList: [],
                tableList: [],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                tableLoading: false,
                runSysList: [],
                searchForm: {
                    name: '', // 作业流名
                    state: '', // 状态
                    eta: ['', ''], // 计划开始时间
                    total_job_count: '', // 作业总数
                    total_not_execute_job_count: '', // 未执行作业数
                    is_release_dependency: '', // 释放依赖
                    start_time: ['', ''], // 实际开始时间
                    end_time: ['', ''], // 完成时间
                    category: '' // 跑批系统
                },
                isDropdownShow: false,
                replyList: [{
                                id: 1,
                                value: 'false',
                                label: '否'
                            },
                            {
                                id: 2,
                                value: 'true',
                                label: '是'
                            }
                ],
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
                                name: 'cancel',
                                label: '取消'
                            },
                            {
                                id: 8,
                                name: 'positive',
                                label: '就绪'
                            },
                            {
                                id: 9,
                                name: 'stop',
                                label: '终止'
                            },
                            {
                                id: 10,
                                name: 'need_confirm',
                                label: '待审核'
                            },
                            {
                                id: 11,
                                name: 'ignore',
                                label: '忽略'
                            },
                            {
                                id: 12,
                                name: 'exists_need_confirm',
                                label: '正在执行（存在审核）'
                            },
                            {
                                id: 13,
                                name: 'exists_error',
                                label: '正在执行（存在错误）'
                            },
                            {
                                id: 14,
                                name: 'exists_fail',
                                label: '正在执行（存在失败）'
                            },
                            {
                                id: 15,
                                name: 'exists_stop',
                                label: '正在执行（存在终止）'
                            },
                            {
                                id: 16,
                                name: 'exists_pause',
                                label: '正在执行（存在挂起）'
                            }
                ]
            }
        },
        computed: mapGetters(['jobFlowViewSearchForm']),
        created() {
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 143
            // 初始化搜索
            this.initSearch()
            // 首屏刷新
            this.handleLoad(true)
            // 获取跑批系统
            this.getRunSysList()
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
                this.searchForm.start_time = e
            },
            handleEndTimeChange(e) {
                this.searchForm.end_time = e
            },
            // 处理查看详情
            handleCheckDetail(row) {
                this.$router.push({
                    path: '/viewdetail',
                    query: {
                        id: row.id
                    }
                })
            },
            // 处理查看作业
            handleCheckJob(row) {
                this.$store.commit('changeTabActive', 'jobview')
                // this.$store.commit('getJobFlowViewSearch', {jobFlowId: row.id})
                this.$router.push({
                    path: '/jobview',
                    query: {
                        job_flow_id: row.id
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
                // 处理操作前，刷新表格状态。开启loading防止误操作
                const ids = []
                // 数组去重
                this.selectionList.forEach(item => {
                    if (ids.indexOf(item.id) < 0) {
                        ids.push(item.id)
                    }
                })
                const contentMap = {
                    'pause': {
                        preState: '等待、进行中',
                        content: '作业流暂停执行，不会继续后面的执行。属于该作业流的正在执行的作业会继续完成，完成后后续作业不会继续',
                        width: 850
                    },
                    'resume': {
                        preState: '挂起',
                        content: '恢复挂起作业流',
                        width: 400
                    },
                    'cancel': {
                        preState: '除了正在执行',
                        content: '将作业流状态置为取消，不可继续往下执行。将内部所有作业状态置为取消状态',
                        width: 650
                    },
                    'replay': {
                        preState: '成功、错误、失败、取消',
                        content: '重新创建并实例化作业流，然后执行',
                        width: 500
                    },
                    'release': {
                        preState: '未执行',
                        content: '强制执行，包括时间依赖（作业流如果为日历调度也需要定义时间）和前置依赖（释放作业流层面的依赖，不影响作业的依赖',
                        width: 900
                    }
                }
                this.$bkInfo({
                    type: 'primary',
                    title: `执行前状态：${contentMap[str].preState}`,
                    subTitle: `功能说明：${contentMap[str].content}`,
                    width: contentMap[str].width,
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.tableLoading = true
                        // 避免操作接口时间过长，由于接口轮询而接口loading
                        this.opreateFlag = true
                        this.$api.processRun.control({
                            'event': str,
                            'ids': ids
                        }).then(res => {
                            if (res.result) {
                                // 首屏刷新
                                // 这里如果不请空已选的selection。在按某些条件查询下。当页面刷新时，因为是按条件查询。之前已选的selection中状态已改变可是因为默认selection的关系还存在选择列中，可是实际上页面是看不到这些的。所以会导致错误
                                if (this.jobFlowViewSearchForm.state || this.jobFlowViewSearchForm.is_release_dependency) {
                                    this.selectionList = []
                                }
                                this.opreateFlag = false
                                this.$cwMessage('操作成功！', 'success')
                                this.handleLoad(true)
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
            // 处理查询重置
            handleReset() {
                this.searchForm = {
                    name: '', // 作业流名
                    state: '', // 状态
                    eta: ['', ''], // 计划开始时间
                    total_job_count: '', // 作业总数
                    total_not_execute_job_count: '', // 未执行作业数
                    is_release_dependency: '', // 释放依赖
                    start_time: ['', ''], // 实际开始时间
                    end_time: ['', ''], // 完成时间
                    category: '' // 跑批系统
                }
            },
            // 处理查询
            handleSearch() {
                // 更新缓存
                this.selectionList = []
                this.$store.commit('getJobFlowViewSearch', this.searchForm)
                this.midSearchForm = deepClone(this.searchForm)
                this.pagination.current = 1
                // 首屏刷新
                this.handleLoad(true)
            },
            // 获取跑批系统
            getRunSysList() {
                this.runSysList = []
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
                // this.handleReset()
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
            // 搜索值初始化
            initSearch() {
                const catchForm = this.jobFlowViewSearchForm
                // 作业流名
                if (catchForm.hasOwnProperty('name')) {
                    this.searchForm.name = catchForm.name
                }
                // 计划开始时间
                if (catchForm.hasOwnProperty('eta')) {
                    this.searchForm.eta[0] = catchForm.eta[0]
                    this.searchForm.eta[1] = catchForm.eta[1]
                }
                // 实际开始时间
                if (catchForm.hasOwnProperty('start_time')) {
                    this.searchForm.start_time[0] = catchForm.start_time[0]
                    this.searchForm.start_time[1] = catchForm.start_time[1]
                }
                // 完成时间
                if (catchForm.hasOwnProperty('end_time')) {
                    this.searchForm.end_time[0] = catchForm.end_time[0]
                    this.searchForm.end_time[1] = catchForm.end_time[1]
                }
                // 作业总数
                if (catchForm.hasOwnProperty('total_job_count')) {
                    this.searchForm.total_job_count = catchForm.total_job_count
                }
                // 未执行作业数
                if (catchForm.hasOwnProperty('total_not_execute_job_count')) {
                    this.searchForm.total_not_execute_job_count = catchForm.total_not_execute_job_count
                }
                // 跑批系统
                if (catchForm.hasOwnProperty('category')) {
                    this.searchForm.category = catchForm.category
                }
                // 是否释放依赖
                if (catchForm.hasOwnProperty('is_release_dependency')) {
                    this.searchForm.is_release_dependency = catchForm.is_release_dependency
                }
                // 状态
                if (catchForm.hasOwnProperty('state')) {
                    this.searchForm.state = catchForm.state
                }
                // 使用midSearchForm来查询表格，为了避免轮询调接口因为v-model双向绑定searchForm引起用户未点击查询而表格也会根据当前条件获取
                this.midSearchForm = deepClone(this.searchForm)
            },
            handleLoad(first = false) {
                // 当前页面在等待操作结果，不做轮询
                if (this.opreateFlag) {
                    return false
                }
                // 判断是否首屏刷新
                if (first) {
                    this.tableLoading = true
                }
                const params = {
                    name: this.midSearchForm.name, // 作业流名
                    eta_gte: this.midSearchForm.eta[0], // 计划开始时间
                    eta_lte: this.midSearchForm.eta[1], // 计划开始时间
                    start_time_gte: this.midSearchForm.start_time[0], // 实际开始时间
                    start_time_lte: this.midSearchForm.start_time[1], // 实际开始时间
                    end_time_gte: this.midSearchForm.end_time[0], // 完成时间
                    end_time_lte: this.midSearchForm.end_time[1], // 完成时间
                    total_job_count: this.midSearchForm.total_job_count, // 作业总数
                    total_not_execute_job_count: this.midSearchForm.total_not_execute_job_count, // 未执行作业数
                    category: this.midSearchForm.category, // 跑批系统
                    is_release_dependency: this.midSearchForm.is_release_dependency, // 是否释放依赖
                    state: this.midSearchForm.state, // 状态
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }
                this.$api.processRun.list(params).then(res => {
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
    #jobFlowView {
        height: 100%;
        overflow: auto;

        .header {
            width: 100%;
            font-size: 0;
            float: left;
            margin-bottom: 20px;
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

                /deep/ .bk-table-empty-block {
                    background-color: #fff;
                }
            }
        }
    }
</style>
