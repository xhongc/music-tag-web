<template>
    <div id="singleJobFlow" v-bkloading="{ isLoading: mainLoading, zIndex: 999999 }">
        <div class="node-drawer">
            <bk-sideslider :is-show.sync="nodeDrawer.show" :quick-close="true" :title="nodeDrawer.title" :width="nodeDrawer.width"
                ext-cls="custom-sidelider" @hidden="handleNodeDrawerClose">
                <node-info slot="content" @node-drawer-close="handleNodeDrawerClose" :key="nodeSliderKey" :node-data="nodeData"
                    @update-node-data="handleUpdateNode">
                </node-info>
            </bk-sideslider>
            <bk-sideslider :is-show.sync="edgeDrawer.show" :quick-close="true" :title="edgeDrawer.title" :width="edgeDrawer.width"
                ext-cls="custom-sidelider">
                <edge-info slot="content" :key="edgeSliderKey" :edge-data="edgeData" @update-edge-data="handleUpdateEdge"
                    @edge-drawer-close="handleEdgeDrawerClose">
                </edge-info>
            </bk-sideslider>
        </div>
        <div class="header" style="position: relative;z-index: 100;">
            <header-panel @handleSave="handleSave" :graph="graph" ref="headerPanel"
                :control-type="controlType" @layout-setting="handleLayoutSetting"></header-panel>
        </div>
        <div style="clear: both;"></div>
        <div id="main" class="main" ref="main">
            <Drawer class="taskFormatDrawer" :title="drawer.title" :width="drawer.width" :mask="false" :mask-closable="true"
                :transfer="false" placement="left" v-model="drawer.show" :inner="true" class-name="custom-drawer"
                @on-close="handleDrawerClose" :before-close="handleDrawerCloseBefore">
                <base-info v-show="isActive === 1" ref="baseInfo" @empty-task-make="handleEmptyTaskMake" :control-type="controlType"></base-info>
                <task-make v-show="isActive === 2" @main-add-node="handleAddNode" ref="taskMake" :key="taskMakeKey"
                    :control-type="controlType" @empty-task-make="handleEmptyTaskMake"></task-make>
            </Drawer>
        </div>
        <bk-dialog title="连线模式选择"
            v-model="flowModeDialog.show"
            :confirm-fn="handleFlowAddEdgeConfirm"
            ext-cls="add-mode-dialog"
            :mask-close="false"
            header-position="left">
            <add-mode-dialog :key="flowModeDialogKey" ref="addModeDialog"></add-mode-dialog>
            <bk-dialog v-model="flowModeDialog.childDialog.show"
                :mask-close="false"
                :width="flowModeDialog.childDialog.width"
                header-position="left"
                :render-directive="'if'"
                :position="{ top: 50 }"
                ext-cls="pre-flow-canvas-dialog"
                :confirm-fn="handlePreFlowNOdeAddConfirm"
                :show-footer="flowModeDialog.childDialog.footerShow">
                <div slot="header">
                    <span style="color: #313237;">当前作业流：{{flowModeDialog.childDialog.title}}</span>
                    <span class="iconfont icon-mianxingtubiao-wenti" style="margin-left: 4px;color: #979BA5;font-size: 16px;" v-bk-tooltips="flowModeTipConfig"></span>
                </div>
                <pre-flow-canvas :options="flowModeDialog.curObj" :pre-edges="flowModeDialog.preEdges" ref="preFlowCanvas"></pre-flow-canvas>
            </bk-dialog>
        </bk-dialog>
    </div>
</template>

