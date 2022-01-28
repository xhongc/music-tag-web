<template>
    <div id="jobViewHistory">
        <div class="header" v-if="auth.search">
            <div style="float: left;">
                <bk-input clearable width="240px" style="width: 240px;margin-right: 8px;" :placeholder="'请输入作业名称'"
                    :right-icon="'bk-icon icon-search'" v-model="searchFrom.name" @right-icon-click="handleSearch"
                    @enter="handleSearch">
                </bk-input>
                <bk-button slot="dropdown-trigger" :theme="isDropdownShow === true ? 'primary' : 'default'" @click="handleOpenSeniorSearch"
                    :icon-right="isDropdownShow === true ? 'angle-double-up' : 'angle-double-down'">高级搜索</bk-button>
            </div>
            <div class="senior-search-box" v-if="isDropdownShow">
                <bk-container :margin="0">
                    <bk-form :label-width="100">
                        <bk-row>
                            <bk-col :span="6">
                                <bk-form-item label="作业名:">
                                    <bk-input :placeholder="'请输入作业名称'" v-model="searchFrom.name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="执行者:">
                                    <bk-input :placeholder="'请输入执行者'" v-model="searchFrom.executor" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="状态:">
                                    <bk-select class="header-select" :clearable="true" style="background-color: #fff;"
                                        v-model="searchFrom.state">
                                        <bk-option v-for="(item, index) in stateList" :key="index" :id="item.name"
                                            :name="item.label">
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
            <!--                                :sortable="item.sortable" -->
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable" :max-height="maxTableHeight">
                <bk-table-column label="作业名" prop="name" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span style="color: #3a84ff;cursor: pointer;" @click="handleCheckDetail(props.row)">{{props.row.name}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="所属作业流名" prop="process" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="状态" prop="state">
                    <template slot-scope="props">
                        <span>{{stateList[stateList.findIndex(e => e.name === props.row.state)].label}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="Agent" prop="station" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="计划开始时间" prop="eta" :show-overflow-tooltip="true" sortable>
                    <template slot-scope="props">
                        <span>{{props.row.eta === '' ? '- -' : props.row.eta}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="执行者" prop="executor" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="实际开始时间" prop="start_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="完成时间" prop="end_time" :show-overflow-tooltip="true" sortable></bk-table-column>
            </bk-table>
        </div>
    </div>
</template>

<script>
    import {
        mapGetters
    } from 'vuex'
    export default {
        data() {
            return {
                maxTableHeight: '',
                auth: {},
                tableLoading: false,
                tableList: [],
                isDropdownShow: false,
                searchFrom: {
                    name: '', // 作业名
                    executor: '', // 执行者
                    state: '' // 状态
                },
                stateList: [{
                                id: 5,
                                name: 'success',
                                label: '成功'
                            },
                            {
                                id: 7,
                                name: 'cancel',
                                label: '取消'
                            }
                ],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                }
            }
        },
        computed: mapGetters(['jobHistorySearchForm']),
        created() {
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 143
            this.initSearch()
            this.handleLoad()
        },
        methods: {
            handleCheckDetail(row) {
                this.$router.push({
                    path: '/jobviewdetail',
                    query: {
                        id: row.id
                    }
                })
            },
            // 处理表格size切换
            handlePageLimitChange(val) {
                this.pagination.current = 1
                this.pagination.limit = val
                this.handleLoad()
            },
            // 处理页面跳转
            handlePageChange(page) {
                this.pagination.current = page
                this.handleLoad()
            },
            // 处理搜索重置
            handleReset() {
                this.searchFrom = {
                    name: '', // 作业名
                    executor: '', // 执行者
                    state: '' // 状态
                }
            },
            // 搜索值初始化
            initSearch() {
                const catchForm = this.jobHistorySearchForm
                if (catchForm.hasOwnProperty('name')) {
                    this.searchFrom.name = catchForm.name
                }
                if (catchForm.hasOwnProperty('executor')) {
                    this.searchFrom.executor = catchForm.executor
                }
                if (catchForm.hasOwnProperty('state')) {
                    this.searchFrom.state = catchForm.state
                }
            },
            handleLoad() {
                this.tableLoading = true
                const data = {
                    name: this.searchFrom.name,
                    executor: this.searchFrom.executor,
                    state: this.searchFrom.state,
                    content_id: this.$route.query.hasOwnProperty('job_id') ? this.$route.query.job_id : '',
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }
                if (this.$route.query.job_flow_id) {
                    data['process_history'] = this.$route.query.job_flow_id
                }
                this.$api.nodeHistory.list(data).then(res => {
                    if (res.result) {
                        this.pagination.count = res.data.count
                        this.tableList = res.data.items
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.tableLoading = false
                })
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
                // this.handleReset()
            },
            // 处理查询
            handleSearch() {
                // 更新缓存
                this.$store.commit('getJobHistorySearch', this.searchFrom)
                this.pagination.current = 1
                this.handleLoad()
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobViewHistory {
        // padding: 20px;
        height: 100%;
        overflow: auto;

        .header {
            width: 100%;
            font-size: 0;
            margin-bottom: 20px;
            float: left;
            // position: relative;

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
