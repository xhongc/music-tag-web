<template>
    <div id="jobFlowDetail">
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
        <div class="box" v-bkloading="{ isLoading: mainLoading, zIndex: 999999 }">
            <p class="title">执行详情</p>
            <div id="content">
                <div class="left-statusList">
                    <statusList style="position: absolute;left: 20px;top: 15px;"></statusList>
                </div>
                <div class="right-canvas">
                    <div id="main" ref="main"></div>
                </div>
            </div>
        </div>
        <div class="box">
            <p class="title">前置命令检测</p>
            <!-- <bk-input :type="'textarea'" :rows="8" ext-cls="custom-textarea" :disabled="true" v-model="form.pre_commands"></bk-input> -->
            <editor :height="'200px'" ref="editor" :codes="form.pre_commands" :read-only="true" :language="'shell'"></editor>
        </div>
        <div class="box">
            <p class="title">先行作业/作业流</p>
            <bk-table :data="form.upstream_nodes" ext-cls="customTable">
                <bk-table-column prop="type" label="类型"></bk-table-column>
                <bk-table-column prop="name" label="名称"></bk-table-column>
                <bk-table-column prop="station" label="Agent"></bk-table-column>
                <bk-table-column prop="state" label="状态"></bk-table-column>
                <bk-table-column prop="eta" label="计划开始时间"></bk-table-column>
                <bk-table-column prop="start_time" label="实际开始时间"></bk-table-column>
                <bk-table-column prop="end_time" label="实际完成时间"></bk-table-column>
            </bk-table>
        </div>
        <div class="box">
            <p class="title">后续作业/作业流</p>
            <bk-table :data="form.downstream_nodes" ext-cls="customTable">
                <bk-table-column prop="type" label="类型"></bk-table-column>
                <bk-table-column prop="name" label="名称"></bk-table-column>
                <bk-table-column prop="station" label="Agent"></bk-table-column>
                <bk-table-column prop="state" label="状态"></bk-table-column>
                <bk-table-column prop="eta" label="计划开始时间"></bk-table-column>
                <bk-table-column prop="start_time" label="实际开始时间"></bk-table-column>
                <bk-table-column prop="end_time" label="实际完成时间"></bk-table-column>
            </bk-table>
        </div>
        <div class="node-drawer">
            <bk-sideslider :is-show.sync="nodeDrawer.show" :quick-close="true" :title="nodeDrawer.title" :width="nodeDrawer.width"
                ext-cls="custom-sidelider">
                <node-info slot="content" :node-data="nodeData" :key="nodeSliderKey">
                </node-info>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import editor from '@/components/monacoEditor'
    import {
        deepClone, getUUID
    } from '../../../common/util.js'
    import registerFactory from '@/components/graph/graph.js'
    import G6 from '@antv/g6'
    import statusList from './job_flow_detail/statusList.vue'
    import nodeInfo from './job_flow_detail/nodeInfo.vue'
    export default {
        components: {
            statusList,
            nodeInfo,
            editor
        },
        data() {
            return {
                nodeSliderKey: 0,
                form: {},
                graph: null,
                mainLoading: false,
                tooltip: null, // 内容超出提示
                cfg: {}, // 配置项
                nodeDrawer: {
                    title: '',
                    show: false,
                    width: 496
                },
                nodeData: {},
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
            this.handleLoad()
        },
        mounted() {
            // 创建画布
            this.$nextTick(() => {
                this.createGraphic()
                this.initGraphEvent()
            })
            window.addEventListener('resize', this.handleChangeCavasSize, false)
        },
        beforeDestroy() {
            window.removeEventListener('resize', this.handleChangeCavasSize, false)
            this.graph.destroy()
        },
        methods: {
            // 处理改变画布大小
            handleChangeCavasSize() {
                this.graph.changeSize(this.$refs.main.clientWidth, 550)
                this.graph.fitView([20, 30, 30, 80])
            },
            handleLoad() {
                this.$api.processHistory.retrieve(parseInt(this.$route.query.id)).then(res => {
                    if (res.result) {
                        this.form = res.data
                        if (this.form.hasOwnProperty('pre_commands')) {
                            this.$refs.editor.monacoEditor.setValue(this.form.pre_commands)
                        }
                        this.renderCanvas(true)
                    } else {
                        this.$cwMessage(res.message, 'error')
                        // this.renderCanvas(false)
                    }
                })
            },
            initGraphEvent() {
                this.graph.on('node:click', e => {
                    const model = e.item.get('model')
                    // 开始节点，结束节点，作业流节点不做处理
                    if (model.nodeType === 0 || model.nodeType === 1 || model.nodeType === 3) {
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
            renderCanvas(detail) {
                this.mainLoading = true
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
                                label: node.name.length > 8 ? `${node.name.substr(0, 8)}...` : node.name,
                                name: node.name,
                                icon: node.ico,
                                id: node.hasOwnProperty('end_uuid') ? node.end_uuid : node.uuid,
                                x: Number(node.left),
                                y: Number(node.top),
                                nodeType: node.type,
                                state: node.state,
                                type: (node.type === 0 || node.type === 1) ? 'circle-node' : 'rect-node',
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
                    offsetX: 20,
                    offsetY: -20,
                    itemTypes: ['node'],
                    // 自定义 tooltip 内容
                    getContent: (e) => {
                        const outDiv = document.createElement('div')
                        outDiv.style.width = 'fit-content'
                        outDiv.innerHTML =
                            `
                      <ul>
                        <li>${e.item.getModel().name}</li>
                      </ul>`
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
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobFlowDetail {
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
            .title {
                margin-bottom: 12px;
                font-size: 14px;
                color: #63656E;
                font-weight: bold;
                height: 22px;
                line-height: 22px;
            }
            .custom-textarea {
                /deep/ textarea {
                    padding: 20px;
                    background-color: rgb(49, 50, 56) !important;
                    color: #C4C6CC !important;
                }
            }
            .customTable {
                /deep/ .bk-table-empty-block {
                    background-color: #fff;
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
                    }
                }
            }

            margin-bottom: 24px;
        }
    }
</style>
