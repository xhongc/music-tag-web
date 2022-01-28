<template>
    <div id="largeScreen" ref="largeScreen" v-bkloading="{ isLoading: largeScreenLoading, zIndex: 10 }">
        <!--   <fullscreen ref="fullscreen" @change="fullscreenChange" id="fullscreen"> -->
        <bk-resize-layout :collapsible="true" :border="false" style="height: 100%;" initial-divide="272px" :disabled="true"
            @collapse-change="handleCollapseChange" ext-cls="custom-layout">
            <div slot="aside" style="height: 100%;" class="left" ref="aside">
                <left-tree @change-canvas-size="handleChangeCavasSize" @node-select="handleTreeNodeSelect" ref="tree"
                    :key="treeKey"></left-tree>
            </div>
            <div slot="main" style="height: 100%;" class="right" v-bkloading="{ isLoading: mainLoading, zIndex: 10 }">
                <div class="left-status-list">
                    <status-list style="position: absolute;left: 20px;top: 15px;"></status-list>
                </div>
                <div class="right-canvas" id="main" ref="main"></div>
                <div class="top-menu">
                    <top-menu @full-screen="handleFullScreen" ref="topMenu" @open-sys-screen="handleOpenSysScreen"
                        @open-job-flow="handleOpenJobFlow" @on-reset="hanldeReset"></top-menu>
                </div>
            </div>
        </bk-resize-layout>
        <!-- </fullscreen> -->
    </div>
</template>

