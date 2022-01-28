<template>
    <div id="calendarMgmt">
        <div class="header" style="display: flex;justify-content: space-between;">
            <div style="float: left;width: 20%;">
                <bk-button @click="createCalendar" v-if="auth.create" theme="primary" style="margin-right: 8px;">新增日历</bk-button>
                <bk-button @click="handleExportFiles">导出</bk-button>
            </div>
            <div style="float: right;display: flex;" v-if="auth.search">
                <div class="search-item">
                    <span style="display: inline-block;flex-basis: 60px;">日历名称</span>
                    <bk-input v-model="searchForm.name" placeholder="请输入日历名称" style="flex: 1;margin-right: 16px;"
                        clearable></bk-input>
                </div>
                <div class="search-item">
                    <span style="display: inline-block;flex-basis: 50px;">创建人</span>
                    <bk-input v-model="searchForm.creator" placeholder="请输入创建人" style="flex: 1;margin-right: 16px;"
                        clearable></bk-input>
                </div>
                <div class="search-item">
                    <span style="display: inline-block;flex-basis: 60px;">创建时间</span>
                    <bk-date-picker :placeholder="'选择日期时间'" :type="'datetimerange'" format="yyyy-MM-dd HH:mm:ss" style="flex: 1;margin-right: 16px;"
                        :transfer="true" @change="handleCreateTimeChange" :shortcuts="shortcuts" :value="searchForm.create_time" :title="searchForm.create_time"></bk-date-picker>
                </div>
                <div class="search-item">
                    <bk-button @click="handleSearch" style="margin-right: 8px;" theme="primary">搜索</bk-button>
                    <bk-button @click="handleReset">重置</bk-button>
                </div>
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" @select-all="handleSelectAll" @select="handleSelect"
                v-bkloading="{ isLoading: tableLoading, zIndex: 10 }" ext-cls="customTable" :max-height="maxTableHeight">
                <bk-table-column type="selection" width="60"></bk-table-column>
                <bk-table-column label="日历名" prop="name" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span style="color: #3a84ff;cursor: pointer;" @click="calendarDetail(props.row)">{{props.row.name}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="日历描述" prop="description" sortable></bk-table-column>
                <bk-table-column label="关联作业流数" prop="total_process_num" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="创建时间" prop="create_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="创建人" prop="creator" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="上次修改时间" prop="edit_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="修改人" prop="editor" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{(props.row.editor !== '' && props.row.editor !== null) ? props.row.editor : '- -'}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作" width="150">
                    <template slot-scope="props">
                        <bk-button class="mr10" theme="primary" text @click="calendarUpdate(props.row)" v-if="auth.modify">修改</bk-button>
                        <bk-button class="mr10" theme="primary" text @click="calendarDel(props.row)" v-if="auth.del">删除</bk-button>
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
                selectionList: [],
                tableList: [],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                tableLoading: false,
                searchForm: {
                    name: '',
                    create_time: ['', ''],
                    creator: ''
                },
                shortcuts: [{
                    text: '最近一周',
                    value() {
                        const end = new Date()
                        const start = new Date()
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                        return [start, end]
                    }
                }, {
                    text: '最近一个月',
                    value() {
                        const end = new Date()
                        const start = new Date()
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                        return [start, end]
                    }
                }, {
                    text: '最近三个月',
                    value() {
                        const end = new Date()
                        const start = new Date()
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
                        return [start, end]
                    }
                }],
                form: {
                    description: '',
                    name: '',
                    date: ''
                }
            }
        },
        created() {
            this.handleLoad()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            handleReset() {
                this.searchForm = {
                    name: '',
                    create_time: ['', ''],
                    creator: ''
                }
            },
            // 日历详情
            calendarDetail(row) {
                this.$router.push({
                    path: '/addcalendarmgmt',
                    query: {
                        type: 'detail',
                        name: row.name
                    }
                })
                // this.form = {
                //     name: row.name,
                //     description: row.description,
                //     date: row.date,
                //     quick: row.quick
                // }
                // this.$router.push({
                //     name: 'AddCalendarMgmt',
                //     params: {
                //         isDetail: true,
                //         form: this.form
                //     }
                // })
            },
            // 日历修改
            calendarUpdate(row) {
                this.$router.push({
                    path: '/addcalendarmgmt',
                    query: {
                        type: 'update',
                        id: row.id,
                        name: row.name
                    }
                })
                // this.form = {
                //     id: row.id,
                //     name: row.name,
                //     description: row.description,
                //     date: row.date,
                //     quick: row.quick
                // }
                // this.$router.push({
                //     name: 'AddCalendarMgmt',
                //     params: {
                //         isEdit: true,
                //         form: this.form
                //     }
                // })
            },
            // 删除日历
            calendarDel(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.$api.calendar.delete(row.id).then(res => {
                            if (res.result) {
                                this.$bkMessage({
                                    message: '删除成功',
                                    theme: 'success'
                                })
                                if (this.tableList.length === 1 && this.pagination.current !== 1) {
                                    this.pagination.current -= 1
                                }
                                this.handleLoad()
                            } else {
                                this.$bkMessage({
                                    message: res.message,
                                    theme: 'error'
                                })
                            }
                        })
                    }
                })
            },
            // 新增日历
            createCalendar() {
                this.$router.push({
                    path: '/addcalendarmgmt',
                    query: {
                        type: 'add'
                    }
                })
                // this.$router.push({
                //     name: 'AddCalendarMgmt',
                //     params: {
                //         isDetail: false,
                //         isEdit: false,
                //         isAdd: true
                //     }
                // })
            },
            handleCreateTimeChange(e) {
                this.searchForm.create_time = e
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
                window.open(window.siteUrl + '/export/calendar/?id=' + ids.join(','))
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
                    'name': this.searchForm.name, // 日历名
                    'creator': this.searchForm.creator, // 创建者
                    'create_time_gte': this.searchForm.create_time[0], // 开始时间
                    'create_time_lte': this.searchForm.create_time[1], // 结束时间
                    'page': this.pagination.current, // 当前页码
                    'page_size': this.pagination.limit // 每页展示条数
                }
                this.$api.calendar.list(params).then(res => {
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
    #calendarMgmt {
        padding: 20px;
        height: 100%;
        overflow: hidden;

        .header {
            width: 100%;
            font-size: 0;
            margin-bottom: 20px;
            float: left;

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
