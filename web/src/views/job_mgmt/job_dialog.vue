<template>
    <div id="jobDialog">
        <div class="form">
            <div class="form-item">
                <span>作业名</span>
                <p>{{form.name}}</p>
            </div>
            <div class="form-item">
                <span>所属作业流</span>
                <p :title="form.process">{{checkFormValue(form.process)}}</p>
            </div>
            <div class="form-item">
                <span>Agent</span>
                <p>{{form.station}}</p>
            </div>
            <div class="form-item">
                <span>IP</span>
                <p>{{form.ip}}</p>
            </div>
            <div class="form-item">
                <span>操作系统</span>
                <p>{{form.os}}</p>
            </div>
            <div class="form-item">
                <span>作业描述</span>
                <p :title="form.description">{{checkFormValue(form.description)}}</p>
            </div>
            <div class="form-item">
                <span>执行账号</span>
                <p>{{form.account}}</p>
            </div>
            <div class="form-item">
                <span>脚本类型</span>
                <p>{{scriptTypeList.find(item => item.key === form.script_type).label}}</p>
            </div>
            <template v-if="form.script_type === 6">
                <div class="form-item">
                    <span>请求方式</span>
                    <p>{{checkFormValue(form.request_type)}}</p>
                </div>
                <div class="form-item">
                    <span>URL</span>
                    <p>{{checkFormValue(form.request_url)}}</p>
                </div>
                <div class="form-item">
                    <span>请求头</span>
                    <p>{{checkFormValue(form.headers)}}</p>
                </div>
                <div class="form-item">
                    <span>请求体</span>
                    <p :title="form.params">{{JSON.parse(JSON.stringify(checkFormValue(form.params)))}}</p>
                </div>
            </template>
            <div class="form-item" v-if="form.script_type !== 6">
                <span>脚本内容</span>
                <p :title="form.script_content">{{form.script_content}}</p>
            </div>
            <div class="form-item">
                <span>超时时间</span>
                <p>{{checkFormValue(form.script_timeout)}}</p>
            </div>
            <div class="form-item">
                <span>退出码</span>
                <p>{{checkFormValue(form.exit_code)}}</p>
            </div>
            <div class="form-item">
                <span>上一次执行时间</span>
                <p>{{checkFormValue(form.last_run_at)}}</p>
            </div>
            <div class="form-item">
                <span>执行次数</span>
                <p>{{checkFormValue(form.total_run_count)}}</p>
            </div>
            <div class="form-item">
                <span>创建人</span>
                <p>{{form.creator}}</p>
            </div>
            <div class="form-item">
                <span>创建时间</span>
                <p>{{form.create_time}}</p>
            </div>
            <div class="form-item">
                <span>修改人</span>
                <p>{{checkFormValue(form.editor)}}</p>
            </div>
            <div class="form-item">
                <span>上一次修改时间</span>
                <p>{{checkFormValue(form.edit_time)}}</p>
            </div>
        </div>
        <!--        <bk-form ref="form">
            <bk-form-item label="作业名:">
                <bk-input v-model="form.name" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="所属作业流:">
                <bk-input v-model="form.process" :disabled="true" :title="form.process"></bk-input>
            </bk-form-item>
            <bk-form-item label="Agent:">
                <bk-input v-model="form.station" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="IP:">
                <bk-input v-model="form.ip" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="系统:">
                <bk-input v-model="form.os" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="作业描述:">
                <bk-input v-model="form.description" :disabled="true" :title="form.description"></bk-input>
            </bk-form-item>
            <bk-form-item label="执行账号:">
                <bk-input v-model="form.account" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="脚本类型:">
                <bk-select v-model="form.script_type"
                    placeholder="请选择" :disabled="true">
                    <bk-option v-for="(item, index) in scriptTypeList" :key="index" :id="item.key"
                        :name="item.label">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <template v-if="form.script_type === 6">
                <bk-form-item label="请求方式">
                    <bk-input :disabled="true" v-model="form.request_type"></bk-input>
                </bk-form-item>
                <bk-form-item label="URL">
                    <bk-input :disabled="true" v-model="form.request_url"></bk-input>
                </bk-form-item>
                <bk-form-item label="请求头">
                    <bk-input :disabled="true" v-model="form.headers" :title="form.headers"></bk-input>
                </bk-form-item>
                <bk-form-item label="请求体">
                    <bk-input :disabled="true" v-model="form.params" :type="'textarea'" :rows="4" :title="form.params"></bk-input>
                </bk-form-item>
            </template>
            <bk-form-item label="脚本内容:" v-if="form.script_type !== 6">
                <bk-input v-model="form.script_content" :disabled="true" :title="form.script_content"></bk-input>
            </bk-form-item>
            <bk-form-item label="超时时间:">
                <bk-input v-model="form.script_timeout" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="退出码:">
                <bk-input v-model="form.exit_code" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="上一次执行时间:">
                <bk-input v-model="form.last_run_at" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="执行次数:">
                <bk-input v-model="form.total_run_count" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="创建人:">
                <bk-input v-model="form.creator" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="创建时间:">
                <bk-input v-model="form.create_time" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="修改人:">
                <bk-input v-model="form.editor" :disabled="true"></bk-input>
            </bk-form-item>
            <bk-form-item label="上一次修改时间:">
                <bk-input v-model="form.edit_time" :disabled="true"></bk-input>
            </bk-form-item>
        </bk-form> -->
    </div>
</template>

<script>
    export default {
        // props: ['jobFrom'],
        props: {
            jobFrom: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                formLoading: false,
                form: {},
                scriptTypeList: [{
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
                ] // 脚本类型下拉列表
            }
        },
        created() {
            this.form = this.jobFrom
            // console.log(this.form)
        },
        methods: {
            checkFormValue(val) {
                let str = val
                if (val === undefined || val === '' || val === null) {
                    str = '--'
                }
                return str
            }
        }
    }
</script>

<style lang="scss" scoped>
    #jobDialog {
        // height: 700px;
        // padding-right: 20px;
        padding: 20px;
        overflow: scroll;

        .form {
            .form-item {
                display: flex;
                align-items: center;
                margin-bottom: 24px;

                span {
                    flex-basis: 180px;
                    color: rgb(150,155,165);
                }
                p {
                    width: 280px;
                    color: rgb(90,92,101);
                    white-space:nowrap;
                    overflow:hidden;
                    text-overflow:ellipsis;
                }
                &:last-of-type {
                    margin-bottom: 0;
                }
            }
        }
    }
</style>
