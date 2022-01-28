<template>
    <div id="edgeInfo">
        <div class="content">
            <div class="box">
                <p class="title">基本信息</p>
                <div class="info">
                    <bk-form ref="form" :label-width="90" :rules="rules" :model="form">
                        <bk-form-item label="分支名称:" :error-display-type="'normal'" :required="true" :property="'name'">
                            <bk-input v-model="form.name" :disabled="disabled"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="表达式:" :error-display-type="'normal'" :required="true" :property="'expression'">
                            <bk-input :type="'textarea'" :rows="20" ext-cls="custom-textarea" v-model="form.expression" :disabled="disabled"></bk-input>
                        </bk-form-item>
                    </bk-form>
                </div>
            </div>
        </div>
        <div class="footer" v-if="!disabled">
            <bk-button theme="primary" @click="handleConfim" style="margin-right: 8px;">确定</bk-button>
            <bk-button @click="handleCancel">取消</bk-button>
        </div>
    </div>
</template>

<script>
    export default {
        // props: ['edgeData'],
        props: {
            edgeData: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                disabled: false,
                form: {
                    name: '',
                    expression: ''
                },
                rules: {
                    name: [{
                        required: true,
                        message: '分支名称不能为空',
                        trigger: 'blur'
                    }],
                    expression: [{
                        required: true,
                        message: '表达式不能为空',
                        trigger: 'blur'
                    }]
                }
            }
        },
        created() {
            this.form = this.edgeData.data
            if (this.$route.query.type === 'detail') {
                this.disabled = true
            }
        },
        methods: {
            handleConfim() {
                this.$bkInfo({
                    type: 'primary',
                    title: '确认要保存吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.$refs.form.validate().then(validator => {
                            this.$emit('update-edge-data', this.form, this.edgeData.id)
                            this.$cwMessage('保存成功！', 'success')
                            this.$emit('edge-drawer-close')
                        }).catch(e => {
                            this.$cwMessage('您的输入有误，请检查输入！', 'warning')
                        })
                    },
                    cancelFn: async() => {
                        this.$emit('edge-drawer-close')
                    }
                })
            },
            handleCancel() {
                this.$emit('edge-drawer-close')
            }
        }
    }
</script>

<style lang="scss" scoped>
    #edgeInfo {
        height: 100%;

        .content {
            padding: 16px 20px 0 16px;
            height: calc(100% - 54px);
            overflow: auto;

            .box {
                margin-bottom: 14px;

                .title {
                    font-size: 14px;
                    height: 22px;
                    line-height: 22px;
                    color: #313238;
                    font-weight: bold;
                    margin-bottom: 16px;
                }

                .info {
                    .custom-textarea {
                        /deep/ textarea {
                            padding: 20px;
                            background-color: rgb(49, 50, 56) !important;
                            color: #C4C6CC !important;
                        }
                    }

                    .pre-commands {
                        display: flex;

                        i {
                            font-size: 32px;
                            color: #979BA5;
                            width: 32px;
                            text-align: center;
                            height: 32px;
                            line-height: 32px;
                            cursor: pointer;
                        }
                    }
                }
            }
        }

        .footer {
            border-top: 1px solid #DCDEE5;
            height: 54px;
            line-height: 54px;
            background: #FAFBFD;
            padding-left: 16px;
            font-size: 0;
        }
    }
</style>
