<template>
    <div id="jobFlowList">
        <div class="header">
            <div style="float: left;">
                <bk-button theme="primary" @click="handleExportFiles">导出</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;margin-right: 8px;" :placeholder="'请输入作业流名称'"
                    :right-icon="'bk-icon icon-search'" v-model="searchFrom.name" @right-icon-click="handleSearch"
                    @enter="handleSearch">
                </bk-input>
                <bk-button slot="dropdown-trigger" :theme="isDropdownShow === true ? 'primary' : 'default'"
                    @click="handleOpenSeniorSearch"
                    :icon-right="isDropdownShow === true ? 'angle-double-up' : 'angle-double-down'">高级搜索</bk-button>
            </div>
            <div class="senior-search-box" v-if="isDropdownShow">
                <bk-container :margin="0">
                    <bk-form :label-width="100">
                        <bk-row>
                            <bk-col :span="6">
                                <bk-form-item label="作业流名称:">
                                    <bk-input :placeholder="'请输入作业流名称'" v-model="searchFrom.name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="创建人:">
                                    <bk-input :placeholder="'请输入创建人'" v-model="searchFrom.creator" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="跑批系统:">
                                    <bk-select class="header-select" :clearable="true" style="background-color: #fff;"
                                        v-model="searchFrom.category">
                                        <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id"
                                            :name="item.name">
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
                ext-cls="customTable" @select-all="handleSelectAll" @select="handleSelect" :size="setting.size"
                :max-height="maxTableHeight">
                <bk-table-column type="selection" width="60"></bk-table-column>
                <bk-table-column :label="item.label" :prop="item.id" v-for="(item, index) in setting.selectedFields"
                    :key="index" :show-overflow-tooltip="item.overflowTooltip" :sortable="item.sortable">
                    <template slot-scope="props">
                        <div v-if="item.id !== 'type' && item.id !== 'name' && item.id !== 'cross_day_dependence'">
                            {{(props.row[item.id] === '' || props.row[item.id] === null) ? '- -' : props.row[item.id]}}
                        </div>
                        <div v-else-if="item.id === 'type'">
                            <span v-if="props.row.type === 'null'">无</span>
                            <span v-else-if="props.row.type === 'calendar'">日历</span>
                            <span v-else-if="props.row.type === 'time'">定时</span>
                            <span v-else-if="props.row.type === 'cycle'">周期</span>
                        </div>
                        <div v-else-if="item.id === 'name'" style="color: #3a84ff;cursor: pointer;"
                            @click="handleOpenDetail(props.row)">{{props.row[item.id]}}</div>
                        <div v-else-if="item.id === 'cross_day_dependence'">
                            <span>{{props.row[item.id] === true ? '是' : '否'}}</span>
                        </div>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作" width="180">
                    <template slot-scope="props">
                        <div style="display: flex;align-items: center;">
                            <bk-button class="mr10" theme="primary" text @click="handleImplement(props.row)"
                                v-if="auth.operate">新建任务</bk-button>
                            <bk-button class="mr10" theme="primary" text @click="handleOpenUpdate(props.row)"
                                v-if="auth.modify">修改</bk-button>
                            <bk-button class="mr10" theme="primary" text @click="handleDelete(props.row)"
                                v-if="auth.del">删除</bk-button>
                            <bk-popover ext-cls="dot-menu" placement="bottom-start" theme="dot-menu light"
                                trigger="click" :arrow="false" :distance="0" offset="15">
                                <span class="dot-menu-trigger"></span>
                                <ul class="dot-menu-list" slot="content">
                                    <li class="dot-menu-item" v-if="auth.modify" @click="handleClone(props.row)">克隆</li>
                                    <li class="dot-menu-item" @click="handleJumpHistory(props.row)">执行历史</li>
                                </ul>
                            </bk-popover>
                        </div>
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
    export default {
        data() {
            const fields = [{
                id: 'name',
                label: '作业流名',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'var_table',
                label: '变量表',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'run_type',
                label: '调度方式',
                overflowTooltip: false,
                sortable: true
            }, {
                id: 'category',
                label: '分类',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'create_by',
                label: '创建者',
                overflowTooltip: false,
                sortable: false
            }, {
                id: 'create_time',
                label: '创建时间',
                overflowTooltip: true,
                sortable: true
            }, {
                id: 'update_time',
                label: '更新时间',
                overflowTooltip: true,
                sortable: true
            }, {
                id: 'total_run_count',
                label: '执行次数',
                overflowTooltip: false,
                sortable: true
            }, {
                id: 'description',
                label: '作业流描述',
                overflowTooltip: true,
                sortable: false
            }]
            return {
                maxTableHeight: '',
                auth: {},
                tableList: [],
                tableLoading: false,
                runSysList: [], // 跑批系统下拉列表
                selectionList: [], // 表格多选
                searchFrom: {
                    name: '', // 作业流名称
                    creator: '', // 创建人
                    category: '' // 跑批系统id
                },
                isDropdownShow: false,
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                setting: {
                    size: 'small', // 表格大小
                    fields: fields, // 表格所有列
                    selectedFields: fields.slice(0, 8) // 表格当前显示列
                }
            }
        },
        created() {
            this.getRunSysList()
            this.handleLoad()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            // 处理克隆
            handleClone(row) {
                this.$router.push({
                    path: '/singlejobflow',
                    query: {
                        job_flow_data: row.id,
                        type: 'clone'
                    }
                })
            },
            // 处理删除
            handleDelete(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.tableLoading = true
                        this.$api.process.delete(row.id).then(res => {
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
            // 处理跳转查看历史
            handleJumpHistory(row) {
                this.$store.commit('changeTabActive', 'jobflowviewhistory')
                this.$router.push({
                    path: '/jobflowviewhistory',
                    query: {
                        job_flow_id: row.id
                    }
                })
            },
            // 处理表格字段显隐
            handleSettingChange({
                fields,
                size
            }) {
                this.setting.size = size
                this.setting.selectedFields = fields
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
            // 处理执行
            handleImplement(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要执行吗？',
                    confirmLoading: false,
                    confirmFn: () => {
                        this.$router.push({
                            path: '/taskCreate',
                            query: {
                                job_flow_data: row.id,
                                type: 'detail'
                            }
                        })
                    }
                })
            },
            // 处理打开修改
            handleOpenUpdate(row) {
                this.$router.push({
                    path: '/singlejobflow',
                    query: {
                        job_flow_data: row.id,
                        type: 'update'
                    }
                })
            },
            // 处理打开详情
            handleOpenDetail(row) {
                this.$router.push({
                    path: '/singlejobflow',
                    query: {
                        job_flow_data: row.id,
                        type: 'detail'
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
                window.open(window.siteUrl + '/export/process/?id=' + ids.join(','))
            },
            // 处理搜索
            handleSearch() {
                this.pagination.current = 1
                this.handleLoad()
            },
            // 处理搜索重置
            handleReset() {
                this.searchFrom = {
                    name: '', // 作业流名称
                    creator: '', // 创建人
                    category: '' // 跑批系统id
                }
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
                // this.handleReset()
            },
            // 获取跑批系统下拉列表
            getRunSysList() {
                this.runSysList = []
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
                this.$api.process.list({
                    ...this.searchFrom,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }).then(res => {
                    if (res.result) {
                        this.pagination.count = res.data.count
                        this.tableList = res.data.items
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

<style lang="scss">
    .dot-menu {
        display: inline-block;
        vertical-align: middle;

        .tippy-tooltip.dot-menu-theme {
            padding: 0;
        }
    }

    .dot-menu-list {
        margin: 0;
        padding: 5px 0;
        min-width: 50px;
        list-style: none;
    }

    .dot-menu-list .dot-menu-item {
        padding: 0 10px;
        font-size: 12px;
        line-height: 26px;
        cursor: pointer;
        text-align: center;

        &:hover {
            background-color: #eaf3ff;
            color: #3a84ff;
        }
    }
</style>
<style lang="scss" scoped>
    #jobFlowList {
        padding: 20px;
        height: 100%;
        overflow: auto;

        .header {
            width: 100%;
            font-size: 0;
            float: left;
            margin-bottom: 20px;
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

                .dot-menu-trigger {
                    display: block;
                    width: 20px;
                    height: 20px;
                    line-height: 20px;
                    border-radius: 50%;
                    text-align: center;
                    font-size: 0;
                    cursor: pointer;
                }

                .dot-menu-trigger:hover {
                    color: #3A84FF;
                    background-color: #DCDEE5;
                }

                .dot-menu-trigger:before {
                    content: "";
                    display: inline-block;
                    width: 3px;
                    height: 3px;
                    border-radius: 50%;
                    background-color: currentColor;
                    box-shadow: 0 -4px 0 currentColor, 0 4px 0 currentColor;
                }
            }
        }
    }
</style>
