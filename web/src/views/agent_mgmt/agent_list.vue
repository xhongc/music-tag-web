<template>
    <div id="agentList">
        <div class="header" v-if="auth.create || auth.search">
            <div style="float: left;" v-if="auth.create">
                <bk-button theme="primary" @click="handleOpenDialog('新增Agent', {})">新增Agent</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable
                    width="240px"
                    style="width: 240px;margin-right: 8px;"
                    :placeholder="'请输入Agent名称'"
                    :right-icon="'bk-icon icon-search'"
                    v-model="searchFrom.name"
                    @right-icon-click="handleSearch"
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
                                <bk-form-item label="Agent:">
                                    <bk-input :placeholder="'请输入Agent'" v-model="searchFrom.name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="IP:">
                                    <bk-input :placeholder="'请输入IP'" v-model="searchFrom.ip" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="跑批系统:">
                                    <bk-select class="header-select"
                                        :clearable="true"
                                        style="background-color: #fff;"
                                        v-model="searchFrom.category">
                                        <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id"
                                            :name="item.name">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="操作系统:">
                                    <bk-input :placeholder="'请输入操作系统'" v-model="searchFrom.os" clearable></bk-input>
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
            <bk-table ref="table"
                :data="tableList"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange"
                v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable"
                :max-height="maxTableHeight">
                <bk-table-column label="Agent名称" prop="name" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="IP" prop="ip" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="所属业务" prop="biz_name" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="跑批系统" prop="category" sortable :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span
                            v-if="runSysList.length">{{runSysList.find(item => item.id === props.row.category).name}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作系统" prop="os" sortable :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.os === '' ? '- -' : props.row.os}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="作业并发限制" prop="max_concurrency" sortable :show-overflow-tooltip="true">
                </bk-table-column>
                <bk-table-column label="Agent添加时间" prop="create_time" sortable :show-overflow-tooltip="true">
                </bk-table-column>
                <bk-table-column label="操作" v-if="auth.del || auth.modify">
                    <template slot-scope="props">
                        <bk-button text @click="handleOpenDialog('修改Agent', props.row)" v-if="auth.modify">修改
                        </bk-button>
                        <bk-button style="margin-left: 10px;" text @click="handleDelete(props.row)" v-if="auth.del">删除
                        </bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
        <div>
            <bk-dialog v-model="dialogShow"
                theme="primary"
                :mask-close="false"
                header-position="left"
                :title="dialogTitle"
                :show-footer="true"
                :position="{ top: 50 }"
                :draggable="false"
                width="500"
                @confirm="handleConfim"
                :loading="dialogLoading"
                :close-icon="closeIconShow">
                <agent-dialog @close-dialog="handleCloseDialog"
                    :key="dialogKey"
                    :operation-flag="operationFlag"
                    :agent-from="agentFrom"
                    ref="agentDialog">
                </agent-dialog>
            </bk-dialog>
        </div>
    </div>
</template>

<script>
    import agentDialog from './agent_dialog.vue'
    export default {
        components: {
            agentDialog
        },
        data() {
            return {
                maxTableHeight: '',
                auth: {},
                agentFrom: {},
                operationFlag: '', // 判断是以何种方式打开弹窗
                dialogKey: 0, // 用以刷新弹窗组件的key
                dialogTitle: '', // 弹窗标题
                dialogShow: false,
                dialogLoading: false,
                closeIconShow: true,
                tableLoading: false,
                searchFrom: {
                    name: '', // agent名称
                    ip: '', // ip
                    category: '', // 跑批系统
                    os: '' // 操作系统
                },
                tableList: [],
                runSysList: [], // 跑批下拉列表
                isDropdownShow: false,
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                }
            }
        },
        created() {
            this.handleLoad()
            this.getRunSysList()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            // 处理确认
            handleConfim() {
                this.dialogLoading = true
                this.$refs.agentDialog.$refs.form.validate().then(validator => {
                    let nowHostData = {}
                    this.$refs.agentDialog.hostList.some(item => {
                        nowHostData = item
                        return item.bk_host_innerip === this.$refs.agentDialog.form.ip
                    })
                    if (this.operationFlag === '新增Agent') {
                        this.$refs.agentDialog.handleAddAgent(nowHostData)
                    } else {
                        this.$refs.agentDialog.handleUpdateAgent(nowHostData)
                    }
                }).catch(e => {
                    this.$cwMessage('输入有误, 请检查您的输入！', 'warning')
                    this.dialogLoading = false
                })
            },
            handleCloseDialog(flag) {
                if (flag) {
                    this.handleLoad()
                }
                this.dialogShow = false
            },
            // 处理删除
            handleDelete(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.$api.station.delete(row.id).then(res => {
                            if (res.result) {
                                this.$cwMessage('删除成功！', 'success')
                                if (this.tableList.length === 1 && this.pagination.current !== 1) {
                                    this.pagination.current -= 1
                                }
                                this.handleLoad()
                            } else {
                                this.$cwMessage(res.message, 'error')
                            }
                        })
                    }
                })
            },
            // 获取跑批系统
            getRunSysList() {
                this.runSysList = []
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
            handleLoad() {
                this.tableLoading = true
                this.$api.station.list({
                    ...this.searchFrom,
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
            },
            // 处理表单重置
            handleReset() {
                this.searchFrom = {
                    name: '', // agent名称
                    ip: '', // ip
                    category: '', // 跑批系统
                    os: '' // 操作系统
                }
            },
            // 处理查找
            handleSearch() {
                this.pagination.current = 1
                this.handleLoad()
            },
            // 处理打开dialog
            handleOpenDialog(str, row) {
                this.agentFrom = row
                this.operationFlag = str
                // dialogKey用于刷新组件
                this.dialogKey += 1
                this.dialogShow = true
                this.dialogTitle = str
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
            }
        }
    }
</script>

<style lang="scss" scoped>
    #agentList {
        padding: 20px;
        height: 100%;

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
            }
        }
    }
</style>