<script>
    import {
        deepClone, getUUID
    } from '../../common/util.js'
    import leftTree from './tree.vue'
    import statusList from './statusList.vue'
    import topMenu from './topMenu.vue'
    import registerFactory from '@/components/graph/graph.js'
    import G6 from '@antv/g6'
    import fullscreen from 'vue-fullscreen'
    import Vue from 'vue'
    Vue.use(fullscreen)
    export default {
        components: {
            leftTree,
            statusList,
            topMenu
        },
        data() {
            return {
                treeKey: 0,
                tooltip: null,
                fullscreen: false,
                largeScreenLoading: false,
                mainLoading: false,
                graph: null,
                cfg: {},
                sysData: {},
                flowData: {}
            }
        },
        mounted() {
            // 创建画布
            this.$nextTick(() => {
                this.createGraphic()
                this.initGraphEvent()
            })
            // 监听屏幕大小变化改变画布
            window.addEventListener('resize', this.handleChangeCavasSize, false)
            // let aside = document.getElementsByClassName('')
        },
        created() {
            this.getAllRunSys()
        },
        beforeDestroy() {
            this.graph.destroy()
            window.removeEventListener('resize', this.handleChangeCavasSize, false)
        },
        methods: {
            handleCollapseChange(flag) {
                if (flag === true) {
                    this.$nextTick(() => {
                        const aside = document.getElementsByClassName('bk-resize-layout-aside')
                        aside[0].style.width = 0
                    })
                }
            },
            // 处理复位
            hanldeReset() {
                this.graph.fitCenter()
            },
            // 处理打开跑批系统大屏
            handleOpenSysScreen(e) {
                this.$refs.tree.$refs.topoTree.setSelected(e, {
                    emitEvent: false,
                    beforeSelect: true
                })
                this.getAllRunSys()
            },
            // 处理打开作业流大屏
            handleOpenJobFlow(e) {
                this.$api.process.get_topology().then(res => {
                    if (res.result) {
                        this.flowData = res.data
                        this.renderCanvas(true, this.flowData)
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.largeScreenLoading = false
                })
            },
            // 处理拓扑树选择
            handleTreeNodeSelect(e) {
                this.$refs.topMenu.viewBtnActive = 2
                let id = e.id
                if (id === 'all') {
                    id = ''
                }
                this.getJobFlowByRunId(id)
            },
            // 处理改变画布大小
            handleChangeCavasSize() {
                this.graph.changeSize(this.$refs.main.clientWidth, this.$refs.main.clientHeight)
            },
            // 处理全屏
            handleFullScreen() {
                this.$fullscreen.toggle(this.$refs.largeScreen, {
                    wrap: false,
                    callback: this.fullscreenChange
                })
            },
            // 处理全屏
            fullscreenChange(fullscreen) {
                this.fullscreen = fullscreen
            },
            initOption() {
                // 工厂函数注册自定义节点
                this.cfg = registerFactory(G6, {
                    width: this.$refs.main.clientWidth,
                    height: this.$refs.main.clientHeight,
                    fitView: true,
                    maxZoom: 1,
                    animate: true, // Boolean，可选，切换布局时是否使用动画过度
                    layout: {
                        type: 'dagre',
                        rankdir: 'LR', // 可选，默认为图的中心
                        align: 'DL', // 可选
                        nodesep: 20, // 可选
                        ranksep: 50, // 可选
                        controlPoints: false // 可选
                    },
                    // layout: {
                    //     type: 'xxx', // 位置将固定
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
                    plugins: [this.tooltip],
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
                // 创建内容超出提示
                this.tooltip = new G6.Tooltip({
                    offsetX: 10,
                    offsetY: 10,
                    itemTypes: ['node'],
                    // 自定义 tooltip 内容
                    getContent: (e) => {
                        const outDiv = document.createElement('div')
                        const model = e.item.getModel()
                        outDiv.style.width = 'fit-content'
                        outDiv.className = 'node-tool-tip'
                        outDiv.innerHTML =
                            `<ul>
                                    <li>作业总数：${model.info.jobCount}</li>
                                    <li>成功：${model.info.successCount}</li>
                                    <li>正在执行：${model.info.operatingCount}</li>
                                    <li>失败：${model.info.failureCount}</li>
                                    <li>错误：${model.info.errorCount}</li>
                                    <li>等待：${model.info.waitCount}</li>
                                    <li>挂起：${model.info.pauseCount}</li>
                                    <li>取消：${model.info.cancelCount}</li>
                                    <li>尚未实例化作业数：${model.info.todayNotExecuteCount}</li>
                                 </ul>`
                        return outDiv
                    }
                    // shouldBegin(e) {
                    //     const model = e.item.get('model')
                    //     return true
                    // }
                })
            },
            // 获取所有跑批系统
            getAllRunSys() {
                this.largeScreenLoading = true
                this.$api.category.get_topology().then(res => {
                    if (res.result) {
                        this.sysData = res.data
                        this.renderCanvas(true, this.sysData)
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.largeScreenLoading = false
                })
            },
            renderCanvas(detail, cavnsData) {
                this.mainLoading = true
                if (this.$refs.topMenu.viewBtnActive === 1) {
                    this.getCavasData(detail, 5, cavnsData)
                } else {
                    this.getCavasData(detail, 3, cavnsData)
                }
            },
            // 初始化画布数据，渲染画布
            getCavasData(detail, nodeType, cData) {
                const _this = this
                const cavasData = deepClone(cData)
                setTimeout(() => {
                    const data = {
                        edges: cavasData.lines.map(line => {
                            return {
                                detail: detail,
                                id: getUUID(32, 16),
                                source: line.from.toString(),
                                target: line.to.toString()
                            }
                        }),
                        nodes: cavasData.nodes.map((node, index) => {
                            return {
                                ...node,
                                detail: detail,
                                label: node.label.length > 9 ? `${node.label.substr(0, 9)}` : node
                                    .label,
                                name: node.label,
                                icon: '',
                                id: node.id.toString(),
                                // x: (index + 1) * 70,
                                // y: (index + 1) * 50,
                                nodeType: nodeType,
                                state: node.state,
                                type: 'rect-node',
                                labelCfg: {
                                    style: {
                                        textAlign: 'left'
                                    }
                                },
                                style: {
                                    width: 154,
                                    height: 40,
                                    radius: 20,
                                    iconCfg: {
                                        fill: '#3a84ff'
                                    }
                                }
                            }
                        })
                    }
                    _this.graph.read(data)
                    // _this.graph.fitCenter()
                    _this.mainLoading = false
                }, 2000)
            },
            createGraphic() {
                // 创建菜单
                this.createMenu()
                // 初始化配置项
                this.initOption()
                // 创建graph实例
                this.graph = new G6.Graph(this.cfg)
            },
            initGraphEvent() {
                this.graph.on('node:click', e => {
                    const model = e.item.get('model')
                    if (model.nodeType === 3) {
                        if (model.instance_id) {
                            // 消除由于keepalive快照导致从作业流详情回退后找不到dom
                            if (this.fullscreen) {
                                this.handleFullScreen()
                            }
                            setTimeout(() => {
                                this.$router.push({
                                    path: '/viewdetail',
                                    query: {
                                        id: model.instance_id
                                    }
                                })
                            }, 300)
                        } else {
                            this.$cwMessage('该作业流尚未实例化!', 'primary')
                        }
                        return false
                    }
                    this.$refs.tree.treeSeachVal = ''
                    this.$refs.tree.filterTree('')
                    this.$refs.tree.$refs.topoTree.setSelected(parseInt(model.id), {
                        emitEvent: false,
                        beforeSelect: true
                    })
                    this.$refs.topMenu.viewBtnActive = 2
                    // 根据跑批id获取相关作业流
                    this.getJobFlowByRunId(model.id)
                })
            },
            // 根据跑批id获取相关作业流
            getJobFlowByRunId(id) {
                this.largeScreenLoading = true
                this.$api.process.get_topology({
                    category: id
                }).then(res => {
                    if (res.result) {
                        this.flowData = res.data
                        this.renderCanvas(true, this.flowData)
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.largeScreenLoading = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #largeScreen {
        height: 100%;
        background-color: #fff;

        .custom-layout {
            /deep/ .bk-resize-layout-aside:after {
                width: 0;
            }
        }

        .left {
            padding: 16px 16px 0 16px;
        }

        .right {
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
            background-image: linear-gradient(90deg, rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%), linear-gradient(rgba(180, 180, 180, 0.15) 10%, rgba(0, 0, 0, 0) 10%);
            background-size: 10px 10px;
            display: flex;

            .left-status-list {
                height: 100%;
                width: 150px;
            }

            #main {
                width: 100%;
                height: 100%;

                /deep/ .node-tool-tip {
                    ul {
                        li {
                            padding: 2px;
                        }
                    }
                }

                // cursor: pointer;
            }

            .top-menu {
                position: absolute;
                right: 0px;
                top: 0px;
                padding-top: 20px;
                padding-right: 19px;
            }
        }
    }
</style>
