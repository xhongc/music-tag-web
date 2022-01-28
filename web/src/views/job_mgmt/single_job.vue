<template>
    <div id="singleJob" v-bkloading="{ isLoading: formLoading, zIndex: 10 }">
        <div class="content">
            <bk-container :margin="0">
                <bk-form ref="form" :label-width="120" :rules="rules" :model="form">
                    <bk-form-item label="作业名称:" :error-display-type="'normal'" :required="true" :property="'name'">
                        <bk-input placeholder="作业名称" v-model="form.name" clearable></bk-input>
                    </bk-form-item>
                    <bk-form-item label="作业描述:" :error-display-type="'normal'" :required="true"
                        :property="'description'">
                        <bk-input placeholder="作业描述" v-model="form.description" clearable></bk-input>
                    </bk-form-item>
                    <bk-form-item label="选择跑批系统:" :error-display-type="'normal'" :required="true"
                        :property="'category'">
                        <bk-select :clearable="false" style="background-color: #fff;" v-model="form.category"
                            placeholder="请选择" @change="handleRunIdChange">
                            <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id" :name="item.name">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item label="选择Agent:" :error-display-type="'normal'" :required="true"
                        :property="'station'">
                        <bk-select :clearable="false" style="background-color: #fff;" v-model="form.station"
                            placeholder="请选择" @change="handleAgentIdChange">
                            <bk-option v-for="(item, index) in agentList" :key="index" :id="item.id" :name="item.name"
                                v-if="agnetListShow">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item label="系统类型:">
                        <span v-show="form.os">{{form.os}}</span>
                    </bk-form-item>
                    <bk-form-item label="执行账号:" :error-display-type="'normal'" :required="true"
                        :property="'data.account'">
                        <bk-select :clearable="false" style="background-color: #fff;" v-model="form.data.account"
                            placeholder="请选择">
                            <bk-option v-for="(item, index) in accountList" :key="index" :id="item.account"
                                :name="item.account" v-if="accountListShow">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item label="脚本类型:" :error-display-type="'normal'" :required="true"
                        :property="'data.script_type'">
                        <bk-select :clearable="false" style="background-color: #fff;" v-model="form.data.script_type"
                            placeholder="请选择" @change="handleScriptTypeChange">
                            <bk-option v-for="(item, index) in scriptTypeList" :key="index" :id="item.key"
                                :name="item.label">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <!-- HTTP作业 -->
                    <template v-if="form.data.script_type === 6">
                        <bk-form-item label="请求方式:" :error-display-type="'normal'" :required="true"
                            :property="'data.request_type'">
                            <bk-select :clearable="false" style="background-color: #fff;" placeholder="请选择"
                                v-model="form.data.request_type">
                                <bk-option v-for="(item, index) in httpReqTypeList" :key="index" :id="item.key"
                                    :name="item.label">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item label="URL:" :error-display-type="'normal'" :required="true"
                            :property="'data.request_url'">
                            <bk-input placeholder="URL" v-model="form.data.request_url"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="请求头:" :property="'data.headers'" :error-display-type="'normal'">
                            <bk-input :placeholder="headerHolder" v-model="form.data.headers"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="请求体:" :property="'data.params'" :error-display-type="'normal'">
                            <bk-input :placeholder="paramsHolder" v-model="form.data.params" :type="'textarea'" :rows="4">
                            </bk-input>
                        </bk-form-item>
                    </template>
                    <!-- java作业 -->
                    <template v-if="form.data.script_type === 7">
                        <bk-form-item label="jar包路径:" :error-display-type="'normal'" :required="true">
                            <bk-input placeholder="jar包路径"></bk-input>
                        </bk-form-item>
                    </template>
                    <!-- sql作业 -->
                    <template v-if="form.data.script_type === 8">
                        <bk-form-item label="数据库类型:" :error-display-type="'normal'" :required="true">
                            <bk-select :clearable="false" style="background-color: #fff;" placeholder="请选择">
                                <bk-option v-for="(item, index) in sqlTypeList" :key="index" :id="item.key"
                                    :name="item.label">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item label="数据库:" :error-display-type="'normal'" :required="true">
                            <bk-input placeholder="数据库"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="主机:">
                            <bk-input placeholder="主机" style="width: 360px;"></bk-input>
                            <span style="margin: 0 12px 0 16px;">端口号:</span>
                            <bk-input placeholder="端口号" style="width: 122px;"></bk-input>
                        </bk-form-item>
                        <bk-row style="margin-top: 20px;margin-bottom: 20px;">
                            <bk-col :span="12">
                                <bk-form-item label="数据库用户:" :error-display-type="'normal'" :required="true">
                                    <bk-input placeholder="数据库用户" style="width: 290px;"></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="11" style="margin-left: 16px;">
                                <bk-form-item label="密码:" :error-display-type="'normal'" :required="true">
                                    <bk-input placeholder="密码" :type="'password'" style="width: 194px;"></bk-input>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                    </template>
                    <bk-form-item label="脚本内容:" :error-display-type="'normal'" :required="true"
                        :property="'data.script_content'"
                        v-show="!(form.data.script_type === 6) && !(form.data.script_type === 7)">
                        <!-- <bk-input :type="'textarea'" style="width: 720px;" :rows="10" ext-cls="custom-textarea" v-model="form.data.script_content"></bk-input> -->
                        <editor :width="'720px'" :height="'300px'" ref="editor" :codes="form.data.script_content">
                        </editor>
                    </bk-form-item>
                    <bk-form-item label="作业退出码:">
                        <bk-input placeholder="作业退出码" v-model="form.exit_code"></bk-input>
                    </bk-form-item>
                    <bk-form-item label="超时时间(s):" :error-display-type="'normal'" :required="true"
                        :property="'data.script_timeout'">
                        <bk-input placeholder="超时时间" type="number" v-model="form.data.script_timeout"></bk-input>
                    </bk-form-item>
                    <bk-form-item style="font-size: 0px;" v-if="!overScreenFlag">
                        <bk-button theme="primary" style="margin-right: 8px;" @click="handleConfim">确定</bk-button>
                        <bk-button @click="handleCancel">取消</bk-button>
                    </bk-form-item>
                </bk-form>
            </bk-container>
        </div>
        <template v-if="overScreenFlag">
            <div style="height: 72px;"></div>
            <div class="footer">
                <bk-button theme="primary" style="margin: 0 10px 0 140px;" @click="handleConfim">确定</bk-button>
                <bk-button @click="handleCancel">取消</bk-button>
            </div>
        </template>
    </div>
