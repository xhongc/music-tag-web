<template>
    <div id="addUser">
        <div class="header-search">
            <bk-input v-model="name" style="width: 300px;" :placeholder="'请输入用户名或中文名'" @enter="handleSearch"
                @right-icon-click="handleSearch" :right-icon="'bk-icon icon-search'" :clearable="true"></bk-input>
        </div>
        <div class="content">
            <bk-table ref="table" :data="tableList" v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable">
                <bk-table-column label="用户名" prop="username" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="中文名" prop="display_name" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.display_name === '' ? '- -' : props.row.display_name}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="邮箱" prop="email" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.email === '' ? '- -' : props.row.email}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="手机" prop="telephone" :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.telephone === '' ? '- -' : props.row.telephone}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="操作">
                    <template slot-scope="props">
                        <bk-button class="mr10" theme="success" text @click="handleAdduser(props.row)">添加</bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
        <bk-dialog v-model="addUserDialogShow" theme="primary" :mask-close="false" header-position="left" title="新增用户"
            :show-footer="true" :position="{ top: 50 }" :draggable="false" width="600" @confirm="handleConfim" :loading="dialogLoading" :close-icon="closeIconShow">
            <user-info :run-sys-list="runSysList" ref="userInfo" :user-form="userForm" :key="userInfoKey"></user-info>
        </bk-dialog>
    </div>
</template>

<script>
    import {
        deepClone
    } from '../../../common/util.js'
    import userInfo from './userInfo.vue'
    export default {
        components: {
            userInfo
        },
        props: {
            runSysList: {
                type: Array,
                default: []
            }
        },
        data() {
            return {
                dialogLoading: false,
                closeIconShow: true,
                name: '',
                tableList: [],
                tableLoading: false,
                addUserDialogShow: false,
                userForm: {},
                userInfoKey: 0,
                midTableList: []
            }
        },
        created() {
            this.handleLoad()
        },
        methods: {
            handleAdduser(row) {
                this.userForm = {
                    bk_username: row.username,
                    chname: row.display_name,
                    email: row.email,
                    phone: row.telephone
                }
                this.userInfoKey += 1
                this.addUserDialogShow = true
            },
            handleConfim() {
                this.dialogLoading = true
                this.$refs.userInfo.$refs.form.validate().then(validator => {
                    this.closeIconShow = false
                    const params = {
                        bk_username: this.$refs.userInfo.form.bk_username,
                        role: this.$refs.userInfo.form.role,
                        chname: this.$refs.userInfo.form.chname,
                        email: this.$refs.userInfo.form.email,
                        phone: this.$refs.userInfo.form.phone,
                        notice_methods: this.$refs.userInfo.form.notice_methods,
                        categories: this.$refs.userInfo.form.role === 0 ? 'all' : this.$refs.userInfo.form
                            .categories
                    }
                    this.$api.user.create(params).then(res => {
                        if (res.result) {
                            this.addUserDialogShow = false
                            this.handleLoad()
                            this.$emit('after-add-user')
                            this.$cwMessage('新增成功!', 'success')
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                        this.closeIconShow = true
                        this.dialogLoading = false
                    })
                }).catch(e => {
                    this.$cwMessage('您的输入有误，请检查输入！', 'warning')
                    this.dialogLoading = false
                })
            },
            handleSearch() {
                const arr = this.midTableList.filter(item => {
                    return !this.name || item.display_name.toLowerCase().includes(this.name.toLowerCase()) ||
                        item.username
                            .toLowerCase().includes(this.name.toLowerCase())
                })
                this.tableList = deepClone(arr)
            },
            handleLoad() {
                this.tableLoading = true
                this.$api.user.get_uncreated_users().then(res => {
                    if (res.result) {
                        this.tableList = res.data
                        this.midTableList = res.data
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
    #addUser {
        width: 100%;

        .header-search {
            font-size: 0px;
        }

        .content {
            margin-top: 20px;
            width: 100%;
            max-height: 400px;
            overflow: scroll;

            .customTable {
                width: calc(100% - 1px);

                /deep/ .bk-table-empty-block {
                    background-color: #fff;
                }
            }
        }
    }
</style>
