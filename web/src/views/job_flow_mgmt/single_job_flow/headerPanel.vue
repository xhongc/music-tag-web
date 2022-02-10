<template>
    <div id="header-panel">
        <div class="left">
            <div class="box" @click="handleOpenBaseInfo">
                <i class="iconfont icon-mianxingtubiao-jibenxinxi" :style="{ color: isActive === 1 ? '#3A84FF' : '#979BA5' }"></i>
                <p :style="{ color: isActive === 1 ? '#3A84FF' : '#333333' }">基本信息</p>
            </div>
            <div class="box" style="margin-left: 36px;" @click="handleOpenTaskMake" v-if="!disabled">
                <i class="iconfont icon-mianxingtubiao-renwubianpai" :style="{ color: isActive === 2 ? '#3A84FF' : '#979BA5' }"></i>
                <p :style="{ color: isActive === 2 ? '#3A84FF' : '#333333' }">任务编排</p>
            </div>
        </div>
        <div class="right">
            <i class="iconfont icon-xianxingtubiao-fuwei" title="复位" @click="handleReset"></i>
            <i class="iconfont icon-xianxingtubiao-yijianbianpai" title="一键排版" @click="handleLayoutSetting"></i>
            <i class="iconfont icon-xianxingtubiao-baocun" title="保存" @click="handleSave" v-if="!disabled"></i>
        </div>
    </div>
</template>

