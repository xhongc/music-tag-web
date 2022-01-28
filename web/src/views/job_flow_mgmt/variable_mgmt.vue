<template>
    <div id="varMgmt">
        <div class="header">
            <div style="float: left;">
                <bk-button theme="primary" style="margin-right: 8px;" @click="handleOpenAdd" v-if="auth.create">新增变量表</bk-button>
                <bk-button @click="handleExportFiles">导出</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;" :placeholder="'请输入变量表名'" :right-icon="'bk-icon icon-search'"
                    v-model="searchData" @right-icon-click="handleSearch" @enter="handleSearch">
                </bk-input>
                <!-- <bk-button @click="handleSearch">搜索</bk-button> -->
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable" @select-all="handleSelectAll" @select="handleSelect" :max-height="maxTableHeight">
                <bk-table-column type="selection" width="60"></bk-table-column>
                <bk-table-column label="变量表" prop="name" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span style="color: #3a84ff;cursor: pointer;" @click="handleOpenDetail(props.row)">{{props.row.name}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="描述" prop="description" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="关联的作业流" prop="processes" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.processes.length > 0 ? props.row.processes.join(',') : '- -'}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="变量总数" prop="total_var_num" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="创建时间" prop="create_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="操作" width="150">
                    <template slot-scope="props">
                        <bk-button class="mr10" theme="primary" text @click="handleOpenUpdate(props.row)" v-if="auth.modify">修改</bk-button>
                        <bk-button class="mr10" theme="primary" text @click="handleDelete(props.row)" v-if="auth.del">删除</bk-button>
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
                searchData: '',
                tableList: [],
                selectionList: [],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                }
            }
        },
        created() {
            this.handleLoad()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            // 处理打开详情
            handleOpenDetail(row) {
                this.$router.push({
                    path: '/variablechange',
                    query: {
                        type: 'detail',
                        id: row.id
                    }
                })
            },
            // 处理打开修改
            handleOpenUpdate(row) {
                this.$router.push({
                    path: '/variablechange',
                    query: {
                        type: 'update',
                        id: row.id
                    }
                })
            },
            // 处理跳转新增变量表
            handleOpenAdd() {
                this.$router.push({
                    path: '/variablechange',
                    query: {
                        type: 'add'
                    }
                })
            },
            // 处理导出
            handleExportFiles() {
                if (this.selectionList.length === 0) {
                    return this.$cwMessage('至少选择一条数据！', 'warning')
                }
                const ids = []
                // 数组去重
                this.selectionList.forEach(item => {
                    if (ids.indexOf(item.id) < 0) {
                        ids.push(item.id)
                    }
                })
                window.open(window.siteUrl + '/export/var_table/?id=' + ids.join(','))
            },
            // 处理删除表量表
            handleDelete(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.tableLoading = true
                        this.$api.varTable.delete(row.id).then(res => {
                            if (res.result) {
                                this.$cwMessage('删除成功！', 'success')
                                if (this.tableList.length === 1 && this.pagination.current !== 1) {
                                    this.pagination.current -= 1
                                }
                                this.handleLoad()
                            } else {
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
            // 处理搜索
            handleSearch() {
                this.pagination.current = 1
                this.handleLoad()
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
            // 处理表格默认选择
            defaultCheck() {
                this.$nextTick(() => {
                    this.selectionList.forEach(item1 => {
                        this.tableList.forEach(item2 => {
                            if (item1.id === item2.id) {
                                this.$refs.table.toggleRowSelection(item2, true)
                            }
                        })
                    })
                })
            },
            handleLoad() {
                this.tableLoading = true
                const params = {
                    name: this.searchData,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }
                this.$api.varTable.list(params).then(res => {
                    if (res.result) {
                        this.tableList = res.data.items
                        this.pagination.count = res.data.count
                        if (this.selectionList.length > 0) {
                            this.defaultCheck()
                        }
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
    #varMgmt {
        padding: 20px;
        height: 100%;
        overflow: hidden;

        .header {
            width: 100%;
            font-size: 0;
            margin-bottom: 20px;
            float: left;
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
