<template>
    <div id="log">
        <div class="header" v-if="auth.search">
            <div class="search-item" style="width: 15%;">
                <span style="display: inline-block;flex-basis: 50px;">操作者</span>
                <bk-input v-model="searchForm.user" :clearable="true" placeholder="操作者"
                    style="flex: 1;margin-right: 16px;" :title="searchForm.user"></bk-input>
            </div>
            <div class="search-item" style="width: 17%;">
                <span style="display: inline-block;flex-basis: 60px;">操作对象</span>
                <bk-select class="header-select" :clearable="true"
                    style="background-color: #fff;flex: 1;margin-right: 16px;" v-model="searchForm.object_repr"
                    placeholder="请选择" :title="searchForm.object_repr">
                    <bk-option v-for="(item, index) in objectReprs" :key="index" :id="item.value" :name="item.name">
                    </bk-option>
                </bk-select>
            </div>
            <div class="search-item" style="width: 17%;">
                <span style="display: inline-block;flex-basis: 60px;">操作类型</span>
                <bk-select class="header-select" :clearable="true"
                    style="background-color: #fff;flex: 1;margin-right: 16px;" v-model="searchForm.action_flag"
                    placeholder="请选择" :title="searchForm.action_flag">
                    <bk-option v-for="(item, index) in actionFlags" :key="index" :id="item.value" :name="item.name">
                    </bk-option>
                </bk-select>
            </div>
            <div class="search-item" style="width: 24%;">
                <span style="display: inline-block;flex-basis: 60px;">开始时间</span>
                <bk-date-picker :value="searchForm.eta" :placeholder="'选择日期时间'" :type="'datetimerange'"
                    format="yyyy-MM-dd HH:mm:ss" style="flex: 1;margin-right: 16px;" :transfer="true"
                    @change="handleEtaChange" :title="searchForm.eta"></bk-date-picker>
            </div>
            <div class="search-item" style="width: 20%;">
                <bk-button @click="handleSearch" style="margin-right: 8px;" theme="primary">搜索</bk-button>
                <bk-button @click="handleReset">重置</bk-button>
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable" :max-height="maxTableHeight">
                <bk-table-column label="操作者" prop="user" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="操作对象" prop="object_repr" sortable>
                </bk-table-column>
                <bk-table-column label="操作类型" prop="action_flag" sortable>
                    <template slot-scope="props">
                        <span v-if="props.row.action_flag === 0">新增</span>
                        <span v-else-if="props.row.action_flag === 1">修改</span>
                        <span v-else-if="props.row.action_flag === 2">删除</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作时间" prop="action_time" :show-overflow-tooltip="true" sortable>
                </bk-table-column>
                <bk-table-column label="概要" prop="change_message" :show-overflow-tooltip="true"></bk-table-column>
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
                tableList: [],
                tableLoading: false,
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                searchForm: {
                    user: '', // 执行者
                    object_repr: '', // 操作对象
                    action_flag: '', // 操作类型
                    eta: ['', ''] // 开始时间
                },
                actionFlags: [{
                                  name: '新增',
                                  value: 0
                              },
                              {
                                  name: '修改',
                                  value: 1
                              },
                              {
                                  name: '删除',
                                  value: 2
                              }
                ],
                objectReprs: [{
                                  name: '作业',
                                  value: '作业'
                              },
                              {
                                  name: '作业流',
                                  value: '作业流'
                              },
                              {
                                  name: '系统设置',
                                  value: '系统设置'
                              },
                              {
                                  name: 'Agent',
                                  value: 'Agent'
                              },
                              {
                                  name: '变量表',
                                  value: '变量表'
                              },
                              {
                                  name: '日历',
                                  value: '日历'
                              },
                              {
                                  name: '系统类别',
                                  value: '系统类别'
                              },
                              {
                                  name: '用户',
                                  value: '用户'
                              }
                ]
            }
        },
        created() {
            this.handleLoad(true)
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            handleEtaChange(e) {
                this.searchForm.eta = e
            },
            // 处理重置
            handleReset() {
                this.searchForm = {
                    user: '', // 执行者
                    object_repr: '', // 操作对象
                    action_flag: '', // 操作类型
                    eta: ['', ''] // 开始时间
                }
            },
            // 处理搜索
            handleSearch() {
                this.pagination.current = 1
                this.handleLoad(false)
            },
            // 处理表格size切换
            handlePageLimitChange(val) {
                this.pagination.current = 1
                this.pagination.limit = val
                this.handleLoad(false)
            },
            // 处理页面跳转
            handlePageChange(page) {
                this.pagination.current = page
                this.handleLoad(false)
            },
            handleLoad(first) {
                this.tableLoading = true
                if (this.$route.query.hasOwnProperty('object_repr') && first) {
                    this.searchForm.object_repr = this.$route.query.object_repr
                }
                this.$api.auditLog.list({
                    user: this.searchForm.user,
                    action_flag: this.searchForm.action_flag,
                    action_time_gte: this.searchForm.eta[0],
                    action_time_lte: this.searchForm.eta[1],
                    object_repr: this.searchForm.object_repr,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }).then(res => {
                    if (res.result) {
                        this.pagination.count = res.data.count
                        this.tableList = res.data.items
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.tableLoading = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #log {
        padding: 20px;
        height: 100%;

        .header {
            width: 100%;
            font-size: 0;
            margin-bottom: 20px;
            float: left;
            display: flex;

            .search-item {
                display: flex;

                span {
                    display: inline-block;
                    height: 32px;
                    line-height: 32px;
                    font-size: 14px;
                    margin-right: 12px;
                }
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