<script>
    import {
        deepClone
    } from '../../../common/util.js'
    export default {
        // props: ['nodes', 'edges', 'graph', 'controlType'],
        props: {
            graph: {
                type: Object,
                default: null
            },
            controlType: {
                type: String,
                default: ''
            }
        },
        inject: ['father_this'],
        data() {
            return {
                getWayOK: {
                    curGetWayNode: null,
                    flag: true
                },
                all_timenodes_lines: [],
                timeResult: [],
                openResult: [],
                closeResult: [],
                validatorFlag: true, // 上传前校验位
                midNodes: [], // 保存前节点数据处理
                midLines: [],
                isActive: 0,
                disabled: false
            }
        },
        created() {
            if (this.$route.query.type === 'detail') {
                this.disabled = true
            }
            if (this.$route.query.type === 'add') {
                this.isActive = 1
            }
        },
        methods: {
            handleLayoutSetting() {
                this.$emit('layout-setting')
            },
            timeisOk() {
                this.all_timenodes_lines.forEach((item, index) => {
                    let i = 0
                    while (i <= this.all_timenodes_lines[index].length - 1) {
                        const currentTime = this.all_timenodes_lines[index][i].node_data.eta // 获取当前节点时间
                        for (let j = i; j < this.all_timenodes_lines[index].length; j++) {
                            if (this.all_timenodes_lines[index][j].node_data.eta < currentTime) { // 如果当前节点时间的后面有比它小的时间表明校验失败
                                this.timeResult.push({
                                    node1: this.all_timenodes_lines[index][i],
                                    node2: this.all_timenodes_lines[index][j]
                                })
                            }
                        }
                        i++
                    }
                })
            },
            tree_for(currentnode, lastNode, lines, nodes, hasTimeNodes) {
                // 找下一个点
                if (currentnode.uuid === lastNode.uuid) {
                    return
                }
                if (currentnode.node_data.eta) {
                    hasTimeNodes.push(currentnode)
                }
                const nextNodes = []
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].from === currentnode.uuid) {
                        for (let j = 0; j < nodes.length; j++) {
                            if (nodes[j].uuid === lines[i].to) {
                                nextNodes.push(nodes[j])
                                break
                            }
                        }
                    }
                }
                nextNodes.forEach((item, index) => {
                    const tmpHasTimeNodes = deepClone(hasTimeNodes)
                    this.tree_for(item, lastNode, lines, nodes, tmpHasTimeNodes)
                    if (item.uuid === lastNode.uuid) {
                        if (tmpHasTimeNodes.length > 1) {
                            this.all_timenodes_lines.push(tmpHasTimeNodes) // 获取所有的时间节点连线结果
                        }
                    }
                })
            },
            // 打开基本信息或任务编排设置抽屉
            setDrawer(isActive, show, title) {
                this.isActive = isActive
                this.father_this.isActive = isActive
                this.father_this.drawer.show = show
                this.father_this.drawer.title = title
            },
            // 处理打开基本信息抽屉
            handleOpenBaseInfo() {
                this.setDrawer(1, true, '基本信息')
            },
            // 处理打开任务编排抽屉
            handleOpenTaskMake() {
                if (this.$route.query.type === 'detail') {
                    this.father_this.controlType = this.father_this.jobFlowFrom.run_type
                    this.setDrawer(2, true, '任务编排')
                } else {
                    if (this.father_this.$refs.baseInfo.form.type !== '') {
                        this.father_this.controlType = this.father_this.$refs.baseInfo.form.run_type
                        this.setDrawer(2, true, '任务编排')
                    } else {
                        this.$cwMessage('请先选择基本信息中的调度方式，才可进行任务编排', 'warning')
                    }
                }
            },
            // 处理复位
            handleReset() {
                this.graph.fitCenter()
            },
            get_nodeTime(information) {
                this.all_timenodes_lines = []
                this.timeResult = []
                const lines = information.lines // 拿到连线集
                const nodes = information.nodes // 拿到节点集
                const firstNode = nodes[0] // 拿到开始节点
                const lastNode = nodes[1] // 拿到结束节点
                this.tree_for(firstNode, lastNode, lines, nodes, [])
            },
            // 保存前连线初始化
            handleInitLines() {
                this.midLines = []
                this.midLines = this.graph.getEdges().map(e => {
                    const line = e.get('model')
                    return {
                        from: line.source,
                        to: line.target,
                        getWay: line.getWay
                    }
                })
            },
            // 保存节点前初始化
            handleInitNodes() {
                this.getWayOK.flag = true
                this.midNodes = []
                for (const e of this.graph.getNodes()) {
                    const node = e.get('model')
                    const item = {
                        show: true,
                        top: node.y,
                        left: node.x,
                        type: node.nodeType,
                        name: node.name,
                        node_data: node.node_data,
                        state: 'wait',
                        newState: '等待',
                        ico: node.icon,
                        content: node.content,
                        uuid: node.id
                    }
                    if (node.endUuid !== '') {
                        item.end_uuid = node.endUuid
                    }
                    // 获取节点出线，判断其是否为分支节点
                    const arr = e.getOutEdges().filter(line => {
                        return line.get('model').hasOwnProperty('label')
                    })
                    // arr不为空，表明为分支节点，分支节点的分支连线必须大于或等于2。若不满足，退出循环
                    if (arr.length !== 0 && arr.length < 2) {
                        this.getWayOK.flag = false
                        this.getWayOK.curGetWayNode = item
                        break
                    }
                    // 表明为分支节点，将其type改为4
                    if (arr.length >= 2) {
                        item.type = 4
                    }
                    this.midNodes.push(item)
                }
            },
            // 判断闭环前先删除作业流节点以及连线，因为作业流节点不需要参与闭环校验
            deleteFlowNode(paramData) {
                let linesLen = paramData.pipeline_tree.lines.length - 1
                let nodesLen = paramData.pipeline_tree.nodes.length - 1
                for (let i = nodesLen; i >= 0; i--) {
                    if (paramData.pipeline_tree.nodes[i].type === 3) {
                        const s = paramData.pipeline_tree.nodes.splice(i, 1)
                        nodesLen -= 1
                        for (let j = linesLen; j >= 0; j--) {
                            if (paramData.pipeline_tree.lines[j].from === s[0].uuid) {
                                paramData.pipeline_tree.lines.splice(j, 1)
                                linesLen -= 1
                            }
                        }
                    }
                }
                // 这里是为了防止删除作业流相关联的连线后，导致实际上有孤立的作业节点，可是因为没有连线所以不参与闭环判断。
                // 可以在这里提前做一次闭环判断
                const arr = []
                paramData.pipeline_tree.nodes.forEach(node => {
                    const currentNode = node
                    const flag = paramData.pipeline_tree.lines.some(line => {
                        return currentNode.uuid === line.from || currentNode.uuid === line.to
                    })
                    arr.push(flag)
                })
                if (arr.indexOf(false) >= 0) {
                    this.$cwMessage('连线未形成闭环，保存不通过！', 'warning')
                    return false
                }
                return true
            },
            // 参数分别为：当前连线，结束节点，连线集
            isClose(currentLine, lastNode, lines) {
                if (currentLine.to !== lastNode.uuid) { // 当前连线的下一节点不等于结束节点，表明此时连线未结束
                    const firstLines = lines.filter((item, index) => { // 拿到开始线集
                        return item.from === currentLine.to
                    })
                    if (firstLines.length === 0) { // 如果开始线集为空则表明该节点没有下一连线了，即未生成闭环
                        this.closeResult.push(false)
                        return false
                    } else { // 如果开始线集不为空则遍历递归调用继续往下判断
                        firstLines.forEach((item, index) => {
                            this.isClose(item, lastNode, lines)
                        })
                    }
                } else { // 表明此时已到结束节点
                    this.closeResult.push(true)
                    return true
                }
            },
            // 参数分别为：当前连线，开始节点，连线集
            isOpen(currentLine, firstNode, lines) {
                if (currentLine.from !== firstNode.uuid) { // 当前连线的下一节点不等于开始节点，表明此时连线未结束
                    const lastLines = lines.filter((item, index) => { // 拿到反向开始线集
                        return item.to === currentLine.from
                    })
                    if (lastLines.length === 0) { // 如果反向开始线集为空则表明该节点没有下一连线了，即未生成闭环
                        this.openResult.push(false)
                        return false
                    } else { // 如果反向开始线集不为空则遍历递归调用继续往下判断
                        lastLines.forEach((item, index) => {
                            this.isOpen(item, firstNode, lines)
                        })
                    }
                } else { // 表明此时已到开始节点
                    this.openResult.push(true)
                    return true
                }
            },
            // 正向闭环判断
            isPositiveClose(information) {
                this.closeResult = []
                const lines = information.lines // 拿到连线集
                const nodes = information.nodes // 拿到节点集
                const firstNode = nodes[0] // 拿到开始节点
                const lastNode = nodes[1] // 拿到结束节点
                const firstLines = lines.filter((item, index) => { // 拿到开始线集
                    return item.from === firstNode.uuid
                })
                firstLines.forEach((item, index) => { // 遍历开始线集判断闭环
                    this.isClose(item, lastNode, lines)
                })
            },
            // 反向闭环判断
            isReverseClose(information) {
                this.openResult = []
                const lines = information.lines // 拿到连线集
                const nodes = information.nodes // 拿到节点集
                const firstNode = nodes[0] // 拿到开始节点
                const lastNode = nodes[1] // 拿到结束节点
                const firstLines = lines.filter((item, index) => { // 拿到反向开始线集
                    return item.to === lastNode.uuid
                })
                firstLines.forEach((item, index) => { // 遍历反向开始线集判断闭环
                    this.isOpen(item, firstNode, lines)
                })
            },
            // 判断闭环
            checkClose() {
                const paramData = deepClone({
                    pipeline_tree: {
                        lines: this.midLines,
                        nodes: this.midNodes
                    }
                })
                // 删除作业流节点及连线，避免干扰
                const flag = this.deleteFlowNode(paramData)
                if (!flag) {
                    this.validatorFlag = false
                    return false
                }
                // 判断是否形成闭环,正向判断
                this.isPositiveClose(paramData.pipeline_tree)
                // 判断是否形成闭环,反向判断，这种情况校验是为了防止后期删除与开始节点的连线造成的
                this.isReverseClose(paramData.pipeline_tree)
                if (this.closeResult.indexOf(false) > -1 || this.openResult.indexOf(false) > -1) { // 只要结果数组中有一个false就表明未形成闭环
                    this.validatorFlag = false
                    this.$cwMessage('连线未形成闭环，保存不通过！', 'warning')
                } else {
                    this.validatorFlag = true
                }
            },
            // 校验孤立节点
            checkSingleNode() {
                const linesIds = []
                let flag = false
                if (this.graph.getEdges().length > 0) {
                    this.graph.getEdges().forEach(e => {
                        const line = e.get('model')
                        linesIds.push(line.source)
                        linesIds.push(line.target)
                    })
                    this.graph.getNodes().forEach(e => {
                        const node = e.get('model')
                        if (linesIds.indexOf(node.id) === -1) {
                            flag = true
                        }
                    })
                } else {
                    flag = true
                }
                if (flag) {
                    this.$cwMessage('有孤立节点，保存不通过！', 'warning')
                    this.validatorFlag = false
                }
            },
            // 处理保存
            handleSave() {
                // 详情状态下不做处理
                if (this.$route.query.type === 'detail') {
                    return false
                }
                this.validatorFlag = true
                // 校验孤立节点
                this.checkSingleNode()
                // 表明没有孤立节点, 开始闭环校验
                if (this.validatorFlag) {
                    // 上传前节点，连线数据初始化
                    this.handleInitNodes()
                    this.handleInitLines()
                    if (!this.getWayOK.flag) {
                        return this.$cwMessage(`校验不通过: ${this.getWayOK.curGetWayNode.name}节点的分支连线至少有两条, 请检查您的连线！`, 'warning')
                    }
                    // 检查闭环
                    this.checkClose()
                    // 表明已形成闭环，开始表单校验
                    if (this.validatorFlag) {
                        this.checkFrom()
                    }
                }
            },
            checkFrom() {
                this.father_this.$refs.baseInfo.$refs.form.validate().then(validator => {
                    this.validatorFlag = true
                    // let flag = false
                    // 表单校验通过，调度方式为日历的情况下，校验开始时间
                    if (this.controlType === 'calendar') {
                        const flag = this.midNodes.some(node => {
                            return node.node_data.eta < this.father_this.$refs.baseInfo.form.calendarTime &&
                                (node.name !== '开始' && node.name !== '结束') && node.node_data.eta
                        })
                        if (flag) {
                            this.$cwMessage('校验不通过: 节点开始时间不能小于日历开始时间, 请检查您的选择', 'warning')
                            this.validatorFlag = false
                        } else {
                            this.get_nodeTime(deepClone({
                                lines: this.midLines,
                                nodes: this.midNodes
                            }))
                            // 获取节点开始时间校验结果
                            this.timeisOk()
                            if (this.timeResult.length > 0) {
                                const msg = this.timeResult[0]
                                this.$cwMessage(
                                    `校验不通过: (${msg.node2.name})节点的开始时间必须比(${msg.node1.name})大,请检查您的选择`,
                                    'warning')
                                this.validatorFlag = false
                            } else {
                                this.validatorFlag = true
                            }
                        }
                    }
                    // 时间校验通过，保存数据
                    if (this.validatorFlag) {
                        const params = {
                            pipeline_tree: {
                                lines: [],
                                nodes: []
                            }
                        }
                        if (this.father_this.$refs.baseInfo.form.cross_day_dependence) {
                            params.cross_day_dependence = true // 跨日依赖
                        }
                        // todo 节点
                        params.pipeline_tree.lines = this.midLines
                        params.pipeline_tree.nodes = this.midNodes
                        params.name = this.father_this.$refs.baseInfo.form.jobFlowName // 作业流名称
                        params.type = this.father_this.$refs.baseInfo.form.type // 调度方式
                        params.description = this.father_this.$refs.baseInfo.form.jobFlowDescribe // 作业流描述
                        params.var_table = this.father_this.$refs.baseInfo.form.var_table // 变量表值
                        params.category = this.father_this.$refs.baseInfo.form.category // 跑批系统id
                        // 有前置文件路径
                        if (this.father_this.$refs.baseInfo.form.file_dependence.file_path !== '') {
                            if (!this.father_this.$refs.baseInfo.form.pre_category) {
                                return this.$cwMessage('有前置文件，前置跑批系统不能为空，请选择！', 'warning')
                            }
                            if (!this.father_this.$refs.baseInfo.form.pre_agent) {
                                return this.$cwMessage('有前置文件，前置Agent不能为空，请选择！', 'warning')
                            }
                            if (!this.father_this.$refs.baseInfo.form.file_dependence.max_num) {
                                return this.$cwMessage('有前置文件，巡检次数不能为空，请输入！', 'warning')
                            }
                            if (!this.father_this.$refs.baseInfo.form.file_dependence.cycle.value) {
                                return this.$cwMessage('有前置文件，巡检周期不能为空，请输入！', 'warning')
                            }
                            if (!this.father_this.$refs.baseInfo.form.file_dependence.cycle.type) {
                                return this.$cwMessage('有前置文件，巡检周期时间类型不能为空，请选择！', 'warning')
                            }
                            // 到了这里说明此时有前置路径，且前置跑批系统和前置Agent都不为空，且其余必填条件也满足
                            params.pre_category = this.father_this.$refs.baseInfo.form.pre_category // 作业流前置跑批id
                            params.pre_agent = this.father_this.$refs.baseInfo.form.pre_agent // 作业流前置agent
                            params.file_dependence = this.father_this.$refs.baseInfo.form.file_dependence // 前置文件参数
                        }
                        // 调度方式为无
                        if (params.type === 'null') {
                            params.trigger_data = {}
                        }
                        // 调度方式为定时
                        if (params.type === 'time') {
                            params.trigger_data = {
                                eta: this.father_this.$refs.baseInfo.form.fixedTime // 开始时间
                            }
                        }
                        // 调度方式为周期
                        if (params.type === 'cycle') {
                            params.trigger_data = {
                                eta: this.father_this.$refs.baseInfo.form.periodTime, // 开始时间
                                cycle: this.father_this.$refs.baseInfo.form.cycleDat, // 每隔XXX开始执行
                                unit: this.father_this.$refs.baseInfo.form.timeOption // 时间类型
                            }
                        }
                        // 调度方式为日历
                        if (params.type === 'calendar') {
                            params.trigger_data = {
                                eta: this.father_this.$refs.baseInfo.form.calendarTime, // 开始时间
                                calendar_id: this.father_this.$refs.baseInfo.form.calendarValue // 日历值
                            }
                        }
                        // console.log(params)
                        this.$emit('handleSave', params)
                    }
                }).catch(e => {
                    this.$cwMessage(e.content, 'warning')
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #header-panel {
        height: 56px;
        padding: 7px 32px 7px 32px;
        background-color: #fff;

        .left {
            float: left;
            display: flex;

            .box {
                cursor: pointer;
                width: 48px;
                text-align: center;
                position: relative;
                bottom: 6px;

                i {
                    font-size: 20px;
                }

                p {
                    margin-top: 2px;
                    height: 20px;
                    line-height: 20px;
                    font-size: 12px;
                }
            }
        }

        .right {
            float: right;
            display: flex;
            font-size: 20px;
            color: #979BA5;
            margin-top: 10px;

            i {
                cursor: pointer;
                margin-left: 16px;
            }
        }
    }
</style>
