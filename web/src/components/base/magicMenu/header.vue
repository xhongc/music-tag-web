<template>
    <div class="monitor-navigation-header">
        <div class="header-title">
            <span class="header-title-icon" @click="handleBack" v-if="$route.meta.hasOwnProperty('back')">
                <svg class="icon"
                    style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;"
                    viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4756">
                    <path d="M416 480h320v64H416l96 96-48 48-176-176 176-176 48 48-96 96z" p-id="4757"></path>
                </svg>
            </span>
        </div>
        <div style="display: flex;justify-content: center;align-items: center;">
            <bk-popover theme="light navigation-message" :arrow="false" offset="-150, 5" trigger="mouseenter"
                :tippy-options="{ 'hideOnClick': false }">
                <div class="header-mind">
                    <bk-badge class="" :theme="'danger'" :max="99" :val="msgList.length" :visible="msgList.length > 0">
                    <svg style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;"
                        viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M32,56c-1.3,0-2.6-0.6-3.4-1.6h-4.5c0.5,1.5,1.4,2.7,2.6,3.7c3.1,2.5,7.5,2.5,10.6,0c1.2-1,2.1-2.3,2.6-3.7h-4.5C34.6,55.4,33.3,56,32,56z"></path>
                        <path
                            d="M53.8,49.1L50,41.5V28c0-8.4-5.8-15.7-14-17.6V8c0-2.2-1.8-4-4-4s-4,1.8-4,4v2.4c-8.2,1.9-14,9.2-14,17.6v13.5l-3.8,7.6c-0.3,0.6-0.3,1.3,0.1,1.9c0.4,0.6,1,1,1.7,1h40c0.7,0,1.3-0.4,1.7-1C54,50.4,54.1,49.7,53.8,49.1z"></path>
                    </svg>
                    </bk-badge>
                </div>
                <template slot="content">
                    <div class="monitor-navigation-message">
                        <h5 class="message-title">消息中心</h5>
                        <ul class="message-list">
                            <li class="message-list-item" v-for="(item,index) in msgList" :key="index"
                                @click="handleRedirect(item)">
                                <span class="item-message">{{ item.message }}</span>
                                <span class="item-date">{{ item.created_at }}</span>
                            </li>
                        </ul>
                    </div>
                </template>
            </bk-popover>
            <bk-popover theme="light navigation-message" :arrow="false" placement="bottom"
                :tippy-options="{ 'hideOnClick': false }">
                <div class="header-user">
                    {{ userData.username }}
                    <i class="bk-icon icon-down-shape"></i>
                </div>
                <template slot="content">
                    <ul class="monitor-navigation-admin">
                        <li class="nav-item" @click="handleUserListClic2k">
                            后台管理{{refresh}}
                        </li>
                        <li class="nav-item" @click="handleUserListClic3k">
                            使用手册
                        </li>
                        <li class="nav-item" @click="handleUserListClick">
                            关于作者
                        </li>
                    </ul>
                </template>
            </bk-popover>
        </div>

    </div>
</template>

