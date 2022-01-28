<template>
    <div id="userInfo">
        <bk-form ref="form" :label-width="90" :rules="rules" :model="form">
            <bk-form-item label="用户名:">
                <bk-input disabled v-model="form.bk_username"></bk-input>
            </bk-form-item>
            <bk-form-item label="中文名:">
                <bk-input disabled v-model="form.chname"></bk-input>
            </bk-form-item>
            <bk-form-item label="邮箱:">
                <bk-input disabled v-model="form.email"></bk-input>
            </bk-form-item>
            <bk-form-item label="手机:">
                <bk-input disabled v-model="form.phone"></bk-input>
            </bk-form-item>
            <bk-form-item label="通知方式:" :error-display-type="'normal'" :required="true" :property="'notice_methods'">
                <bk-select multiple display-tag v-model="form.notice_methods">
                    <bk-option v-for="option in methodList" :key="option.key" :id="option.key" :name="option.label">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="角色:" :error-display-type="'normal'" :required="true" :property="'role'">
                <bk-select v-model="form.role" @change="handleRoleChange">
                    <bk-option v-for="option in roleList" :key="option.key" :id="option.key" :name="option.label">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="系统类别:">
                <bk-select v-model="form.categories" :disabled="categorieDisabled" multiple display-tag>
                    <bk-option v-if="form.role === 0" id="all" name="全部">
                    </bk-option>
                    <bk-option v-else v-for="option in runSysList" :key="option.id" :id="option.id" :name="option.name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    export default {
        props: {
            runSysList: {
                type: Array,
                default: []
            },
            userForm: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                firstKey: 0,
                categorieDisabled: false,
                form: {
                    bk_username: '', // 用户名
                    chname: '', // 中文名
                    email: '', // 邮箱
                    phone: '', // 手机号
                    notice_methods: [], // 通知方式
                    role: '', // 角色
                    categories: [] // 系统类别
                },
                roleList: [{
                               key: 0,
                               label: '超级管理员'
                           },
                           {
                               key: 1,
                               label: '管理员'
                           },
                           {
                               key: 2,
                               label: '操作者'
                           },
                           {
                               key: 3,
                               label: '普通用户'
                           }
                ],
                methodList: [{
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
                rules: {
                    notice_methods: [{
                        required: true,
                        message: '通知方式不能为空',
                        trigger: 'change'
                    }],
                    role: [{
                        required: true,
                        message: '角色不能为空',
                        trigger: 'change'
                    }]
                }
            }
        },
        created() {
            Object.assign(this.form, this.userForm)
            if (this.form.role === 0) {
                this.form.categories = ['all']
            }
        },
        methods: {
            handleRoleChange(e) {
                if (e === 0) {
                    this.categorieDisabled = true
                    this.form.categories = ['all']
                } else {
                    this.form.categories = []
                    this.categorieDisabled = false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
</style>