<script>
    import options from './single_job_flow/options.js'
    import {
        deepClone, getUUID
    } from '../../common/util.js'
    import addModeDialog from './single_job_flow/addModeDialog.vue'
    import preFlowCanvas from './single_job_flow/preFlowCanvas.vue'
    import nodeInfo from './single_job_flow/nodeInfo.vue'
    import edgeInfo from './single_job_flow/edgeInfo.vue'
    import headerPanel from './single_job_flow/headerPanel.vue'
    import baseInfo from './single_job_flow/baseInfo.vue'
    import taskMake from './single_job_flow/taskMake.vue'
    import baseNodes from './single_job_flow/baseNode.js'
    import registerFactory from '@/components/graph/graph.js'
    import G6 from '@antv/g6'
    export default {
        components: {
            baseInfo, // 基础信息
            taskMake, // 任务编排
            headerPanel, // 头部菜单
            nodeInfo, // 节点信息
            edgeInfo, // 分支线信息
            addModeDialog, // 前置作业流连线模式选择弹窗
            preFlowCanvas // 前置作业流详情画布
        },
        provide() {
            return {
                father_this: this
            }
        },
        data() {
            return {
                checkFlag: true,
                dragStartNode: {},
                jobFlowFrom: null,
                flowModeTipConfig: {
                    content: '选择前置作业流中的某个节点作为前置依赖连线，不可重复选择节点连线，不可选择该作业流中的前置作业流节点！',
                    placement: 'right',
                    width: 300,
                    zIndex: 999999
                    // delay: [0, 60000]
                },
                mainLoading: false, // 画布loading
                nodeData: {}, // 当前节点的数据
                edgeData: {}, // 当前分支线的数据
                isActive: 0, // 当前选中头部菜单， 1为基本信息， 2为任务编排
                controlType: '',
                taskMakeKey: 0, // 是否刷新任务编排
                nodeSliderKey: 0, // 节点信息抽屉组件key
                edgeSliderKey: 0, // 分支线抽屉信息组件key
                flowModeDialogKey: 0, // 前置作业流连线弹窗组件key
                nodeDrawer: { // 节点信息抽屉
                    show: false,
                    width: 536,
                    title: ''
                },
                edgeDrawer: { // 节点信息抽屉
                    show: false,
                    width: 496,
                    title: ''
                },
                drawer: { // 配置栏抽屉
                    show: false,
                    width: 532,
                    title: ''
                },
                nodes: [{ ...baseNodes[0],
                        id: getUUID(32, 16)
                        // uuid: getUUID(32, 16)
                        },
                        { ...baseNodes[1],
                        id: getUUID(32, 16)
                        // uuid: getUUID(32, 16)
                        }
                ],
                edges: [],
                graph: null,
                flowModeDialog: { // 前置作业流连线模式选择弹窗
                    show: false,
                    curObj: {}, // 当前前置作业流的信息
                    preEdges: [], // 当前前置作业流节点的出线集
                    childDialog: { // 当前前置作业流节点的详情弹框
                        footerShow: false,
                        show: false,
                        width: 960,
                        title: ''
                    }
                }
            }
        },
        created() {
            // 如果当前为详情或编辑，初始化数据
            if (this.$route.query.type !== 'add') {
                this.getSingleJobFlow()
            } else {
                this.isActive = 1
                this.drawer.title = '基础信息'
                this.drawer.show = true
            }
        },
        mounted() {
            // 创建画布并绑定相关事件
            this.$nextTick(() => {
                this.createGraphic()
                this.initGraphEvent()
            })
            // 监听屏幕大小变化改变画布
            window.addEventListener('resize', this.handleChangeCavasSize, false)
        },
        beforeDestroy() {
            this.graph.destroy()
            window.removeEventListener('resize', this.handleChangeCavasSize, false)
        },
        beforeRouteLeave(to, from, next) {
            if (this.checkFlag && this.$route.query.type !== 'detail') {
                this.$bkInfo({
                    type: 'warning',
                    width: 480,
                    title: '该操作会导致您的编辑无保存, 确认吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        next()
                    }
                })
            } else {
                next()
            }
        },
        methods: {
            // 处理改变画布大小
            handleChangeCavasSize() {
                this.graph.changeSize(this.$refs.main.clientWidth, this.$refs.main.clientHeight)
            },
            // 一键排版
            handleLayoutSetting() {
                let nodesep = 40
                let ranksep = 70
                let rankdir = 'LR'
                if (!this.graph.getEdges().length) {
                    rankdir = 'DL'
                    nodesep = 50
                    ranksep = 30
                }
                // 防止触碰
                this.mainLoading = true
                const midNodes = this.graph.getNodes().map(e => {
                    return {
                        ...e.get('model')
                    }
                })
                const start = midNodes[0]
                const stop = midNodes[1]
                const arr = [start].concat(midNodes.splice(2)).concat([stop])
                arr.forEach((item, index) => {
                    item.idx = index
                    this.graph.updateItem(item.id, item)
                })
                this.graph.updateLayout({
                    type: 'dagre',
                    rankdir: rankdir, // 可选，默认为图的中心
                    // align: 'DL', // 可选
                    nodesep: nodesep, // 可选,节点竖直间距
                    ranksep: ranksep, // 可选,节点水平间距
                    controlPoints: false // 可选
                })
                setTimeout(() => {
                    this.mainLoading = false
                }, 1000)
            },
            // 处理前置作业流节点连线模式确认
            handleFlowAddEdgeConfirm() {
                if (this.$refs.addModeDialog.modeValue === 'flow') {
                    setTimeout(() => {
                        this.graph.addItem('edge', {
                            id: getUUID(32, 16),
                            source: this.flowModeDialog.curObj.sourceNode.get('id'),
                            target: this.flowModeDialog.curObj.targetNode.get('id'),
                            gateWay: {
                                name: '', // 分支名
                                expression: '' // 条件表达式
                            }
                        })
                    }, 100)
                    this.flowModeDialog.show = false
                } else {
                    const edges = this.flowModeDialog.curObj.sourceNode.getEdges()
                    // 表明已有其他前置连线，收集前置节点连线
                    if (edges.length) {
                        this.flowModeDialog.preEdges = edges.filter(item => {
                            return item.getModel().hasOwnProperty('label')
                        })
                    }
                    this.flowModeDialog.childDialog.title = this.flowModeDialog.curObj.sourceNode.getModel().name
                    this.flowModeDialog.childDialog.footerShow = true
                    this.flowModeDialog.childDialog.show = true
                }
            },
            // 处理选择前置作业流中的某个作业节点确认
            handlePreFlowNOdeAddConfirm() {
                if (!this.$refs.preFlowCanvas.currentChooseNode) {
                    this.$cwMessage('当前作业节点未选择，至少选择一个作业节点！', 'warning')
                } else {
                    const _this = this
                    setTimeout(() => {
                        const label = `${_this.$refs.preFlowCanvas.currentChooseNode.name}→${_this.flowModeDialog.curObj.targetNode.getModel().name}`
                        this.graph.addItem('edge', {
                            id: getUUID(32, 16),
                            source: _this.flowModeDialog.curObj.sourceNode.get('id'),
                            target: _this.flowModeDialog.curObj.targetNode.get('id'),
                            label: label.length > 10 ? `${label.substr(0, 10)}...` : label,
                            rely_node: {
                                name: label,
                                label: label.length > 10 ? `${label.substr(0, 10)}...` : label,
                                content: _this.$refs.preFlowCanvas.currentChooseNode.content,
                                id: _this.$refs.preFlowCanvas.currentChooseNode.id
                            },
                            gateWay: {
                                name: '', // 分支名
                                expression: '' // 条件表达式
                            }
                        })
                        _this.flowModeDialog.childDialog.show = false
                        _this.flowModeDialog.show = false
                    }, 100)
                }
            },
            // 处理获取作业流数据
            getSingleJobFlow() {
                this.$api.process.retrieve(parseInt(this.$route.query.job_flow_data)).then(res => {
                    if (res.result) {
                        this.jobFlowFrom = res.data
                        if (this.$route.query.type === 'detail') {
                            this.handleRender(true)
                        } else {
                            this.handleRender(false)
                        }
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                })
            },
            // 处理渲染，true为详情方式渲染，false为编辑或新增方式渲染
            handleRender(detail) {
                this.mainLoading = true
                const _this = this
                setTimeout(() => {
                    const data = {
                        edges: _this.jobFlowFrom.pipeline_tree.lines.map(line => {
                            const item = {
                                detail: detail,
                                id: getUUID(32, 16),
                                source: line.from,
                                target: line.to,
                                getWay: {
                                    name: line.hasOwnProperty('getWay') ? line.getWay.name : '',
                                    expression: line.hasOwnProperty('getWay') ? line.getWay.expression : ''
                                }
                            }
                            if (item.getWay.name !== '') {
                                item.label = line.getWay.name.length > 4 ? `${item.getWay.name.substr(0, 4)}...` : line.getWay.name
                            }
                            return item
                        }),
                        nodes: _this.jobFlowFrom.pipeline_tree.nodes.map((node, index) => {
                            let style = {}
                            if (node.type === 0 || node.type === 1) {
                                style = {
                                    fill: '#fff',
                                    stroke: '#DCDEE5',
                                    lineWidth: 1,
                                    r: 24
                                }
                            } else if (node.type === 4 || node.type === 5) {
                                style = {
                                    fill: '#fff',
                                    stroke: '#DCDEE5',
                                    lineWidth: 1,
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
                                label: node.name.length > 8 ? `${node.name.substr(0, 8)}...` : node.name,
                                name: node.name,
                                icon: node.ico,
                                id: node.hasOwnProperty(node.end_uuid) ? node.end_uuid : node.uuid,
                                endUuid: node.hasOwnProperty(node.end_uuid) ? node.end_uuid : '', // 有enduuid表明为作业流，加上enduuid,没有为空
                                x: node.left,
                                y: node.top,
                                nodeType: node.type,
                                type: (node.type === 0 || node.type === 1 || node.type === 4) ? 'circle-node' : 'rect-node',
                                labelCfg: {
                                    style: {
                                        textAlign: (node.type === 0 || node.type === 1) ? 'center' : 'left'
                                    }
                                },
                                style: {
                                    ...style
                                }
                            }
                        })
                    }
                    _this.graph.read(data)
                    _this.mainLoading = false
                }, 2000)
            },
            // 处理更新节点的数据
            handleUpdateNode(data, id) {
                const item = this.graph.findById(id).get('model')
                item.node_data = data
                this.graph.updateItem(id, item)
            },
            // 处理更新线的数据
            handleUpdateEdge(data, id) {
                const item = this.graph.findById(id).get('model')
                item.label = data.name.length > 4 ? `${data.name.substr(0, 4)}...` : data.name
                item.getWay = data
                this.graph.updateItem(id, item)
                this.edgeDrawer.show = false
            },
            // 处理清空画布和任务编排, flag判断是否刷新任务编排组件
            handleEmptyTaskMake(flag) {
                this.mainLoading = true
                if (flag) {
                    this.taskMakeKey += 1
                }
                if (this.$route.query.type !== 'add') {
                    this.jobFlowFrom.category = '' // 这个地方是为了防止task组件key值刷新后，在task组件mounted周期中跑批id重新获取
                }
                this.$cwMessage('清空画布', 'primary')
                this.graph.clear()
                const data = {
                    nodes: [{
                        ...this.nodes[0],
                        id: getUUID(32, 16)
                    // uuid: getUUID(32, 16)
                    }, {
                        ...this.nodes[1],
                        id: getUUID(32, 16)
                    // uuid: getUUID(32, 16)
                    }]
                }
                this.graph.read(data)
                this.mainLoading = false
            },
            // 处理保存
            handleSave(params) {
                // this.mainLoading = true
                if (this.$route.query.type === 'add') {
                    this.$api.process.create(params).then(res => {
                        if (res.result) {
                            this.checkFlag = false
                            this.$cwMessage('添加成功', 'success')
                            this.$router.push({
                                path: '/jobflowlist'
                            })
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                        this.mainLoading = false
                    })
                } else if (this.$route.query.type === 'update') {
                    this.$api.process.update(parseInt(this.$route.query.job_flow_data), params).then(res => {
                        if (res.result) {
                            this.checkFlag = false
                            this.$cwMessage('修改成功', 'success')
                            this.$router.push({
                                path: '/jobflowlist'
                            })
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                        this.mainLoading = false
                    })
                } else if (this.$route.query.type === 'clone') {
                    params.id = parseInt(this.$route.query.job_flow_data)
                    this.$api.process.clone(params).then(res => {
                        if (res.result) {
                            this.checkFlag = false
                            this.$cwMessage('克隆成功', 'success')
                            this.$router.push({
                                path: '/jobflowlist'
                            })
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                        this.mainLoading = false
                    })
                }
            },
            // 初始化graph监听函数
            initGraphEvent() {
                // 监听节点选中
                this.graph.on('after-node-selected', e => {
                    if (e.item.getModel().nodeType !== 3) {
                        this.handleOpenNodeDrawer(e)
                    } else {
                        this.handleOpenFlowDrawer(e)
                    }
                })
                // 监听节点连线
                this.graph.on('before-edge-add', (flag, obj) => {
                    this.handleEdgeAdd(flag, obj)
                })
                // 监听删除连线
                this.graph.on('before-delete-edge', e => {
                    this.handleDeleteEdge(e)
                })
                // 监听编辑连线
                this.graph.on('before-edit-edge', e => {
                    this.handleOpenEdgeInfo(e)
                })
                // 监听详情状态下打开分支连线信息
                this.graph.on('before-open-edge', e => {
                    this.handleOpenEdgeInfo(e)
                })
                // 监听删除节点
                this.graph.on('before-delete-node', e => {
                    this.handleDeleteNode(e.item)
                })
            },
            handleOpenFlowDrawer(e) {
                this.flowModeDialog.preEdges = []
                const edges = e.item.getEdges()
                console.log(123, e.item.getModel())
                // 表明已有其他前置连线，收集前置节点连线
                if (edges.length) {
                    this.flowModeDialog.preEdges = edges.filter(item => {
                        return item.getModel().hasOwnProperty('label')
                    })
                }
                this.flowModeDialog.curObj = { sourceNode: e.item }
                this.flowModeDialog.childDialog.title = e.item.getModel().name
                this.flowModeDialog.childDialog.footerShow = false
                this.flowModeDialog.childDialog.show = true
            },
            // 打开分支连线抽屉
            handleOpenEdgeInfo(e) {
                const model = e.item.get('model')
                this.edgeData = {
                    data: deepClone(model.getWay), // 深拷贝分支连线数据
                    id: model.id
                }
                // 如果当前分支连线标题不为空，默认抽屉表题为分支连线标题
                if (model.getWay && model.getWay.name !== '') {
                    this.edgeDrawer.title = model.getWay.name
                } else {
                    this.edgeDrawer.title = '标题'
                }
                this.edgeDrawer.show = true
            },
            // 监听删除连线
            handleDeleteEdge(e) {
                this.$bkInfo({
                    type: 'warning',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        const model = e.item.get('model')
                        this.graph.removeItem(model.id)
                    }
                })
            },
            // 清空所有节点状态
            clearAllState() {
                const selectedNodes = this.graph.findAllByState('node', 'nodeState:selected')
                selectedNodes.forEach(node => {
                    node.clearStates(['nodeState:selected', 'nodeState:hover'])
                })
            },
            // 处理节点连线
            handleEdgeAdd(flag, obj) {
                if (flag) {
                    setTimeout(() => {
                        this.graph.addItem('edge', {
                            id: getUUID(32, 16),
                            source: obj.sourceNode.get('id'),
                            target: obj.targetNode.get('id'),
                            getWay: {
                                name: '', // 分支名
                                expression: '' // 条件表达式
                            }
                        })
                    }, 100)
                } else {
                    this.$cwMessage(obj.msg, 'error')
                }
            },
            // 处理节点信息关闭
            handleNodeDrawerClose(flag) {
                if (flag) {
                    this.nodeDrawer.show = false
                }
                this.clearAllState()
            },
            // 处理分支信息关闭
            handleEdgeDrawerClose() {
                this.edgeDrawer.show = false
            },
            // 处理打开节点信息抽屉
            handleOpenNodeDrawer(e) {
                const model = e.item.get('model')
                this.nodeData = {
                    data: deepClone(model.node_data), // 深拷贝节点数据
                    id: model.id
                }
                this.nodeSliderKey += 1
                this.nodeDrawer.show = true
                this.nodeDrawer.title = model.name
            },
            // 处理删除节点
            handleDeleteNode(item) {
                this.$bkInfo({
                    type: 'warning',
                    title: '确认要删除吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.graph.removeItem(item)
                    }
                })
            },
            // 创建画布
            createGraphic() {
                this.mainLoading = true
                // 创建内容超出提示
                const tooltip = new G6.Tooltip({
                    offsetX: 50,
                    offsetY: -100,
                    itemTypes: ['node'],
                    // 自定义 tooltip 内容
                    getContent: (e) => {
                        const outDiv = document.createElement('div')
                        outDiv.innerHTML = `<span>${e.item.getModel().name}</span>`
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
                // 工厂函数注册自定义节点
                const cfg = registerFactory(G6, {
                    width: this.$refs.main.clientWidth,
                    height: this.$refs.main.clientHeight,
                    animate: true, // Boolean，可选，切换布局时是否使用动画过度
                    defaultNode: {
                        ...options.defaultNode
                    },
                    modes: {
                        default: [
                            ...options.modes,
                            {
                                type: 'drag-node',
                                shouldBegin: e => {
                                    if (e.target.cfg.isAnchor) return false
                                    return true
                                }
                            },
                            {
                                type: 'create-edge',
                                trigger: 'drag',
                                edgeConfig: {
                                    type: 'polyline-edge'
                                },
                                shouldBegin: e => {
                                    if (e.target.cfg.isAnchor) {
                                        this.dragStartNode = {
                                          ...e.item._cfg,
                                          anchorIndex: e.target.cfg.index
                                        }
                                        return true
                                    } else {
                                        return false
                                    }
                                },
                                shouldEnd: e => {
                                    const targetNode = e.item.getContainer().get('item') // 目标节点
                                    const sourceNode = this.dragStartNode.group.get('item') // 起始节点
                                    // 自己连自己
                                    if (targetNode._cfg.id === sourceNode._cfg.id) {
                                        this.graph.emit('before-edge-add', false, {msg: '无效的操作！'})
                                        return false
                                    }
                                    // 开始节点直连结束节点
                                    if (targetNode._cfg.model.nodeType === 1 && sourceNode._cfg.model.nodeType === 0) {
                                        this.graph.emit('before-edge-add', false, {msg: '禁止开始节点直连结束节点！'})
                                        return false
                                    }
                                    // 结束节点直连开始节点
                                    if (targetNode._cfg.model.nodeType === 0 && sourceNode._cfg.model.nodeType === 1) {
                                        this.graph.emit('before-edge-add', false, {msg: '禁止结束节点直连开始节点！'})
                                        return false
                                    }
                                    // 从结束节点开始
                                    if (sourceNode._cfg.model.nodeType === 1) {
                                        this.graph.emit('before-edge-add', false, {msg: '禁止从结束节点开始！'})
                                        return false
                                    }
                                    // 从开始节点结束
                                    if (targetNode._cfg.model.nodeType === 0 && sourceNode._cfg.model.nodeType !== 3) {
                                        this.graph.emit('before-edge-add', false, {msg: '禁止从开始节点结束！'})
                                        return false
                                    }
                                    // 从作业流节点结束
                                    if (targetNode._cfg.model.nodeType === 3) {
                                        this.graph.emit('before-edge-add', false, {msg: '禁止从作业流节点结束！'})
                                        return false
                                    }
                                    let msg = ''
                                    this.graph.getEdges().forEach(line => {
                                        // 重复连线
                                        if (line._cfg.model.source === sourceNode._cfg.id && line._cfg.model.target === targetNode._cfg.id) {
                                            msg = '禁止重复连线'
                                        }
                                        // 回环连线
                                        if (sourceNode._cfg.id === line._cfg.model.target && targetNode._cfg.id === line._cfg.model.source) {
                                            msg = '禁止回环连线'
                                        }
                                    })
                                    // 重复连线
                                    if (msg) {
                                        this.graph.emit('before-edge-add', false, {msg: msg})
                                        return false
                                    }
                                    this.graph.emit('before-edge-add', true, {
                                        targetNode,
                                        sourceNode
                                    })
                                    return false
                                }
                            }
                        ]
                    },
                    defaultEdge: {
                        ...options.defaultEdge
                    },
                    // 覆盖全局样式
                    nodeStateStyles: {
                        ...options.nodeStateStyles
                    },
                    // 默认边不同状态下的样式集合
                    edgeStateStyles: {
                        ...options.edgeStateStyles
                    },
                    // linkCenter: true,
                    // plugins: this.$route.query.type === 'detail' ? [tooltip] : [menu, tooltip],
                    plugins: [tooltip]
                })
                // 创建graph实例
                this.graph = new G6.Graph(cfg)
                // 读取数据，默认添加开始结束节点
                if (this.$route.query.type !== 'add') {
                    return false
                } else {
                    const data = {
                        nodes: this.nodes
                    }
                    this.graph.read(data)
                }
                this.mainLoading = false
            },
            // 处理添加节点
            // todo 节点
            handleAddNode(e) {
                const {
                    x,
                    y
                } = this.graph.getPointByClient(e.x, e.y)
                const model = {
                    detail: false,
                    style: {
                        width: 154,
                        height: 40,
                        radius: 20,
                        zIndex: 20,
                        iconCfg: {
                            fill: '#3a84ff'
                        }
                    },
                    node_data: {
                        inputs: {
                            url: '',
                            method: 'get',
                            header: [
                                {
                                    key: '',
                                    value: ''
                                }],
                            body: '{}',
                            timeout: 60,
                            check_point: {
                                key: '',
                                condition: '',
                                values: ''
                            }
                        },
                        run_mark: 0,
                        node_name: e.target.innerText,
                        description: '',
                        fail_retry_count: 0,
                        fail_offset: 10,
                        fail_offset_unit: 'seconds',
                        is_skip_fail: false,
                        is_timeout_alarm: false
                    },
                    label: e.target.innerText.length > 8 ? `${e.target.innerText.substr(0, 8)}...` : e.target.innerText,
                    name: e.target.innerText,
                    icon: e.target.dataset.icon,
                    endUuid: e.target.dataset.enduuid,
                    id: e.target.dataset.enduuid ? e.target.dataset.enduuid : getUUID(32, 16), // 外部作业流uuid和enduuid要一致
                    // uuid: e.target.dataset.enduuid ? e.target.dataset.enduuid : getUUID(32, 16),
                    nodeType: parseInt(e.target.dataset.nodetype), // 节点类型
                    content: parseInt(e.target.dataset.content), // 作业id
                    type: 'rect-node',
                    x,
                    y
                }
                console.log('model', model)
                if (model.endUuid !== '' && this.graph.findById(model.endUuid)) {
                    return this.$cwMessage('相同作业流已存在，不可重复添加', 'warning')
                }
                const node = this.graph.addItem('node', model)
                this.nodes.push(node)
            },
            // 处理关闭信息编排抽屉
            handleDrawerClose() {
                this.$refs.headerPanel.isActive = 0
            },
            handleDrawerCloseBefore() {
                const promise = new Promise((resolve, reject) => {
                    if (this.$refs.baseInfo.form.type === '') {
                        this.$bkInfo({
                            type: 'primary',
                            title: '请确认是否退出当前操作',
                            subTitle: '请注意需要先完善调度方式的填写，才能进行任务编排！',
                            confirmLoading: false,
                            confirmFn: async() => {
                                resolve()
                            }
                        })
                    } else {
                        resolve()
                    }
                })
                return promise
            }
        }
    }
</script>

<style lang="scss" scoped>
    #singleJobFlow {
        height: 100%;
        width: 100%;

        .node-drawer {

            // height: 100%;
            /deep/ .custom-sidelider {
                .bk-sideslider-wrapper {
                    .bk-sideslider-content {
                        height: calc(100% - 60px) !important;
                        .content {
                            overflow-x: hidden;
                        }
                    }
                }
            }
        }

        #main {
            overflow: hidden;
            height: calc(100% - 56px);
            width: 100%;
            position: relative;
            background-image: linear-gradient(90deg, rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%), linear-gradient(rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%);
            background-size: 10px 10px;

            /deep/ .right-click-menu:hover {
                color: rgb(24, 144, 255);
            }

            /deep/ .right-click-menu {
                text-align: center;
            }

            .taskFormatDrawer {
                /deep/ .ivu-drawer-wrap-inner {
                    z-index: 10;
                    .ivu-drawer-body {
                        overflow-x: hidden;
                    }
                    .ivu-drawer-body::-webkit-scrollbar{
                      width: 0;
                    }
                }
            }

            /deep/ .custom-drawer {
                .ivu-drawer {
                    border: 1px solid #DCDEE5;

                    .ivu-drawer-header {
                        .ivu-drawer-header-inner {
                            font-size: 18px;
                            color: #313237;
                        }
                    }

                    .ivu-drawer-body {
                        padding: 20px 20px;
                    }
                }
            }
        }
    }
</style>
