<template>
    <div id="taskMake" ref="taskMake" v-bkloading="{ isLoading: taskMakeLoading, zIndex: 10 }">
        <div class="box">
            <div style="width: 474px;">
                <bk-alert type="info" title="将作业节点拖至右侧画布进行编排"></bk-alert>
                <!--<span class="iconfont icon-xianxingtubiao-tishi"></span>
                <span>将作业节点拖至右侧画布进行编排</span> -->
            </div>
        </div>
        <div class="box">
            <bk-compose-form-item head-background-color="#fff">
                <bk-select :clearable="false" style="width: 111px;" v-model="form.makeType" placeholder="请选择" @change="handleMakeTypeChange"
                    :disabled="false">
                    <bk-option v-for="(item, index) in makeList" :key="index" :id="item.value" :name="item.label">
                    </bk-option>
                </bk-select>
                <bk-input clearable style="width: 356px;margin-left: 8px" :placeholder="'请输入'" :right-icon="'bk-icon icon-search'"
                    v-model="form.name" @right-icon-click="handleSearch" @enter="handleSearch" :disabled="disabled">
                </bk-input>
            </bk-compose-form-item>
        </div>
        <div class="select-node-box" v-bkloading="{ isLoading: jobListLoading, zIndex: 10 }">
            <div v-for="(item, index) in jobList" :key="index" class="select-node" draggable="true" :title="item.name"
                :data-nodetype="item.nodeType" :data-content="item.id" :data-icon="item.icon" :data-endUuid="item.endUuid">
                {{item.name}}
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        // props: ['controlType'],
        props: {
            controlType: {
                type: String,
                default: {}
            }
        },
        inject: ['father_this'],
        data() {
            return {
                midRunId: '',
                disabled: false,
                cancel: true,
                midSystemId: '',
                taskMakeLoading: false, // 任务编排loading
                jobListLoading: false, // 作业列表loading
                runSysList: [], // 跑批系统下拉列表
                agentShow: true, // agent下拉列表显隐，解决异步获取数据后无法选择问题
                agentList: [], // agent下拉列表
                form: {
                    system_id: '', // 跑批系统id
                    agent_id: '', // agent
                    makeType: 3, // 是否编排
                    name: '' // 作业名
                },
                makeList: [
                    {
                        label: '逻辑节点',
                        value: 3
                    }, {
                        label: '空节点模板',
                        value: 0
                    }, {
                        label: '节点模板',
                        value: 2
                    }, {
                        label: '子流程',
                        value: 1
                    }],
                jobList: [
                    {
                        'id': 45,
                        'creator': 'product',
                        'name': '条件网关',
                        'type': 4,
                        'nodeType': 4,
                        'icon': 'e6d9'
                    },
                    {
                        'id': 46,
                        'creator': 'product',
                        'name': '并行网关',
                        'type': 4,
                        'nodeType': 4,
                        'icon': 'e6d9'
                    },
                    {
                        'id': 47,
                        'creator': 'product',
                        'name': '汇聚网关',
                        'type': 4,
                        'nodeType': 4,
                        'icon': 'e6d9'
                    },
                    {
                        'id': 48,
                        'creator': 'product',
                        'name': '条件并行网关',
                        'type': 4,
                        'nodeType': 4,
                        'icon': 'e6d9'
                    }
                ]
            }
        },
        mounted() {
            if (this.$route.query.type !== 'add') {
                if (this.$route.query.type === 'detail') {
                    this.disabled = true
                }
                setTimeout(() => {
                    this.form.system_id = this.father_this.jobFlowFrom.category
                }, 2000)
            }
            this.getRunSysList()
            // 监听节点拖拽事件
            this.$refs.taskMake.querySelector('.select-node-box').addEventListener('dragend', e => {
                if (e.target.classList.contains('select-node')) {
                    this.$emit('main-add-node', e)
                }
            })
            // 阻止默认动作
            document.addEventListener('drop', e => {
                e.preventDefault()
            }, false)
        },
        methods: {
            // 获取作业流
            getJobFlowList(str) {
                this.jobListLoading = true
                const params = {
                    category: this.form.system_id
                }
                if (str === 'search') {
                    params.name = this.form.name
                }
                this.$api.process.list(params).then(res => {
                    if (res.result) {
                        this.jobList = res.data.items.map((item) => {
                            return {
                                ...item,
                                nodeType: 3,
                                endUuid: item.end_uuid,
                                icon: 'e6d4'
                            }
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.jobListLoading = false
                })
            },
            // 获取节点模板
            getNodeTemplateList(str) {
                this.jobListLoading = true
                const params = {
                    category: this.form.system_id
                }
                if (str === 'search') {
                    params.name = this.form.name
                }
                this.$api.content.list(params).then(res => {
                    if (res.result) {
                        this.jobList = res.data.items.map((item) => {
                            return {
                                ...item,
                                nodeType: 2,
                                endUuid: item.end_uuid,
                                icon: 'e6d9'
                            }
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.jobListLoading = false
                })
            },
            // 获取作业
            getJobList(str) {
                // this.jobListLoading = true
                const params = {
                    station: this.form.agent_id
                }
                if (str === 'search') {
                    params.name = this.form.name
                }
                this.jobList = [
                    {
                        'id': 45,
                        'creator': 'product',
                        'name': '作业终止测试',
                        'type': 2,
                        'create_time': '2021-08-10 17:34:57',
                        'description': 'xx',
                        'editor': 'product',
                        'edit_time': '2021-11-15 11:55:06',
                        'total_run_count': 145,
                        'last_run_at': '2021-11-15 11:55:06',
                        'exit_code': '',
                        'station': 'agent11',
                        'ip': '192.168.163.185',
                        'os': 'linux centos',
                        'category': 'v17',
                        'process': '参数传递_test2_20210818191900,stop_test,重新执行测试,参数传递_test2,外部作业流_test1',
                        'account': 'root',
                        'script_type': 4,
                        'script_content': '1',
                        'script_timeout': 8600
                    }
                ]
                this.jobList = this.jobList.map((item) => {
                    return {
                        ...item,
                        nodeType: item.type,
                        endUuid: '',
                        icon: 'e6d9'
                    }
                })
            },
            // 处理编排类型切换
            handleMakeTypeChange() {
                // 编排类型切换时清空当前agent值,清空作业列表,清空作业名
                this.jobList = []
                this.form.name = ''
                this.form.agent_id = ''
                // 编排类型切换为未编排时，当前跑批系统id不为空，默认获取agent列表
                if (this.form.makeType === 0) {
                    this.getNodeTemplateList()
                } else if (this.form.makeType === 1) {
                    // 编排类型切换成已编排时，记录此时的跑批id
                    this.midRunId = this.form.system_id
                    // 编排类型切换为已编排时，当前跑批系统id不为空，默认获取作业流列表
                    this.getJobFlowList()
                } else if (this.form.makeType === 2) {
                    this.getNodeTemplateList()
                } else if (this.form.makeType === 3) {
                    this.jobList = [
                        {
                            'id': 45,
                            'creator': 'product',
                            'name': '条件网关',
                            'type': 4,
                            'nodeType': 4,
                            'icon': 'e6d9'
                        },
                        {
                            'id': 46,
                            'creator': 'product',
                            'name': '并行网关',
                            'type': 4,
                            'nodeType': 4,
                            'icon': 'e6d9'
                        },
                        {
                            'id': 47,
                            'creator': 'product',
                            'name': '汇聚网关',
                            'type': 4,
                            'nodeType': 4,
                            'icon': 'e6d9'
                        },
                        {
                            'id': 48,
                            'creator': 'product',
                            'name': '条件并行网关',
                            'type': 4,
                            'nodeType': 4,
                            'icon': 'e6d9'
                        }
                    ]
                }
            },
            // 处理查询
            handleSearch() {
                if (!this.form.makeType) {
                    // 当前作业为未编排,查询获取作业列表
                    this.getJobList('search')
                } else {
                    // 当前作业为已编排,查询获取作业流列表
                    this.getJobFlowList('search')
                }
            },
            // 处理跑批系统id变化
            handleRunIdChange(e) {
                // 该标志用于控制在未编排状态下切换跑批系统弹窗选择取消时二次弹窗
                if (!this.cancel) {
                    this.cancel = true
                    return false
                }
                // 跑批系统空值状态下没必要判断
                if (this.midSystemId === '') {
                    this.handleConfim()
                    this.midSystemId = e
                } else {
                    // 未编排状态下切换跑批系统将清空画布
                    if (!this.form.makeType) {
                        // 表明此时的变化是由于在已编排切换了跑批系统切回未编排时为了还原而导致的，这里无需做清空画布的处理
                        if (this.midRunId !== '') {
                            this.midRunId = ''
                            return false
                        }
                        // 这里是由于初始的时候先切了已编排选择跑批id后切回未编排，midRunId为空赋值变化导致的，这里无需做清空画布的处理
                        if (this.form.system_id === '') {
                            this.midSystemId = ''
                            return false
                        }
                        this.$bkInfo({
                            type: 'primary',
                            title: '此操作将清空画布, 确认吗？',
                            confirmLoading: false,
                            confirmFn: async() => {
                                this.jobList = []
                                this.midSystemId = e
                                this.$emit('empty-task-make', false)
                                this.handleConfim()
                            },
                            cancelFn: async() => {
                                this.form.system_id = this.midSystemId
                                this.cancel = false
                            }
                        })
                    } else {
                        // 已编排状态下正常切换
                        this.handleConfim()
                    }
                }
            },
            handleConfim() {
                // 当前为未编排且跑批系统id不为空时获取agent下拉列表
                if (!this.form.makeType && this.form.system_id !== '') {
                    this.form.agent_id = ''
                    this.getAgentList()
                } else {
                    // 当前为已编排，跑批系统id切换获取已编排作业流
                    this.getJobFlowList()
                }
            },
            // 获取agent列表
            getAgentList() {
                this.taskMakeLoading = true
                this.agentShow = false
                this.$api.station.list({
                    'category': this.form.system_id
                }).then(res => {
                    if (res.result) {
                        this.agentList = res.data.items
                        this.agentShow = true
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.taskMakeLoading = false
                })
            },
            // 获取作业库跑批系统
            getRunSysList() {
                this.runSysList = []
            }
        }
    }
</script>

<style lang="scss" scoped>
    #taskMake {
        height: 100%;
        overflow: hidden;

        .box {
            margin-bottom: 24px;

            .flex-wrap {
                height: 32px;
                line-height: 32px;
                display: flex;

                .label {
                    width: 78px;
                    text-align: right;
                    margin-right: 16px;
                }
            }
        }

        .select-node-box {
            overflow: auto;
            height: calc(100% - 215px);
            padding: 0 14px 0 6px;
            font-size: 0px;

            .select-node {
                font-size: 14px;
                cursor: pointer;
                margin-bottom: 12px;
                margin-left: 8px;
                width: 140px;
                text-align: center;
                height: 30px;
                line-height: 30px;
                border: 1px solid #C4C6CC;
                border-radius: 2px;
                float: left;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                padding: 0 8px 0 8px;

                &:hover {
                    background-color: #E1ECFF;
                    ;
                }

                &:active {
                    background-color: #E1ECFF;
                    ;
                    color: #3A84FF;
                }
            }
        }
    }
</style>
