<template>
    <bk-navigation-menu ref="menu" :default-active="nav.id" :before-nav-change="beforeNavChange"
                        :toggle-active="nav.toggle">
        <bk-navigation-menu-item v-for="item in nav.menuList" :key="item.name"
                                 :has-child="item.children && !!item.children.length"
                                 :group="item.group" :icon="item.icon" :disabled="item.disabled" :url="item.to"
                                 :id="item.name" @click="handleRouterJump(item, false)">
            <span>{{ item.cnName }}</span>
            <div slot="child">
                <bk-navigation-menu-item :key="child.name" v-for="child in item.children" :id="child.name"
                                         :disabled="child.disabled"
                                         :icon="child.icon" :default-active="child.active"
                                         @click="handleRouterJump(child, true)">
                    <span>{{ child.cnName }}</span>
                </bk-navigation-menu-item>
            </div>
        </bk-navigation-menu-item>
    </bk-navigation-menu>
</template>

<script>
export default {
    data() {
        return {
            nav: {
                menuList: [
                    {
                        "name": "home",
                        "cnName": "首页",
                        "to": "/home",
                        "icon": "iconfont icon-mianxingtubiao-shouye",
                        "hasChild": false,
                        "children": []
                    },
                    {
                        "name": "NewJob",
                        "cnName": "作业节点管理",
                        "to": "/newjob",
                        "icon": "iconfont icon-mianxingtubiao-zuoyeguanli",
                        "hasChild": true,
                        "children": [
                            {"name": "NewJob", "cnName": "新建作业", "to": "/newjob", "hasChild": false},
                            {"name": "JobList", "cnName": "作业列表", "to": "/joblist", "hasChild": false}]
                    },
                    {
                        'name': 'NewJobFlow',
                        'cnName': '作业流管理',
                        'to': '/newjobflow',
                        'icon': 'iconfont icon-mianxingtubiao-zuoyeliuguanli',
                        'hasChild': true,
                        'children': [{
                            'name': 'NewJobFlow',
                            'cnName': '新建作业流',
                            'to': '/newjobflow',
                            'hasChild': false
                        }, {
                            'name': 'JobFlowList',
                            'cnName': '作业流列表',
                            'to': '/jobflowlist',
                            'hasChild': false
                        }]
                    },
                    {
                        "name": "TaskList",
                        "cnName": "任务管理",
                        "to": "/taskList",
                        "icon": "iconfont icon-mianxingtubiao-zuoyejiankong",
                        "hasChild": false
                    },
                    {
                        "name": "JobMonitor",
                        "cnName": "作业监视",
                        "to": "/jobmonitor",
                        "icon": "iconfont icon-mianxingtubiao-zuoyejiankong",
                        "hasChild": false
                    }],
                id: '', // 当前激活侧边栏
                toggle: false
            }
        }
    },
    watch: {
        $route(val) {
            this.nav.id = val.meta.hasOwnProperty('fatherName') ? val.meta.fatherName : val.name
            console.log(this.nav.id)
        }
    },
    mounted() {
    },
    methods: {
        beforeNavChange(newId, oldId) {
            return true
        },
        handleRouterJump(item) {
            this.$store.commit('getJobFlowHistorySearch', {})
            this.$store.commit('getJobFlowViewSearch', {})
            if (item.to === '/jobmonitor') {
                this.$store.commit('changeTabActive', 'jobflowview')
                return this.$router.push({
                    path: '/jobflowview'
                })
            }
            if (item.to === '/jobhistory') {
                this.$store.commit('changeTabActive', 'jobflowviewhistory')
                return this.$router.push({
                    path: '/jobflowviewhistory'
                })
            }
            this.$router.push({
                path: `${item.to}`
            })
        }
    }
}
</script>

<style>
/* 以下样式是为了适应例子父级的宽高而设置 */
.bk-navigation {
    /* width: 100vw; */
    width: 100% !important;
    /* width: 100vw; */
    height: 100vh;
    outline: 1px solid #ebebeb;
}

.bk-navigation .bk-navigation-wrapper {
    height: 100%;
    /* height: calc(100vh - 252px) !important; */
    width: 100%;
}

.monitor-navigation-nav {
    width: 150px;
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

.monitor-navigation-nav .nav-item {
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

.monitor-navigation-nav .nav-item:hover {
    color: #3A84FF;
    cursor: pointer;
    background-color: #F0F1F5;
}
</style>
