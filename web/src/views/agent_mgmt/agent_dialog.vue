<template>
    <div id="agentDialog" v-bkloading="{ isLoading: formLoading, zIndex: 10 }">
        <bk-form ref="form" :label-width="120" :rules="rules" :model="form">
            <bk-form-item label="Agent" :error-display-type="'normal'" :required="true" :property="'name'">
                <bk-input placeholder="Agent" v-model="form.name"></bk-input>
            </bk-form-item>
            <bk-form-item label="业务" :error-display-type="'normal'" :required="true" :property="'biz_id'">
                <bk-select class="header-select" :clearable="false" style="background-color: #fff;" v-model="form.biz_id"
                    placeholder="请选择" @change="handleBizChange">
                    <bk-option v-for="(item, index) in bizList" :key="index" :id="item.bk_biz_id" :name="item.bk_biz_name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="IP" :error-display-type="'normal'" :required="true" :property="'ip'">
                <bk-select class="header-select" :clearable="false" style="background-color: #fff;" v-model="form.ip"
                    placeholder="请选择" @change="handleHostChange">
                    <bk-option v-for="(item, index) in hostList" :key="index" :id="item.bk_host_innerip" :name="item.bk_host_innerip"
                        v-if="hostShow">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="跑批系统" :error-display-type="'normal'" :required="true" :property="'category'">
                <bk-select class="header-select" :clearable="false" style="background-color: #fff;" v-model="form.category"
                    placeholder="请选择">
                    <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id" :name="item.name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="作业并发限制" :error-display-type="'normal'" :required="true" :property="'max_concurrency'">
                <bk-input placeholder="作业并发限制" v-model="form.max_concurrency" type="number" :min="0"></bk-input>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    import {
        deepClone
    } from '../../common/util.js'
    export default {
        // props: ['operationFlag', 'agentFrom'],
        props: {
            operationFlag: {
                type: String,
                default: ''
            },
            agentFrom: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                hostShow: false,
                form: {
                    name: '', // agent名称
                    biz_id: '', // 业务id
                    ip: '',
                    category: '', // 跑批系统
                    max_concurrency: 10 // 作业并发限制
                },
                formLoading: false,
                bizList: [], // 业务下拉
                runSysList: [], // 跑批系统下拉
                hostList: [],
                rules: {
                    name: [{
                        required: true,
                        message: 'Agent不能为空',
                        trigger: 'blur'
                    }],
                    biz_id: [{
                        required: true,
                        message: '业务不能为空',
                        trigger: 'change'
                    }],
                    ip: [{
                        required: true,
                        message: 'ip不能为空',
                        trigger: 'change'
                    }],
                    category: [{
                        required: true,
                        message: '跑批系统不能为空',
                        trigger: 'change'
                    }],
                    max_concurrency: [{
                        required: true,
                        message: '作业开发限制不能为空',
                        trigger: 'blur'
                    }]
                }
            }
        },
        created() {
            if (this.operationFlag === '修改Agent') {
                this.initHostList()
            }
            this.initBizList()
            this.initRunSysList()
        },
        methods: {
            handleHostChange(e) {
                this.hostList.forEach(item => {
                    if (item.bk_host_innerip === e) {
                        if (item.bk_cloud_id === '') {
                            this.form.ip = ''
                            this.$cwMessage('该主机下没有云区域ID，请换台主机！', 'warning')
                        }
                    }
                })
            },
            handleAddAgent(nowHostData) {
                this.formLoading = true
                this.$parent.$parent.closeIconShow = false
                const data = {
                    ...this.form,
                    biz_name: nowHostData.bk_biz_name,
                    os: nowHostData.bk_os_name,
                    cloud: nowHostData.bk_cloud_id,
                    data: nowHostData
                }
                this.$api.station.create(data).then(res => {
                    if (res.result) {
                        this.$cwMessage('添加成功！', 'success')
                        this.$emit('close-dialog', true)
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.$parent.$parent.closeIconShow = true
                    this.$parent.$parent.dialogLoading = false
                    this.formLoading = false
                })
            },
            handleUpdateAgent(nowHostData) {
                this.formLoading = true
                this.$parent.$parent.closeIconShow = false
                const data = {
                    name: this.form.name,
                    biz_id: this.form.biz_id,
                    ip: this.form.ip,
                    category: this.form.category,
                    max_concurrency: this.form.max_concurrency,
                    biz_name: nowHostData.bk_biz_name,
                    os: nowHostData.bk_os_name,
                    cloud: nowHostData.bk_cloud_id,
                    data: nowHostData
                }
                this.$api.station.update(this.form.id, data).then(res => {
                    if (res.result) {
                        this.$cwMessage('修改成功！', 'success')
                        this.$emit('close-dialog', true)
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.$parent.$parent.closeIconShow = true
                    this.$parent.$parent.dialogLoading = false
                    this.formLoading = false
                })
            },
            // 处理业务变化
            handleBizChange(e) {
                this.hostShow = false
                this.form.ip = ''
                this.$api.station.search_host({
                    biz_id: e
                }).then(res => {
                    if (res.result) {
                        this.hostList = res.data
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.hostShow = true
                })
            },
            // 初始化下拉biz列表
            initBizList() {
                this.formLoading = true
                this.$api.station.get_biz().then(res => {
                    if (res.result) {
                        this.bizList = res.data.info
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.formLoading = false
                })
            },
            // 初始化下拉跑批系统列表
            initRunSysList() {
                this.runSysList = []
            },
            // 初始化下拉ip列表
            initHostList() {
                this.form = deepClone(this.agentFrom)
                this.formLoading = true
                this.hostShow = false
                this.$api.station.search_host({
                    biz_id: this.form.biz_id
                }).then(res => {
                    if (res.result) {
                        this.hostList = res.data
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.formLoading = false
                    this.hostShow = true
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #agentDialog {}
</style>
