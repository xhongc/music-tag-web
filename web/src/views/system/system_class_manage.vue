<template>
    <div id="systemClassManage">
        <div class="header" v-if="auth.create || auth.search">
            <div style="float: left;" v-if="auth.create">
                <bk-button theme="primary" @click="handleOpenDialog('add')">新增系统类别</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;" :placeholder="'请输入系统类别名称'" :right-icon="'bk-icon icon-search'"
                    v-model="searchForm.name" @right-icon-click="handleSearch" @enter="handleSearch">
                </bk-input>
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable" :max-height="maxTableHeight">
                <bk-table-column label="系统类别名称" prop="name" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="创建人" prop="creator" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="创建时间" prop="create_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="修改时间" prop="edit_time" :show-overflow-tooltip="true" sortable></bk-table-column>
                <bk-table-column label="描述" prop="description" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="操作" width="150">
                    <template slot-scope="props">
                        <bk-button class="mr10" theme="primary" text @click="handleOpenDialog('update', props.row)"
                            v-if="auth.modify">修改</bk-button>
                        <bk-button class="mr10" theme="primary" text @click="handleDelete(props.row)" v-if="auth.del">删除</bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
        <bk-dialog v-model="dialogSetting.systemDialogShow" theme="primary" :mask-close="false" header-position="left"
            :title="dialogSetting.title" :show-footer="true" :position="{ top: 50 }" :draggable="false" width="600"
            @confirm="handleConfim" :loading="dialogSetting.dialogLoading" :close-icon="dialogSetting.closeIconShow">
            <system :system-form="systemForm" :key="systemKey" ref="system"></system>
        </bk-dialog>
    </div>
</template>

<script>
    import system from './system_class_manage/systemDialog.vue'
    export default {
        components: {
            system
        },
        data() {
            return {
                maxTableHeight: '',
                loading: false,
                auth: {},
                dialogSetting: {
                    systemDialogShow: false,
                    dialogLoading: false,
                    closeIconShow: true,
                    title: ''
                },
                systemKey: 0,
                systemForm: {},
                tableList: [],
                tableLoading: false,
                searchForm: {
                    name: ''
                },
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
            // 处理确认
            handleConfim() {
                this.dialogSetting.dialogLoading = true
                this.$refs.system.$refs.form.validate().then(validator => {
                    if (this.dialogSetting.title === '新增系统类别') {
                        this.handleAdd()
                    } else {
                        this.handleUpdate()
                    }
                }).catch(e => {
                    this.$cwMessage('输入有误, 请检查您的输入！', 'warning')
                    this.dialogSetting.dialogLoading = false
                })
            },
            // 处理新增
            handleAdd() {
                this.dialogSetting.closeIconShow = false
                this.$api.category.create({ ...this.$refs.system.form
                }).then(res => {
                    if (res.result) {
                        this.dialogSetting.systemDialogShow = false
                        this.$cwMessage('新增成功!', 'success')
                        this.handleLoad()
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.dialogSetting.closeIconShow = true
                    this.dialogSetting.dialogLoading = false
                })
            },
            // 处理修改
            handleUpdate() {
                this.dialogSetting.closeIconShow = false
                this.$api.category.update(this.$refs.system.form.id, { ...this.$refs.system.form
                }).then(res => {
                    if (res.result) {
                        this.dialogSetting.systemDialogShow = false
                        this.$cwMessage('修改成功!', 'success')
                        this.handleLoad()
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.dialogSetting.closeIconShow = true
                    this.dialogSetting.dialogLoading = false
                })
            },
            // 处理打开新增弹窗
            handleOpenDialog(type, row) {
                if (type === 'add') {
                    this.systemForm = {
                        name: '',
                        description: ''
                    }
                    this.dialogSetting.title = '新增系统类别'
                } else {
                    this.systemForm = {
                        ...row
                    }
                    this.dialogSetting.title = '修改系统类别'
                }
                this.systemKey += 1
                this.dialogSetting.systemDialogShow = true
            },
            handleDelete(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.$api.category.delete(row.id).then(res => {
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
            handleLoad() {
                this.tableLoading = true
                this.$api.category.list({
                    ...this.searchForm,
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
    #systemClassManage {
        padding: 20px;
        height: 100%;

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
