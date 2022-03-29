<template>
    <div id="jobFlowViewDetail" v-bkloading="{ isLoading: formLoading, zIndex: 999999 }">
        <div class="box">
            <p class="title">基本信息</p>
            <bk-container>
                <bk-form :label-width="130">
                    <bk-row>
                        <bk-col :span="6">
                            <bk-form-item label="作业流名称:">{{form.name}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="作业流状态:"><span v-if="form.hasOwnProperty('state')">{{stateList[stateList.findIndex(e => e.name === form.state)].label}}</span></bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="启动人:">{{form.executor}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="跑批系统:">{{form.category_name}}</bk-form-item>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="6">
                            <bk-form-item label="计划开始时间:">{{form.eta}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="实际开始时间:">{{form.start_time}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="完成时间:">{{form.end_time}}</bk-form-item>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-form-item label="总共耗时:">{{form.total_time}}</bk-form-item>
                        </bk-col>
                    </bk-row>
                </bk-form>
            </bk-container>
        </div>
        <div class="box">
            <p class="title">执行详情</p>
            <div id="content" v-bkloading="{ isLoading: mainLoading, zIndex: 999 }">
                <div class="left-statusList">
                    <statusList style="position: absolute;left: 20px;top: 15px;"></statusList>
                </div>
                <div class="right-canvas">
                    <div id="main" ref="main"></div>
                </div>
            </div>
        </div>
        <div class="node-drawer">
            <bk-sideslider :is-show.sync="nodeDrawer.show" :quick-close="true" :title="nodeDrawer.title"
                :width="nodeDrawer.width" ext-cls="custom-sidelider">
                <node-info slot="content" :node-data="nodeData" :key="nodeSliderKey">
                </node-info>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import {
        deepClone, getUUID
    } from '../../../common/util.js'
    import registerFactory from '@/components/graph/graph.js'
    import G6 from '@antv/g6'
    import statusList from './job_flow_view_detail/statusList.vue'
    import nodeInfo from './job_flow_view_detail/nodeInfo.vue'
    export default {
        components: {
            statusList,
            nodeInfo
        },
        data() {
            return {
                formLoading: false,
                nodeSliderKey: 0,
                form: {},
                graph: null,
                mainLoading: false,
                opreateFlag: false,
                tooltip: null, // 内容超出提示
                menu: null, // 右键菜单
                cfg: {}, // 配置项
                nodeDrawer: {
                    title: '',
                    show: false,
                    width: 600
                },
                nodeData: {},
                timer: null,
                stateList: [{
                                id: 1,
                                name: 'wait',
                                label: '等待'
                            },
                            {
                                id: 2,
                                name: 'run',
                                label: '正在执行'
                            },
                            {
                                id: 3,
                                name: 'fail',
                                label: '失败'
                            },
                            {
                                id: 4,
                                name: 'error',
                                label: '错误'
                            },
                            {
                                id: 5,
                                name: 'success',
                                label: '成功'
                            },
                            {
                                id: 6,
                                name: 'pause',
                                label: '挂起'
                            },
                            {
                                id: 7,
                                name: 'cancel',
                                label: '取消'
                            },
                            {
                                id: 8,
                                name: 'positive',
                                label: '就绪'
                            },
                            {
                                id: 9,
                                name: 'stop',
                                label: '终止'
                            },
                            {
                                id: 10,
                                name: 'need_confirm',
                                label: '待审核'
                            },
                            {
                                id: 11,
                                name: 'ignore',
                                label: '忽略'
                            },
                            {
                                id: 12,
                                name: 'exists_need_confirm',
                                label: '正在执行（存在审核）'
                            },
                            {
                                id: 13,
                                name: 'exists_error',
                                label: '正在执行（存在错误）'
                            },
                            {
                                id: 14,
                                name: 'exists_fail',
                                label: '正在执行（存在失败）'
                            },
                            {
                                id: 15,
                                name: 'exists_stop',
                                label: '正在执行（存在终止）'
                            },
                            {
                                id: 16,
                                name: 'exists_pause',
                                label: '正在执行（存在挂起）'
                            }
                ]
            }
        },
        created() {
            // 不需要清空画布，首屏刷新
            this.handleLoad(false, true)
        },
        mounted() {
            // 创建画布
            this.$nextTick(() => {
                this.createGraphic()
                this.initGraphEvent()
            })
            // 轮询画布
            this.timer = setInterval(() => {
                // 不需要清空画布，非首屏刷新
                this.handleLoad(false, false)
            }, 3000)
            window.addEventListener('resize', this.handleChangeCavasSize, false)
        },
        beforeDestroy() {
            window.removeEventListener('resize', this.handleChangeCavasSize, false)
            this.graph.destroy()
            clearInterval(this.timer)
        },
        methods: {
            // 处理改变画布大小
            handleChangeCavasSize() {
                this.graph.changeSize(this.$refs.main.clientWidth, 550)
                this.graph.fitView([20, 30, 30, 80])
            },
            initGraphEvent() {
                this.graph.on('node:click', e => {
                    const model = e.item.get('model')
                    // 开始节点，结束节点，作业流节点不做处理
                    if (model.nodeType === 0 || model.nodeType === 1) {
                        return false
                    }
                    this.nodeData = {
                        data: deepClone(model.node_data), // 深拷贝节点数据
                        log: model.log,
                        state: model.state,
                        script_content: model.script_content,
                        start_time: model.start_time,
                        end_time: model.end_time,
                        id: model.id
                    }
                    this.nodeSliderKey += 1
                    this.nodeDrawer.show = true
                    this.nodeDrawer.title = model.name
                })
            },
            createGraphic() {
                // 创建菜单
                this.createMenu()
                // 初始化配置项
                this.initOption()
                // 创建graph实例
                this.graph = new G6.Graph(this.cfg)
            },
            renderCanvas(detail, first) {
                if (first) {
                    this.mainLoading = true
                }
                const _this = this
                setTimeout(() => {
                    const data = {
                        edges: _this.form.pipeline_tree.lines.map(line => {
                            return {
                                detail: detail,
                                id: getUUID(32, 16),
                                source: line.from,
                                target: line.to
                            }
                        }),
                        nodes: _this.form.pipeline_tree.nodes.map((node, index) => {
                            let style = {}
                            if (node.type === 0 || node.type === 1) {
                                style = {
                                    fill: '#fff',
                                    r: 24
                                }
                            } else {
                                style = {
                                    width: 154,
                                    height: 40,
                                    radius: 20,
                                    iconCfg: {
                                        fill: '#3a84ff'
                                    }
                                }
                            }
                            return {
                                ...node,
                                detail: detail,
                                label: node.name.length > 8 ? `${node.name.substr(0, 8)}...` : node
                                    .name,
                                name: node.name,
                                icon: node.ico,
                                id: node.hasOwnProperty('end_uuid') ? node.end_uuid : node.uuid,
                                jobId: node.id,
                                x: Number(node.left),
                                y: Number(node.top),
                                nodeType: node.type,
                                state: node.state,
                                type: (node.type === 0 || node.type === 1) ? 'circle-node'
                                    : 'rect-node',
                                labelCfg: {
                                    style: {
                                        textAlign: (node.type === 0 || node.type === 1) ? 'center'
                                            : 'left'
                                    }
                                },
                                style: {
                                    ...style
                                }
                            }
                        })
                    }
                    _this.graph.read(data)
                    // _this.graph.fitCenter()
                    _this.mainLoading = false
                }, 2000)
            },
            initOption() {
                // 工厂函数注册自定义节点
                this.cfg = registerFactory(G6, {
                    width: this.$refs.main.clientWidth,
                    height: 550,
                    animate: true, // Boolean，可选，切换布局时是否使用动画过度
                    maxZoom: 1, // 最大缩放比例
                    fitView: true,
                    // fitView: true,
                    // layout: {
                    //     type: 'xxx'
                    // },
                    // layout: {
                    //     type: 'dagre',
                    //     rankdir: 'LR', // 可选，默认为图的中心
                    //     align: 'DL', // 可选
                    //     nodesep: 20, // 可选
                    //     ranksep: 50, // 可选
                    //     controlPoints: false, // 可选
                    // },
                    defaultNode: {
                        type: 'rect-node',
                        style: {
                            radius: 10
                        },
                        labelCfg: {
                            fontSize: 20
                        }
                    },
                    defaultEdge: {
                        type: 'polyline-edge', // 扩展了内置边, 有边的事件
                        // type: 'cubic-vertical-edge', // 扩展了内置边, 有边的事件
                        style: {
                            radius: 0, // 拐弯弧度
                            offset: 15, // 拐弯处距离节点的最小距离
                            stroke: '#aab7c3',
                            lineAppendWidth: 10, // 防止线太细没法点中
                            endArrow: {
                                path: 'M 0,0 L 4,3 L 3,0 L 4,-3 Z',
                                fill: '#aab7c3',
                                stroke: '#aab7c3'
                            },
                            zIndex: 999999
                        }
                    },
                    // 覆盖全局样式
                    nodeStateStyles: {
                        'nodeState:default': {
                            opacity: 1,
                            fill: '#fff',
                            stroke: '#DCDEE5',
                            labelCfg: {
                                style: {
                                    fill: '#333333'
                                }
                            }
                        },
                        'nodeState:hover': {
                            opacity: 0.8
                        },
                        'nodeState:selected': {
                            opacity: 0.9,
                            stroke: 'rgb(58,132,255)',
                            labelCfg: {
                                style: {
                                    fill: 'rgb(58,132,255)'
                                }
                            }
                        }
                    },
                    // linkCenter: true,
                    plugins: [this.tooltip, this.menu],
                    modes: {
                        // 允许拖拽画布、缩放画布、拖拽节点
                        default: [
                            'drag-canvas', // 官方内置的行为
                            'zoom-canvas',
                            'hover-node',
                            'drag-node',
                            'hover-edge'
                            // 'select-node'
                        ]
                    }
                })
            },
            // 创建菜单
            createMenu() {
                const _this = this
                // 创建内容超出提示
                this.tooltip = new G6.Tooltip({
                    offsetX: 20,
                    offsetY: -20,
                    itemTypes: ['node'],
                    // 自定义 tooltip 内容
                    getContent: (e) => {
                        const outDiv = document.createElement('div')
                        outDiv.style.width = 'fit-content'
                        outDiv.innerHTML = `<ul><li>${e.item.getModel().name}</li></ul>`
                        return outDiv
                    },
                    shouldBegin(e) {
                        const model = e.item.get('model')
                        // 触发方式，只有在内容超出8个字符的情况下才触发
                        if (model.nodeType === 0 || model.nodeType === 1 || model.name.length <= 8) {
                            return false
                        }
                        return true
                    }
                })
                // 创建右键菜单
                this.menu = new G6.Menu({
                    offsetX: 20,
                    offsetY: 20,
                    itemTypes: ['node'],
                    getContent(e) {
                        const model = e.item.get('model')
                        const outDiv = document.createElement('div')
                        outDiv.style.width = '60px'
                        outDiv.style.cursor = 'pointer'
                        outDiv.innerHTML = _this.renderRightMenu(model)
                        return outDiv
                    },
                    shouldBegin(e) {
                        const model = e.item.get('model')
                        // 触发方式，开始节点和结束节点或节点状态为成功的都不触发
                        if (model.nodeType === 0 || model.nodeType === 1 || model.state === 'ignore') {
                            return false
                        }
                        return true
                    },
                    handleMenuClick(target, item) {
                        const model = item.get('model')
                        const {
                            id
                        } = target
                        _this.handleOperation(id, model.jobId)
                    }
                })
            },
            // 处理执行节点操作
            handleOperation(str, id) {
                const contentMap = {
                    'pause': {
                        preState: '等待',
                        content: '作业暂停执行，不会继续后面的执行',
                        width: 450
                    },
                    'resume': {
                        preState: '挂起',
                        content: '恢复挂起作业流',
                        width: 400
                    },
                    'stop': {
                        preState: '进行中',
                        content: '终止后不会继续后面的执行，并且无法恢复。会强制终止此作业',
                        width: 400
                    },
                    'cancel': {
                        preState: '除了正在执行',
                        content: '将作业状态置为取消，可以继续往下执行',
                        width: 400
                    },
                    'replay': {
                        preState: '已完成、错误、失败，终止、取消',
                        content: '复制一份该作业，并放入原作业流中。如果新的作业成功，那么对作业流就是成功了',
                        width: 650
                    },
                    'release': {
                        preState: '未执行、等待',
                        content: '释放此作业的被依赖关系（包括时间依赖）',
                        width: 400
                    },
                    'success': {
                        preState: '错误，失败，终止',
                        content: '针对错误，失败，终止的作业，设置为成功',
                        width: 400
                    },
                    'confirm': {
                        preState: '待复核',
                        content: '针对待复核的作业，设置为等待',
                        width: 400
                    }
                }
                this.$bkInfo({
                    type: 'primary',
                    title: `执行前状态：${contentMap[str].preState}`,
                    subTitle: `功能说明：${contentMap[str].content}`,
                    width: contentMap[str].width,
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.mainLoading = true
                        // 解决操作执行过程中，由于轮询接口渲染画布而导致mainLoading刷新。
                        // 加入opreateFlag保证轮询过程中不会刷新画布
                        this.opreateFlag = true
                        this.$api.nodeRun.control({
                            'event': str,
                            'ids': [id]
                        }).then(res => {
                            if (res.result) {
                                this.$cwMessage('操作成功！', 'success')
                                // 清空画布并重新获取数据, 首屏刷新
                                this.opreateFlag = false
                                this.handleLoad(true, true)
                            } else {
                                this.$cwMessage(res.message, 'error')
                                // 操作执行接口调用结束，放开轮询
                                this.opreateFlag = false
                                this.mainLoading = false
                            }
                        })
                    }
                })
            },
            // 处理根据节点状态渲染左键菜单
            renderRightMenu(model) {
                // 当前状态为等待wait，可执行操作为挂起(暂停)pause，释放依赖release，取消cancel
                if (model.state === 'wait') {
                    return `<p id="pause" class="right-click-menu">挂起</p>
                            <p id="release" class="right-click-menu">释放依赖</p>
                            <p id="cancel" class="right-click-menu">取消</p>`
                }
                // 当前状态为暂停（挂起）pause，可执行操作为恢复resume，取消cancel
                if (model.state === 'pause') {
                    return `<p id="resume" class="right-click-menu">恢复</p>
                            <p id="cancel" class="right-click-menu">取消</p>`
                }
                // 当前状态为取消cancel，可执行的操作为重新执行replay
                if (model.state === 'cancel') {
                    return '<p id="replay" class="right-click-menu">重新执行</p>'
                }
                // 当前状态为失败fail或错误error或终止stop，可执行的操作为取消cancel，强制成功success，重新执行replay
                if (model.state === 'fail' || model.state === 'error' || model.state === 'stop') {
                    return `<p id="cancel" class="right-click-menu">取消</p>
                            <p id="success" class="right-click-menu">强制成功</p>
                            <p id="replay" class="right-click-menu">重新执行</p>`
                }
                // 当前状态为成功，可执行的操作为取消cancel，重新执行replay
                if (model.state === 'success') {
                    return `<p id="cancel" class="right-click-menu">取消</p>
                            <p id="replay" class="right-click-menu">重新执行</p>`
                }
                // 当前状态为待复核need_confirm，可执行的操作为取消cancel，复核confirm
                if (model.state === 'need_confirm') {
                    return `<p id="cancel" class="right-click-menu">取消</p>
                            <p id="confirm" class="right-click-menu">复核</p>`
                }
                // 当前状态为正在执行run，可执行的操作为终止stop
                if (model.state === 'run') {
                    return '<p id="stop" class="right-click-menu">终止</p>'
                }
            },
            handleLoad(clear = false, first = false) {
                // 操作进行中，不做轮询
                if (this.opreateFlag) {
                    return false
                }
                if (first) {
                    this.formLoading = true
                }
                // 在操作接口未调用结束的情况下不做轮询
                this.$api.processRun.retrieve(parseInt(this.$route.query.id)).then(res => {
                    if (res.result) {
                        this.form = res.data
                        if (this.form.hasOwnProperty('pre_commands')) {
                            this.$refs.editor.monacoEditor.setValue(this.form.pre_commands)
                        }
                        // 是否需要清空画布重新渲染
                        if (clear) {
                            this.graph.clear()
                        }
                        // this.nodeDrawer.show = false
                        this.renderCanvas(true, first)
                        const processState = res.data.pipeline_tree.process_state
                        if (processState === 'success' || processState === 'fail') {
                            clearInterval(this.timer)
                        }
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.formLoading = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobFlowViewDetail {
        padding: 20px;

        .node-drawer {

            // height: 100%;
            /deep/ .custom-sidelider {
                .bk-sideslider-wrapper {
                    .bk-sideslider-content {
                        height: calc(100% - 60px) !important;
                    }
                }
            }
        }

        .box {
             margin-bottom: 24px;
            .title {
                margin-bottom: 12px;
                font-size: 14px;
                color: #63656E;
                font-weight: bold;
                height: 22px;
                line-height: 22px;
            }

            .customTable {
                /deep/ .bk-table-empty-block {
                    background-color: #fff;
                }
            }

            .custom-textarea {
                /deep/ textarea {
                    padding: 20px;
                    background-color: rgb(49, 50, 56) !important;
                    color: #C4C6CC !important;
                }
            }

            #content {
                overflow: hidden;
                height: 550px;
                width: 100%;
                position: relative;
                background-image: linear-gradient(90deg, rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%), linear-gradient(rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%);
                background-size: 10px 10px;
                display: flex;

                .left-statusList {
                    height: 100%;
                    width: 150px;
                    // padding-left: 20px;
                    // padding-top: 15px;
                }

                .right-canvas {
                    width: 100%;
                    height: 100%;
                    position: relative;

                    #main {
                        position: relative;
                        width: 100%;
                        height: 100%;

                        /deep/ .right-click-menu:hover {
                            opacity: .9;
                        }

                        /deep/ .right-click-menu {
                            text-align: center;
                            color: #fff;
                            background-color: #3a84ff;
                            margin-bottom: 8px;
                            height: 22px;
                            line-height: 22px;
                        }

                        /deep/ .right-click-menu:last-of-type {
                            margin-bottom: 0;
                        }
                    }
                }
            }
        }
    }
</style>
