<template>
    <div class="monitor-navigation-header">
        <div class="header-title">
            <span class="header-title-icon" @click="handleBack" v-if="$route.meta.hasOwnProperty('back')">
                <svg class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;"
                    viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4756">
                    <path d="M416 480h320v64H416l96 96-48 48-176-176 176-176 48 48-96 96z" p-id="4757"></path>
                </svg>
            </span>
            {{headerTitle}}
        </div>
        <bk-popover theme="light navigation-message" :arrow="false" placement="bottom" :tippy-options="{ 'hideOnClick': false }">
            <div class="header-user">
                {{userData.username}}
                <i class="bk-icon icon-down-shape"></i>
            </div>
            <template slot="content">
                <ul class="monitor-navigation-admin" @click="handleUserListClick">
                    <li class="nav-item" v-for="userItem in user.list" :key="userItem" :data-key="userItem">
                        {{userItem}}
                    </li>
                </ul>
            </template>
        </bk-popover>
    </div>
</template>

<script>
    import {
        clearStore
    } from '../../../common/store.js'
    export default {
        data() {
            return {
                logout_url: '',
                pageTitle: '测试',
                userData: {},
                user: {
                    list: [
                        '退出'
                    ]
                }
            }
        },
        computed: {
            headerTitle() {
                let title = this.$route.meta.title
                if (title === '变量表') {
                    if (this.$route.query.type === 'detail') {
                        title = '变量表详情'
                    }
                    if (this.$route.query.type === 'update') {
                        title = '修改变量表'
                    }
                    if (this.$route.query.type === 'add') {
                        title = '新增变量表'
                    }
                }
                if (title === '操作日历') {
                    if (this.$route.query.type === 'add') {
                        title = '新增日历'
                    }
                    if (this.$route.query.type === 'update') {
                        title = '修改日历'
                    }
                    if (this.$route.query.type === 'detail') {
                        title = '日历详情'
                    }
                }
                // if (title === '操作日历') {
                //     if (this.$route.params.isAdd === true) {
                //         title = '新增日历'
                //     }
                //     if (this.$route.params.isEdit === true) {
                //         title = '修改日历'
                //     }
                //     if (this.$route.params.isDetail === true) {
                //         title = '日历详情'
                //     }
                // }
                if (title === '单个作业流') {
                    if (this.$route.query.type === 'detail') {
                        title = '单个作业流详情'
                    }
                    if (this.$route.query.type === 'update') {
                        title = '单个作业流修改'
                    }
                }
                if (title === '单个作业') {
                    if (this.$route.query.type === 'update') {
                        title = '单个作业修改'
                    }
                }
                return title
            }
        },
        created() {
            // this.loginUser()
        },
        methods: {
            changeTitle() {},
            handleUserListClick(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', this.logout_url)
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            loginUser() {
                this.$api.user.login().then(res => {
                    if (res.result) {
                        this.userData = res.data
                        this.logout_url = res.data.logout_url
                    }
                })
            },
            handleBack() {
                this.$router.go(-1)
            }
        }
    }
</script>

<style scoped>
    .monitor-navigation-header {
        -webkit-box-flex: 1;
        -ms-flex: 1;
        flex: 1;
        height: 100%;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        justify-content: space-between;
        font-size: 14px;
    }

    .monitor-navigation-header .header-title {
        color: #63656E;
        font-size: 16px;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        margin-left: -6px;
    }

    .monitor-navigation-header .header-title-icon {
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        width: 28px;
        height: 28px;
        font-size: 28px;
        color: #3A84FF;
        cursor: pointer;
    }

    .monitor-navigation-header .header-select {
        width: 240px;
        margin-left: auto;
        margin-right: 34px;
        border: none;
        background: #f0f1f5;
        color: #63656e;
        -webkit-box-shadow: none;
        box-shadow: none
    }

    .monitor-navigation-header .header-user {
        height: 100%;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        -webkit-box-pack: center;
        -ms-flex-pack: center;
        justify-content: center;
        color: #96A2B9;
        /*       margin-left: 8px; */
    }

    .monitor-navigation-header .header-user .bk-icon {
        margin-left: 5px;
        font-size: 12px;
    }

    .monitor-navigation-header .header-user:hover {
        cursor: pointer;
        color: #3A84FF
    }

    .monitor-navigation-admin {
        width: 170px #63656E;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-orient: vertical;
        -webkit-box-direction: normal;
        -ms-flex-direction: column;
        flex-direction: column;
        background: #FFFFFF;
        border: 1px solid #E2E2E2;
        -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
        box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
        padding: 6px 0;
        margin: 0;
        color: #63656E;
    }

    .monitor-navigation-admin .nav-item {
        -webkit-box-flex: 0;
        -ms-flex: 0 0 32px;
        flex: 0 0 32px;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        padding: 0 20px;
        list-style: none
    }

    .monitor-navigation-admin .nav-item:hover {
        color: #3A84FF;
        cursor: pointer;
        background-color: #F0F1F5;
    }
</style>

<style>
    .tippy-popper .tippy-tooltip.navigation-message-theme {
        padding: 0;
        border-radius: 0;
        -webkit-box-shadow: none;
        box-shadow: none;
    }
</style>
