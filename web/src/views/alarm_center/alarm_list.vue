<template>
    <div id="alarmList">
        <div class="header" v-if="auth.search">
            <div style="float: left;">
                <bk-input clearable width="240px" style="width: 240px;margin-right: 8px;" :placeholder="'请输入Agent'"
                    :right-icon="'bk-icon icon-search'" v-model="searchForm.station" @right-icon-click="handleSearch"
                    @enter="handleSearch">
                </bk-input>
                <bk-button slot="dropdown-trigger" :theme="isDropdownShow === true ? 'primary' : 'default'" @click="handleOpenSeniorSearch"
                    :icon-right="isDropdownShow === true ? 'angle-double-up' : 'angle-double-down'">高级搜索</bk-button>
            </div>
            <div class="senior-search-box" v-if="isDropdownShow">
                <bk-container :margin="0">
                    <bk-form :label-width="120">
                        <bk-row>
                            <bk-col :span="6">
                                <bk-form-item label="Agent:">
                                    <bk-input :placeholder="'请输入Agent'" v-model="searchForm.station" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="告警类别:">
                                    <bk-select class="header-select" :clearable="true" style="background-color: #fff;"
                                        v-model="searchForm.type">
                                        <bk-option v-for="(item, index) in alarmTypeList" :key="index" :id="item.name"
                                            :name="item.name">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="跑批系统:">
                                    <bk-select class="header-select" :clearable="true" style="background-color: #fff;"
                                        v-model="searchForm.category">
                                        <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.name"
                                            :name="item.name">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="ip:">
                                    <bk-input :placeholder="'请输入Agent'" v-model="searchForm.ip" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 24px;">
                            <bk-col :span="6">
                                <bk-form-item label="告警时间:">
                                    <bk-date-picker :value="searchForm.create_time" :placeholder="'选择日期时间范围'" :type="'datetimerange'"
                                        format="yyyy-MM-dd HH:mm:ss" style="width: 100%;" :transfer="true" @change="handleCreatTimeChange"></bk-date-picker>
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
                ext-cls="customTable" :max-height="maxTableHeight">
                <bk-table-column label="告警名称" prop="name" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="告警类别" prop="type"></bk-table-column>
                <bk-table-column label="告警时间" prop="create_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="Agent" prop="station" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="IP" prop="ip" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="通知人" prop="receivers" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.receivers === '' ? '- -' : props.row.receivers}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="跑批系统" prop="category" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="告警事件" prop="message" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.message === '' ? '- -' : props.row.message}}</span>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                maxTableHeight: '',
                auth: {},
                tableLoading: false,
                tableList: [],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                isDropdownShow: false,
                searchForm: {
                    station: '', // agent
                    type: '', // 告警类别
                    create_time: ['', ''], // 告警时间
                    ip: '', // ip
                    category: '' // 跑批系统id
                },
                runSysList: [],
                alarmTypeList: [{
                    name: 'Agent'
                }, {
                    name: '作业'
                }]
            }
        },
        created() {
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
            this.handleLoad()
            this.getRunSysList()
        },
        methods: {
            handleCreatTimeChange(e) {
                this.searchForm.create_time = e
            },
            // 处理表格size切换
            handlePageLimitChange(val) {
                this.pagination.current = 1
                this.pagination.limit = val
                // 首屏刷新
                this.handleLoad()
            },
            // 处理页面跳转
            handlePageChange(page) {
                this.pagination.current = page
                // 首屏刷新
                this.handleLoad()
            },
            // 处理重置
            handleReset() {
                this.searchForm = {
                    station: '', // agent
                    type: '', // 告警类别
                    create_time: ['', ''], // 告警时间
                    ip: '', // ip
                    category: '' // 跑批系统id
                }
            },
            // 处理搜索
            handleSearch() {
                this.pagination.current = 1
                this.handleLoad()
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
                // this.handleReset()
            },
            handleLoad() {
                this.tableLoading = true
                this.$api.alarmCenter.list({
                    type: this.searchForm.type,
                    station: this.searchForm.station,
                    create_time_gte: this.searchForm.create_time[0],
                    create_time_lte: this.searchForm.create_time[1],
                    ip: this.searchForm.ip,
                    category: this.searchForm.category,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }).then(res => {
                    if (res.result) {
                        this.tableList = res.data.items
                        this.pagination.count = res.data.count
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.tableLoading = false
                })
            },
            // 获取跑批下拉列表
            getRunSysList() {
                this.runSysList = []
            }
        }
    }
</script>

<style lang="scss" scoped>
    #alarmList {
        height: 100%;
        overflow: auto;
        padding: 20px;

        .header {
            width: 100%;
            margin-bottom: 20px;
            font-size: 0;
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