<script>
    import {clearStore} from '../../../common/store.js'
    import {mapGetters} from 'vuex'

    export default {
        data() {
            return {
                logout_url: 'https://github.com/xhongc/music-tag-web',
                pageTitle: '测试',
                userData: {},
                msgList: [],
                user: {
                    list: [
                        '关于作者'
                    ]
                }
            }
        },
        computed: {
            ...mapGetters(['getHasMsg']),
            refresh() {
                if (this.getHasMsg) {
                    this.$store.commit('setHasMsg', false)
                    this.fetchRecord()
                }
            },
            headerTitle() {
                return this.$route.meta.title
            }
        },
        created() {
            this.loginUser()
            this.fetchRecord()
        },
        methods: {
            changeTitle() {
            },
            handleRedirect(item) {
                console.log(item.parent_path)
                this.$store.commit('setFullPath', item.parent_path)
            },
            handleUserListClick(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', this.logout_url)
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            handleUserListClic2k(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', '/admin/')
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            handleUserListClic3k(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', 'https://xiers-organization.gitbook.io/music-tag-web/')
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            loginUser() {
                this.$api.Task.loginInfo().then((res) => {
                    if (res.result) {
                        this.userData = res.data
                        this.$store.commit('setUserRole', res.data.role)
                    } else {
                        this.$router.push({name: 'login'})
                    }
                })
            },
            handleBack() {
                this.$router.go(-1)
            },
            fetchRecord() {
                this.$api.Task.getRecord({'state': 'failed', 'page_size': 20}).then((res) => {
                    if (res.result) {
                        this.msgList = res.data.items
                    }
                })
            },
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

.navigation-header {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
    font-size: 14px;
}

.monitor-navigation-header .header-mind {
    color: #768197;
    font-size: 16px;
    position: relative;
    height: 32px;
    width: 32px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    margin-right: 8px
}

.monitor-navigation-header .header-mind.is-left {
    color: #63656E;
}

.monitor-navigation-header .header-mind.is-left:hover {
    color: #3A84FF;
    background: #F0F1F5
}

.monitor-navigation-header .header-mind-mark {
    position: absolute;
    right: 8px;
    top: 8px;
    height: 7px;
    width: 7px;
    border: 1px solid #27334C;
    background-color: #EA3636;
    border-radius: 100%
}

.monitor-navigation-header .header-mind-mark.is-left {
    border-color: #F0F1F5;
}

.monitor-navigation-header .header-mind:hover {
    background: -webkit-gradient(linear, right top, left top, from(rgba(37, 48, 71, 1)), to(rgba(38, 50, 71, 1)));
    background: linear-gradient(270deg, rgba(37, 48, 71, 1) 0%, rgba(38, 50, 71, 1) 100%);
    border-radius: 100%;
    cursor: pointer;
    color: #D3D9E4;
}

.monitor-navigation-header .header-mind .lang-icon {
    font-size: 20px;
}

.monitor-navigation-header .header-mind-mark {
    position: absolute;
    right: 8px;
    top: 8px;
    height: 7px;
    width: 7px;
    border: 1px solid #27334C;
    background-color: #EA3636;
    border-radius: 100%
}

.monitor-navigation-header .header-mind-mark.is-left {
    border-color: #F0F1F5;
}

.monitor-navigation-message {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    width: 360px;
    background-color: #FFFFFF;
    border: 1px solid #E2E2E2;
    border-radius: 2px;
    -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    color: #979BA5;
    font-size: 12px;
}

.monitor-navigation-message .message-title {
    -webkit-box-flex: 0;
    -ms-flex: 0 0 48px;
    flex: 0 0 48px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    color: #313238;
    font-size: 14px;
    padding: 0 20px;
    margin: 0;
    border-bottom: 1px solid #F0F1F5;
}

.monitor-navigation-message .message-list {
    -webkit-box-flex: 1;
    -ms-flex: 1;
    flex: 1;
    max-height: 450px;
    overflow: auto;
    margin: 0;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    padding: 0;
}

.monitor-navigation-message .message-list-item {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    width: 100%;
    padding: 0 20px;
}

.monitor-navigation-message .message-list-item .item-message {
    padding: 13px 0;
    line-height: 16px;
    min-height: 42px;
    -webkit-box-flex: 1;
    -ms-flex: 1;
    flex: 1;
    -ms-flex-wrap: wrap;
    flex-wrap: wrap;
    color: #63656E;
}

.monitor-navigation-message .message-list-item .item-date {
    padding: 13px 0;
    margin-left: 16px;
    color: #979BA5;
}

.monitor-navigation-message .message-list-item:hover {
    cursor: pointer;
    background: #F0F1F5;
}

.monitor-navigation-message .message-footer {
    -webkit-box-flex: 0;
    -ms-flex: 0 0 42px;
    flex: 0 0 42px;
    border-top: 1px solid #F0F1F5;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    color: #3A84FF;
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
