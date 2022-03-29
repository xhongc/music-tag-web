<template>
    <div id="jobList">
        <div class="header">
            <div style="float: left;">
                <bk-button theme="primary" @click="handleExportFiles">导出</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;margin-right: 8px;" :placeholder="'请输入作业名称'"
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
                                <bk-form-item label="作业名称:">
                                    <bk-input :placeholder="'请输入作业名称'" v-model="searchFrom.name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="Agent:">
                                    <bk-input :placeholder="'请输入Agent名称'" v-model="searchFrom.station_name" clearable>
                                    </bk-input>
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
                            <bk-col :span="6">
                                <bk-form-item label="IP:">
                                    <bk-input :placeholder="'请输入IP'" v-model="searchFrom.ip" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 20px;">
                            <bk-col :span="6">
                                <bk-form-item label="作业流名称:">
                                    <bk-input :placeholder="'请输入作业流名称'" v-model="searchFrom.process_name" clearable>
                                    </bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="创建人:">
                                    <bk-input :placeholder="'请输入创建人'" v-model="searchFrom.creator" clearable></bk-input>
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
                ext-cls="customTable" @select-all="handleSelectAll" @select="handleSelect" :size="setting.size" :max-height="maxTableHeight">
                <bk-table-column type="selection" width="60"></bk-table-column>
                <bk-table-column :label="item.label" :prop="item.id" v-for="(item, index) in setting.selectedFields"
                    :key="index" :show-overflow-tooltip="item.overflowTooltip" :sortable="item.sortable">
                    <template slot-scope="props">
                        <span
                            v-if="item.id !== 'name'">{{(props.row[item.id] === '' || props.row[item.id] === null) ? '- -' : props.row[item.id]}}</span>
                        <span v-else style="color: #3a84ff;cursor: pointer;"
                            @click="handleOpenDetail(props.row)">{{props.row[item.id]}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作" width="180">
                    <template slot-scope="props">
                        <div style="display: flex;align-items: center;">
                            <bk-button class="mr10" theme="primary" text @click="handleOpenUpdate(props.row)"
                                v-if="auth.modify">修改</bk-button>
                            <bk-button class="mr10" theme="primary" text @click="handleClone(props.row)" v-if="auth.modify">克隆
                            </bk-button>
                            <bk-button class="mr10" theme="primary" text @click="handleDelete(props.row)" v-if="auth.del">删除
                            </bk-button>
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
        <div>
            <bk-sideslider :is-show.sync="dialogShow" :quick-close="true" title="作业详情" :width="500" ext-cls="custom-sidelider">
                <div slot="content" style="height: 100%;">
                    <job-dialog :job-from="jobFrom" :key="dialogKey">
                    </job-dialog>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import jobDialog from './job_dialog.vue'
    export default {
        components: {
            jobDialog
        },
        data() {
            const fields = [{
                id: 'name',
                label: '作业名',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'template_type',
                label: '模板类型',
                overflowTooltip: true,
                sortable: false
            }, {
                id: 'description',
                label: '作业描述',
                overflowTooltip: true,
                sortable: false
            }]
            return {
                maxTableHeight: '',
                auth: {},
                dialogKey: 0,
                jobFrom: {},
                setting: {
                    size: 'small', // 表格大小
                    fields: fields, // 表格所有列
                    selectedFields: fields.slice(0, 8) // 表格当前显示列
                },
                tableLoading: false,
                tableList: [],
                runSysList: [], // 跑批系统下拉列表
                isDropdownShow: false,
                searchFrom: {
                    name: '', // 作业名称
                    station_name: '', // agent
                    category: '', // 跑批系统
                    ip: '', // ip
                    process_name: '', // 作业流名称
                    creator: '' // 创建人
                },
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                selectionList: [], // 表格多选
                dialogShow: false
            }
        },
        created() {
            this.handleLoad()
            this.getRunSysList()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            handleJumpHistory(row) {
                this.$store.commit('changeTabActive', 'jobviewhistory')
                this.$router.push({
                    path: '/jobviewhistory',
                    query: {
                        job_id: row.id
                    }
                })
            },
            // 处理克隆作业
            handleClone(row) {
                this.$router.push({
                    path: '/singlejob',
                    query: {
                        type: 'clone',
                        job_id: row.id
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
            // 处理执行
            handleImplement(row) {
                this.$bkInfo({
                    title: '确认要执行吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.tableLoading = true
                        this.$api.content.execute({
                            id: row.id
                        }).then(res => {
                            if (res.result) {
                                this.$cwMessage('执行成功!', 'success')
                                this.$store.commit('changeTabActive', 'jobview')
                                this.$router.push({
                                    path: '/jobview'
                                })
                            } else {
                                this.$cwMessage(res.message, 'error')
                            }
                            this.tableLoading = false
                        })
                    }
                })
            },
            // 处理打开详情
            handleOpenDetail(row) {
                this.dialogKey += 1
                this.jobFrom = row
                this.dialogShow = true
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
                window.open(window.siteUrl + '/export/content/?id=' + ids.join(','))
            },
            // 处理跳转修改
            handleOpenUpdate(row) {
                this.$router.push({
                    path: '/singlejob',
                    query: {
                        type: 'update',
                        job_id: row.id
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
                        this.$api.content.delete(row.id).then(res => {
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
            // 获取跑批系统
            getRunSysList() {
                this.$api.category.list().then(res => {
                    if (res.result) {
                        this.runSysList = res.data.items
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                })
            },
            // 处理搜索重置
            handleReset() {
                this.searchFrom = {
                    name: '', // 作业名称
                    station_name: '', // agent
                    category: '', // 跑批系统
                    ip: '', // ip
                    process_name: '', // 作业流名称
                    creator: '' // 创建人
                }
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
                // this.handleReset()
            },
            // 处理表格size切换
            handlePageLimitChange(val) {
                this.pagination.current = 1
                this.pagination.limit = val
                this.handleLoad()
            },
            // 处理查找
            handleSearch() {
                this.pagination.current = 1
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
                this.$api.content.list({
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
    #jobList {
        padding: 20px;
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
        .custom-sidelider {
            /deep/ .bk-sideslider-wrapper {
                overflow-y: hidden;
            }
        }
    }
</style>
