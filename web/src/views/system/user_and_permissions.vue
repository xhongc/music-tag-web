<template>
    <div id="userPermission">
        <div class="header" v-if="auth.create || auth.search">
            <div style="float: left;" v-if="auth.create">
                <bk-button theme="primary" @click="handleOpenAddDialog">新增用户</bk-button>
            </div>
            <div style="float: right;" v-if="auth.search">
                <bk-input clearable width="240px" style="width: 240px;" :placeholder="'请输入用户名或中文名'" :right-icon="'bk-icon icon-search'"
                    v-model="searchFrom.name" @right-icon-click="handleSearch" @enter="handleSearch">
                </bk-input>
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table" :data="tableList" :pagination="pagination" @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable" :max-height="maxTableHeight">
                <bk-table-column label="用户名" prop="bk_username" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="中文名" prop="chname" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="邮箱" prop="email" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="手机" prop="phone" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="通知方式" prop="notice_methods" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{notice(props.row)}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="角色" prop="role" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span v-if="props.row.role === 0">超级管理员</span>
                        <span v-else-if="props.row.role === 1">管理员</span>
                        <span v-else-if="props.row.role === 2">操作者</span>
                        <span v-else-if="props.row.role === 3">普通用户</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="系统类别" prop="categories" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{categorie(props.row)}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作">
                    <template slot-scope="props">
                        <bk-button class="mr10" theme="primary" text @click="handleOpenUserDialog(props.row)">修改</bk-button>
                        <bk-button class="mr10" theme="primary" text @click="handleDelete(props.row)">删除</bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
        <bk-dialog v-model="infoDialogShow" theme="primary" :mask-close="false" header-position="left" title="修改"
            :show-footer="true" :position="{ top: 50 }" :draggable="false" width="600" @confirm="handleConfim" :loading="infodialogLoading" :close-icon="infocloseIconShow">
            <user-info :run-sys-list="runSysList" ref="userInfo" :user-form="userForm" :key="userInfoKey"></user-info>
        </bk-dialog>
        <bk-dialog v-model="addUserDialogShow" theme="primary" :mask-close="false" header-position="left" title="选择新增用户"
            :show-footer="true" :position="{ top: 50 }" :draggable="false" width="800" ext-cls="custom-dialog">
            <add-user-dialog :key="addUserDialogKey" :run-sys-list="runSysList" @after-add-user="handleLoad">
            </add-user-dialog>
            <div slot="footer">
                <bk-button @click="addUserDialogShow = false">取消</bk-button>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import userInfo from './user_and_permissions/userInfo.vue'
    import addUserDialog from './user_and_permissions/addUserDialog.vue'
    export default {
        components: {
            addUserDialog,
            userInfo
        },
        data() {
            return {
                maxTableHeight: '',
                auth: {},
                method_list: [{
                                  key: 0,
                                  label: '微信'
                              },
                              {
                                  key: 1,
                                  label: '邮件'
                              },
                              {
                                  key: 2,
                                  label: '短信'
                              }
                ],
                userInfoKey: 0,
                infodialogLoading: false,
                infocloseIconShow: true,
                infoDialogShow: false, // 用户信息弹窗标志位
                addUserDialogShow: false, // 新增用户弹窗标志位
                addUserDialogKey: 0,
                userForm: {}, // 用户信息表单
                dialogKey: 0,
                tableList: [],
                runSysList: [],
                tableLoading: false,
                searchFrom: {
                    name: ''
                },
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                }
            }
        },
        computed: {},
        created() {
            this.handleLoad()
            this.getRunSysList()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            notice(row) {
                const arr = []
                row.notice_methods.forEach(item1 => {
                    this.method_list.forEach(item2 => {
                        if (item2.key === item1) {
                            arr.push(item2.label)
                        }
                    })
                })
                return arr.join(',')
            },
            categorie(row) {
                const arr = []
                row.categories.forEach(item1 => {
                    this.runSysList.forEach(item2 => {
                        if (item2.id === item1) {
                            arr.push(item2.name)
                        }
                    })
                })
                return arr.join(',')
            },
            // 处理打开新增用户弹窗
            handleOpenAddDialog() {
                this.addUserDialogKey += 1
                this.addUserDialogShow = true
            },
            // 处理打开用户弹窗
            handleOpenUserDialog(row) {
                this.userForm = {
                    bk_username: row.bk_username, // 用户名
                    chname: row.chname, // 中文名
                    email: row.email, // 邮箱
                    phone: row.phone, // 手机号
                    notice_methods: row.notice_methods, // 通知方式
                    role: row.role, // 角色
                    categories: row.categories, // 系统类别
                    id: row.id
                }
                this.userInfoKey += 1
                this.infoDialogShow = true
            },
            // 处理删除
            handleDelete(row) {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.$api.user.delete(row.id).then(res => {
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
            handleConfim() {
                this.infodialogLoading = true
                this.$refs.userInfo.$refs.form.validate().then(validator => {
                    this.infocloseIconShow = false
                    this.tableLoading = true
                    const params = {
                        bk_username: this.$refs.userInfo.form.bk_username,
                        role: this.$refs.userInfo.form.role,
                        chname: this.$refs.userInfo.form.chname,
                        email: this.$refs.userInfo.form.email,
                        phone: this.$refs.userInfo.form.phone,
                        notice_methods: this.$refs.userInfo.form.notice_methods,
                        categories: this.$refs.userInfo.form.role === 0 ? 'all' : this.$refs.userInfo.form.categories
                    }
                    this.$api.user.update(this.$refs.userInfo.form.id, params).then(res => {
                        if (res.result) {
                            this.$cwMessage('修改成功!', 'success')
                            this.infoDialogShow = false
                            this.handleLoad()
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                        this.infocloseIconShow = true
                        this.infodialogLoading = false
                        this.tableLoading = false
                    })
                }).catch(e => {
                    this.$cwMessage('您的输入有误，请检查输入！', 'warning')
                    this.infodialogLoading = false
                })
            },
            // 处理查找
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
                this.$api.user.list({
                    search: this.searchFrom.name,
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
            getRunSysList() {
                this.tableLoading = true
                this.$api.category.list().then(res => {
                    if (res.result) {
                        this.runSysList = res.data.items
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
    #userPermission {
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

            // .custom-dialog {
            //     /deep/ .footer-wrapper {
            //         .bk-primary .bk-button-normal {
            //             display: none;
            //         }
            //     }
            // }
        }
    }
</style>