</template>

<script>
    import editor from '@/components/monacoEditor'
    import {
        deepClone, isJson
    } from '../../common/util.js'
    import { validateURL } from '../../common/validate.js'
    export default {
        components: {
            editor
        },
        data() {
            return {
                headerHolder: '请输入请求头, 例如： {"Content-type": "application/json"}',
                paramsHolder: '请输入填写请求体, 例如： {"name": "abc"}',
                checkFlag: true,
                overScreenFlag: false, // 是否超出一屏标志位
                pageKey: 0,
                agnetListShow: true,
                accountListShow: true,
                formLoading: false,
                scriptMap: {
                    1: 'shell',
                    2: 'bat',
                    3: 'perl',
                    4: 'python',
                    5: 'powershell',
                    8: 'sql'
                },
                sqlTypeList: [{
                    key: 'MySQL',
                    label: 'MySQL'
                }, {
                    key: 'Oracle',
                    label: 'Oracle'
                }],
                httpReqTypeList: [{
                    key: 'get',
                    label: 'GET'
                }, {
                    key: 'post',
                    label: 'POST'
                }, {
                    key: 'put',
                    label: 'PUT'
                }, {
                    key: 'delete',
                    label: 'DELETE'
                }], // HTTP请求方式
                scriptTypeList: [
                    {
                        key: 1,
                        label: 'Shell(Linux)',
                        value: 'shell-linux-1'
                    },
                    {
                        key: 2,
                        label: 'Bat(Windows)',
                        value: 'bat-win-2'
                    },
                    {
                        key: 3,
                        label: 'perl',
                        value: 'perl-3'
                    },
                    {
                        key: 4,
                        label: 'Python(Linux)',
                        value: 'python-linux-4'
                    },
                    {
                        key: 5,
                        label: 'PowerShell(Windows)',
                        value: 'powershell-win-5'
                    },
                    {
                        key: 6,
                        label: 'HTTP',
                        value: 'HTTP'
                    }
                    // {
                    //     key: 7,
                    //     label: 'Java',
                    //     value: 'Java'
                    // },
                    // {
                    //     key: 8,
                    //     label: 'SQL',
                    //     value: 'SQL'
                    // }
                ], // 脚本类型下拉列表
                accountList: [], // 执行账号下拉列表
                runSysList: [], // 跑批系统下拉列表
                agentList: [], // agent下拉列表
                form: {
                    name: '', // 作业名称
                    description: '', // 作业描述
                    category: '', // 跑批系统
                    station: '', // agnet
                    os: '', // 系统类型
                    exit_code: '', // 作业退出码
                    data: {
                        account: '', // 执行账号
                        script_type: 1, // 脚本类型
                        script_content: '', // 脚本内容
                        script_timeout: 8600, // 超时时间
                        request_type: '', // http请求，请求方式
                        request_url: '', // http请求，请求url
                        headers: '', // http请求，请求头
                        params: '' // http请求，请求体
                    }
                },
                otherRules: {
                    'data.script_content': [{
                        required: true,
                        message: '脚本内容不能为空',
                        trigger: 'blur'
                    }]
                },
                baseRules: {
                    name: [{
                        required: true,
                        message: '作业名称不能为空',
                        trigger: 'blur'
                    }],
                    description: [{
                        required: true,
                        message: '作业描述不能为空',
                        trigger: 'blur'
                    }],
                    category: [{
                        required: true,
                        message: '跑批系统不能为空',
                        trigger: 'change'
                    }],
                    station: [{
                        required: true,
                        message: 'agent不能为空',
                        trigger: 'change'
                    }],
                    'data.account': [{
                        required: true,
                        message: '执行账号不能为空',
                        trigger: 'change'
                    }],
                    'data.script_type': [{
                        required: true,
                        message: '脚本类型不能为空',
                        trigger: 'change'
                    }],
                    'data.script_timeout': [{
                        required: true,
                        message: '超时时间不能为空',
                        trigger: 'blur'
                    }]
                }
            }
        },
        computed: {
            rules() {
                const rules = {}
                Object.assign(rules, this.baseRules, this.otherRules)
                return rules
            }
        },
        watch: {
            'form.data.script_type': function(val) {
                if (val === 1 || val === 2 || val === 3 || val === 4 || val === 5) {
                    this.otherRules = {
                        'data.script_content': [{
                            required: true,
                            message: '脚本内容不能为空',
                            trigger: 'blur'
                        }]
                    }
                } else if (val === 6) {
                    this.otherRules = {
                        'data.request_type': [{
                            required: true,
                            message: '请求方式不能为空',
                            trigger: 'blur'
                        }],
                        'data.request_url': [{
                            required: true,
                            message: 'URL不能为空',
                            trigger: 'blur'
                        }, {
                            required: true,
                            trigger: 'change',
                            message: '请输入合法的url',
                            validator: (e) => {
                                if (!validateURL(e)) {
                                    return false
                                }
                                return true
                            }
                        }],
                        'data.params': [{
                            required: false,
                            trigger: 'blur',
                            message: '请输入合法的请求体格式，必须为json',
                            validator: (e) => {
                                if (e !== '') {
                                    return isJson(e)
                                }
                                return true
                            }
                        }],
                        'data.headers': [{
                            required: false,
                            trigger: 'blur',
                            message: '请输入合法的请求头格式，必须为json',
                            validator: (e) => {
                                if (e !== '') {
                                    return isJson(e)
                                }
                                return true
                            }
                        }]
                    }
                } else if (val === 7) {
                    console.log('修改java作业校验规则')
                } else if (val === 8) {
                    console.log('修改sql作业校验规则')
                }
            }
        },
        created() {
            // 获取跑批系统
            this.getRunSysList()
            if (this.$route.query.type === 'update' || this.$route.query.type === 'clone') {
                this.initJobData()
            } else {
                this.pageKey += 1
            }
        },
        mounted() {
            const _this = this
            const elementResizeDetectorMaker = require('element-resize-detector') // 导入element-resize-detector
            // 创建实例
            const erd = elementResizeDetectorMaker()
            // 监听id为singleJob的元素 大小变化
            this.$nextTick(() => {
                erd.listenTo(document.getElementById('singleJob'), function(element) {
                    if ((element.offsetHeight - (document.documentElement.clientHeight - 52)) > 0) {
                        _this.overScreenFlag = true
                    } else {
                        _this.overScreenFlag = false
                    }
                })
            })
        },
        beforeRouteLeave(to, from, next) {
            if (this.checkFlag) {
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
            // 处理切换脚本类型
            handleScriptTypeChange(e) {
                // this.overScreen()
                if (e === 6) {
                    return false
                }
                this.$refs.editor.changeModel(this.scriptMap[e])
            },
            // 处理跑批系统选择
            handleRunIdChange(e) {
                // 由于修改作业时，作业初始化导致触发该方法清除正常的数据，因此这里要做判断。
                // pageKey为初始化的标志，初始化结束后大于0
                if ((this.$route.query.type === 'update' || this.$route.query.type === 'clone') && this.pageKey === 0) {
                    this.getAgentList(e)
                    return
                }
                this.form.station = ''
                this.form.os = ''
                this.form.data.account = ''
                this.getAgentList(e)
            },
            // 处理agent选择
            handleAgentIdChange() {
                // 由于修改作业时，作业初始化导致触发该方法清除正常的数据，因此这里要做判断。
                // pageKey为初始化的标志，初始化结束后大于0
                if (this.pageKey !== 0) {
                    this.form.os = ''
                    this.form.data.account = ''
                    let bkBizId = ''
                    for (const item of this.agentList) {
                        if (item.id === this.form.station) {
                            bkBizId = item.biz_id
                            this.form.os = item.os
                        }
                    }
                    if (bkBizId !== '') {
                        this.getAccountList(bkBizId)
                    }
                }
            },
            // 处理新建作业
            handleAddJob() {
                this.formLoading = true
                const params = deepClone(this.form)
                this.deleteProp(params)
                // if (params.data.params) {
                //     params.data.params = JSON.stringify(JSON.parse(params.data.params), null, 2)
                // }
                // this.form.data.params = params.data.params
                // console.log(params)
                this.$api.content.create(params).then(res => {
                    if (res.result) {
                        this.checkFlag = false
                        this.$cwMessage('创建成功！', 'success')
                        this.$router.push({
                            path: '/joblist'
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.formLoading = false
                })
            },
            // 处理修改作业
            handleUpdateJob() {
                this.formLoading = true
                const id = parseInt(this.$route.query.job_id)
                const params = deepClone(this.form)
                this.deleteProp(params)
                this.$api.content.update(id, params).then(res => {
                    if (res.result) {
                        this.checkFlag = false
                        this.$cwMessage('更新成功！', 'success')
                        this.$router.push({
                            path: '/joblist'
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.formLoading = false
                })
            },
            // 非http类型的作业，以下属性不传
            deleteProp(params) {
                if (this.form.data.script_type !== 6) {
                    delete params.data.request_type
                    delete params.data.request_url
                    delete params.data.headers
                    delete params.data.params
                }
            },
            // 处理克隆作业
            handleCloneJob() {
                this.formLoading = true
                const params = deepClone(this.form)
                this.deleteProp(params)
                this.$api.content.clone(params).then(res => {
                    if (res.result) {
                        this.$cwMessage('克隆成功！', 'success')
                        this.$router.push({
                            path: '/joblist'
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.formLoading = false
                })
            },
            // 处理确定
            handleConfim() {
                if (this.form.data.script_type !== 6) {
                    // 只有非http类型的节点才获取脚本内容
                    this.form.data.script_content = this.$refs.editor.monacoEditor.getValue()
                } else {
                    this.form.data.script_content = '' // 加个else清空脚本内容是为了防止原本非http类型的节点切换为http保存之后，原来的脚本内容还在。
                }
                this.$refs.form.validate().then(validator => {
                    if (this.$route.query.type === 'add') {
                        this.handleAddJob()
                    } else if (this.$route.query.type === 'update') {
                        this.handleUpdateJob()
                    } else if (this.$route.query.type === 'clone') {
                        this.handleCloneJob()
                    }
                }).catch(e => {
                    // this.$cwMessage('输入有误，请检查您的输入！', 'warning')
                    // this.overScreen()
                })
            },
            // 处理取消
            handleCancel() {
                this.$router.go(-1)
            },
            // 获取执行账号下拉列表
            getAccountList(bkBizId) {
                this.accountListShow = false
                this.$api.station.get_os_account({
                    bk_biz_id: bkBizId
                }).then(res => {
                    if (res.result) {
                        this.accountList = res.data
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.accountListShow = true
                })
            },
            // 获取agent下拉列表
            getAgentList(e) {
                this.agnetListShow = false
                this.accountListShow = false
                this.$api.station.list({
                    category: e
                }).then(res => {
                    if (res.result) {
                        this.agentList = res.data.items
                        // 由于修改作业时，作业初始化时执行账号的获取需要等待agent列表获取之后才能查找biz_id
                        // pageKey为初始化的标志，初始化结束后大于0
                        if ((this.$route.query.type === 'update' || this.$route.query.type === 'clone') && this.pageKey === 0) {
                            this.pageKey += 1
                            let bkBizId = ''
                            for (const item of this.agentList) {
                                if (item.id === this.form.station) {
                                    bkBizId = item.biz_id
                                    this.form.os = item.os
                                }
                            }
                            if (bkBizId !== '') {
                                this.getAccountList(bkBizId)
                            }
                        }
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.agnetListShow = true
                    this.accountListShow = true
                })
            },
            // 获取跑批系统
            getRunSysList() {
                this.formLoading = true
                this.runSysList = []
            },
            // 设置默认编辑器
            setDefaultEditor(e, str) {
                this.$refs.editor.changeModel(this.scriptMap[e], str)
            },
            // 当前为修改，初始化作业
            initJobData() {
                this.formLoading = true
                const id = parseInt(this.$route.query.job_id)
                this.$api.content.retrieve(id).then(res => {
                    if (res.result) {
                        this.form = res.data
                        // 非http类型的节点是没有http节点属性的，上面的赋值会将其覆盖。这里将其重新获取。
                        if (this.form.data.script_type !== 6) {
                            this.$set(this.form.data, 'request_type', '')
                            this.$set(this.form.data, 'request_url', '')
                            this.$set(this.form.data, 'headers', '')
                            this.$set(this.form.data, 'params', '')
                        }
                        this.setDefaultEditor(this.form.data.script_type, this.form.data.script_content)
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
    #singleJob {
        padding-top: 20px;
        // height: 100%;
        // overflow: auto;
        position: relative;

        .content {
            height: 100%;
            width: 700px;
            padding-left: 20px;

            .custom-textarea {
                /deep/ textarea {
                    padding: 20px;
                    background-color: rgb(49, 50, 56) !important;
                    color: #C4C6CC !important;
                }
            }

            .os-button {
                display: inline-block;
                padding: 0 5px 0 5px;
                height: 32px;
                line-height: 32px;
                background-color: #fff;
                font-size: 12px;
                color: #63656E;
                border: 1px solid #C4C6CC;
            }
        }

        .footer {
            position: fixed;
            width: 100%;
            bottom: 0px;
            height: 52px;
            line-height: 52px;
            background: #FFFFFF;
            box-shadow: 0px -2px 6px 0px rgba(0, 0, 0, 0.1);
            font-size: 0;
            z-index: 999;
        }
    }
</style>
