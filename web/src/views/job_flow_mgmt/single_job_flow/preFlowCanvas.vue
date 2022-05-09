<template>
    <div id="preFlowCanvas" v-bkloading="{ isLoading: mainLoading, zIndex: 999999 }">
        <div class="header">
            <div class="select-node">
                <span>已使用依赖的节点：</span>
                <span class="text" v-if="allChooseNode.length"
                    v-bk-tooltips="{ placement: 'bottom', width: 300, content: `${allChooseNode.join(',  ')}` }">{{allChooseNode.join(', ')}}</span>
                <span v-else>- -</span>
            </div>
            <div class="current-select">
                <span>当前选择的节点：</span>
                <span class="text" v-if="currentChooseNode" :title="`${currentChooseNode.name}`">{{currentChooseNode.name}}</span>
                <span v-else>- -</span>
            </div>
        </div>
        <div ref="mainFlow" class="mainFlow" id="mainFlow"></div>
        <div style="height: 150px;width: 150px;position: absolute;bottom: 0px;right: 0px;border: 1px solid #ccc;" ref="miniMap"></div>
    </div>
</template>

<script>
    import baseNodes from './baseNode.js'
    import options from './options.js'
    import registerFactory from '@/components/graph/graph.js'
    import G6 from '@antv/g6'
    import {
        getUUID
    } from '../../../common/util.js'
    export default {
        props: {
            options: {
                type: Object,
                default: () => {}
            },
            preEdges: {
                type: Array,
                default: () => []
            }
        },
        data() {
            return {
                allChooseNode: [],
                currentChooseNode: null,
                jobFlowFrom: null,
                graph: null,
                mainLoading: false,
                basicNodes: [{
                        ...baseNodes[0],
                        id: getUUID(32, 16)
                             },
                             {
                        ...baseNodes[1],
                        id: getUUID(32, 16)
                             }
                ]
            }
        },
        created() {
            this.getSingleJobFlow()
            this.allChooseNode = this.preEdges.map(item => {
                const model = item.getModel()
                return `${model.rely_node.name}`.split('→')[0]
            })
            this.allChooseNode = Array.from(new Set(this.allChooseNode))
        },
        mounted() {
            // 创建画布并绑定相关事件
            this.$nextTick(() => {
                this.createGraphic()
                this.initGraphEvent()
            })
        },
        beforeDestroy() {
            this.graph.destroy()
        },
        methods: {
            // 初始化graph监听函数
            initGraphEvent() {
                // 监听节点选中
                this.graph.on('after-node-selected', e => {
                    const model = e.item.getModel()
                    if (model.nodeType !== 3) {
                        this.currentChooseNode = model
                    }
                })
            },
            getSingleJobFlow() {
                this.mainLoading = true
                const model = this.options.sourceNode.getModel()
                console.log('model', model)
                this.$api.process.retrieve(model.content).then(res => {
                    if (res.result) {
                        this.jobFlowFrom = res.data
                        this.handleRender(true)
                    } else {
                        this.$cwMessage(res.message, 'error')
                        this.mainLoading = false
                    }
                })
            },
            handleRender(detail) {
                console.log('pre render')
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
                                gateWay: {
                                    name: line.hasOwnProperty('gateWay') ? line.gateWay.name : '',
                                    expression: line.hasOwnProperty('gateWay') ? line.gateWay
                                        .expression : ''
                                }
                            }
                            if (item.gateWay.name !== '') {
                                item.label = line.gateWay.name.length > 7
                                    ? `${item.gateWay.name.substr(0, 7)}...` : line.gateWay.name
                            }
                            if (line.hasOwnProperty('rely_node')) {
                                item.rely_node = line.rely_node
                                item.label = line.rely_node.label
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
                            } else {
                                style = {
                                    width: 154,
                                    height: 40,
                                    radius: 20,
                                    stroke: '#DCDEE5',
                                    lineWidth: 1,
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
                                id: node.hasOwnProperty(node.end_uuid) ? node.end_uuid : node.uuid,
                                endUuid: node.hasOwnProperty(node.end_uuid) ? node.end_uuid
                                    : '', // 有enduuid表明为作业流，加上enduuid,没有为空
                                x: Number(node.left),
                                y: Number(node.top),
                                nodeType: node.type,
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
                    // 如果有前置已选节点，需要给它加上已选的样式
                    if (this.preEdges.length) {
                        const nodes = this.graph.getNodes()
                        this.preEdges.forEach(edge => {
                            nodes.forEach(node => {
                                if (edge.getModel().rely_node.id === node.getModel().id) {
                                    const model = node.getModel()
                                    model.choose = true
                                    this.graph.updateItem(model.id, model)
                                    node.setState('nodeState:preselected')
                                }
                            })
                        })
                    }
                    _this.mainLoading = false
                }, 300)
            },
            // 创建画布
            createGraphic() {
                this.mainLoading = true
                const _this = this
                // 创建内容超出提示
                const tooltip = new G6.Tooltip({
                    offsetX: -10,
                    offsetY: -10,
                    itemTypes: ['node', 'edge'],
                    // 自定义 tooltip 内容
                    getContent: (e) => {
                        let content = ''
                        if (e.item._cfg.type === 'edge' && e.target.cfg.type !== 'path') {
                            content = e.item.getModel().gateWay.name
                        } else {
                            content = e.item.getModel().name
                        }
                        const outDiv = document.createElement('div')
                        outDiv.innerHTML = `<span>${content}</span>`
                        return outDiv
                    },
                    shouldBegin(e) {
                        const model = e.item.get('model')
                        if (e.item._cfg.type === 'edge') {
                            if (e.target.cfg.type !== 'path' && !e.target.cfg.attrs.hasOwnProperty(
                                'fontFamily')) {
                                return true
                            }
                            return false
                        }
                        // 触发方式，只有在内容超出8个字符的情况下才触发
                        if (model.nodeType === 0 || model.nodeType === 1 || model.name.length <= 8) {
                            return false
                        }
                        return true
                    }
                })
                const minimap = new G6.Minimap({
                    container: _this.$refs.miniMap,
                    size: [150, 150]
                })
                // 工厂函数注册自定义节点
                const cfg = registerFactory(G6, {
                    container: 'mainFlow',
                    width: 880,
                    height: 500,
                    fitView: true,
                    maxZoom: 1, // 最大缩放比例
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
                    plugins: [tooltip, minimap]
                })
                // 创建graph实例
                this.graph = new G6.Graph(cfg)
                // const data = {
                //     nodes: this.basicNodes
                // }
                // this.graph.read(data)
            }
        }
    }
</script>

<style scoped lang="scss">
    #preFlowCanvas {
        height: 100%;
        width: 100%;
        position: relative;
        .header {
            display: flex;
            margin-bottom: 15px;
            font-size: 14px;
            color: #313237;

            .select-node {
                display: flex;
                align-items: center;

                .text {
                    max-width: 350px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: inline-block;
                }
            }

            .current-select {
                display: flex;
                align-items: center;
                margin-left: 55px;

                .text {
                    max-width: 200px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: inline-block;
                }

                // width: 250px;
                // white-space:nowrap;
                // overflow:hidden;
                // text-overflow:ellipsis;
            }
        }

        #mainFlow {
            width: 100%;
            height: 500px;
            position: relative;
            background-image: linear-gradient(90deg, rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%), linear-gradient(rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%);
            background-size: 10px 10px;
            overflow: hidden;
            border-bottom: 1px solid rgba(180, 180, 180, 0.15);
        }
    }
</style>
