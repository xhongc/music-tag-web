<template>
    <div id="sysSetup" v-bkloading="{ isLoading: loading, zIndex: 10 }">
        <div class="card card-log">
            <p class="title">Logo设置</p>
            <div class="content">
                <div class="img">
                    <img :src="imgSrc">
                </div>
                <input id="uploadFile" style="display: none" @change="uploadFile()" type="file" />
                <bk-button theme="primary" style="margin-right: 8px;" @click="uploadLogo()">选择图片</bk-button>
                <bk-button style="margin-right: 20px;" @click="init_logo()">恢复默认</bk-button>
                <div class="info">
                    <bk-icon style="color: #3A84FF;margin-right: 2px;" type="info-circle-shape" />
                    <span style="color: #979BA5;">仅支持上传 png、jpg、jpeg 格式的图片，建议上传图片宽高比1:1。</span>
                </div>
            </div>
        </div>
        <div class="card card-sys">
            <p class="title">系统设置</p>
            <div class="content">
                <bk-form>
                    <bk-form-item :label="item.description" v-for="(item, index) in sysForm" :key="index" v-if="item.key !== 'system_logo'">
                        <bk-input v-model="edit_sysForm[index].value" @input="verifyData(item)" :disabled="!isEdit"></bk-input>
                    </bk-form-item>
                    <bk-form-item v-if="!isEdit">
                        <bk-button theme="primary" @click="isEdit = true">修改</bk-button>
                    </bk-form-item>
                    <bk-form-item v-if="isEdit" style="font-size: 0;">
                        <bk-button theme="primary" @click="handleSave" style="margin-right: 8px;">保存</bk-button>
                        <bk-button @click="get_setup()">取消</bk-button>
                    </bk-form-item>
                </bk-form>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                imgSrc: '',
                loading: false,
                sysForm: [],
                edit_sysForm: [],
                isEdit: false,
                reg: '',
                re: '',
                resultVerify: ''
            }
        },
        created() {
            this.get_setup()
            this.getLogo()
        },
        methods: {
            // 验证
            verifyData(val) {
                if (val.key === 'BKAPP_CMDB_IP') {
                    this.reg =
                        /^((\d)|([1-9]\d)|(1\d{2})|((2[0-4]\d)|(25[0-5])))(\.((\d)|([1-9]\d)|(1\d{2})|((2[0-4]\d)|(25[0-5])))){3}$/
                    this.re = new RegExp(this.reg)
                } else if (val.key === 'BKAPP_CMDB_PORT') {
                    this.reg =
                        /^([0-9]|[1-9]\d|[1-9]\d{2}|[1-9]\d{3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$/
                    this.re = new RegExp(this.reg)
                } else if (val.key === 'BKAPP_SUPPLIER_ACCOUNT') {
                    this.reg = /^[1-9]\d*|0$/
                    this.re = new RegExp(this.reg)
                } else if (val.key === 'BKAPP_CMDB_API_VERSION') {
                    this.reg = /^[A-Za-z0-9]+$/
                    this.re = new RegExp(this.reg)
                } else if (val.key === 'DAILY_TIME') {
                    this.reg = /^[0-9]*$/
                    this.re = new RegExp(this.reg)
                }
                this.alertInfo(val.value)
            },
            alertInfo(val) {
                if (!this.re.test(val)) {
                    this.$bkMessage({
                        theme: 'warning',
                        message: '请填写合法信息！ ',
                        limit: 1
                    })
                    this.resultVerify = false
                    return this.resultVerify
                } else {
                    this.resultVerify = true
                    return this.resultVerify
                }
            },
            get_setup() {
                this.isEdit = false
                this.loading = true
                this.$api.setting.list().then(res => {
                    this.loading = false
                    if (res.result) {
                        this.sysForm = res.data.items
                        this.edit_sysForm = this.sysForm
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                })
            },
            // 保存修改设置
            handleSave(val) {
                this.loading = true
                for (const i in this.edit_sysForm) {
                    if (this.edit_sysForm[i].value === null || this.edit_sysForm[i].value === '') {
                        this.$bkMessage({
                            theme: 'warning',
                            message: this.edit_sysForm[i].description + '不可为空！ ',
                            delay: 0
                        })
                        return false
                    }
                    this.loading = false
                }
                if (this.resultVerify) {
                    this.$api.setting.batch_update(this.edit_sysForm).then(res => {
                        this.loading = false
                        if (res.result) {
                            this.get_setup()
                            this.$cwMessage('保存成功！', 'success')
                            this.isEdit = false
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                    })
                } else {
                    this.loading = false
                    this.$cwMessage('请输入有效数据！', 'warning')
                }
            },
            uploadLogo() {
                document.getElementById('uploadFile').value = ''
                document.getElementById('uploadFile').click()
            },
            uploadFile() {
                const config = {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
                const file = document.getElementById('uploadFile').files[0]
                const filetypearry = ['png', 'jpg', 'jpeg']
                if ((file.size / 1024 / 1024) < 50) {
                    let isqualified = true
                    for (let a = 0; a < filetypearry.length; a++) {
                        if (filetypearry[a] === (file.name.split('.')[file.name.split('.').length - 1]).toString()) {
                            isqualified = false
                            this.fileData = new FormData()
                            this.fileData.append('file', file)
                            this.fileData.append('flag', true)
                            this.loading = true
                            this.$api.setting.update_logo(this.fileData, config).then(res => {
                                this.loading = false
                                if (res.result) {
                                    this.$cwMessage('上传成功！', 'success')
                                    setTimeout(() => {
                                        window.location.reload()
                                    }, 200)
                                } else {
                                    this.$cwMessage(res.message, 'error')
                                }
                            })
                            break
                        }
                    }
                    if (isqualified) {
                        this.$cwMessage('请上传支持的文件格式(png,jpg,jpeg)！', 'error')
                    }
                } else {
                    this.$cwMessage('请上传50M大小以内的文件！', 'error')
                }
            },
            init_logo() {
                this.$bkInfo({
                    type: 'primary',
                    title: '确定恢复默认吗？',
                    confirmLoading: false,
                    confirmFn: async() => {
                        this.loading = true
                        this.$api.setting.reset_logo().then(res => {
                            this.loading = false
                            if (res.result) {
                                this.$cwMessage('恢复成功', 'success')
                                setTimeout(() => {
                                    window.location.reload()
                                }, 200)
                            } else {
                                this.$cwMessage(res.message, 'error')
                            }
                        })
                    }
                })
            },
            getLogo() {
                this.$api.setting.get_logo().then(res => {
                    if (res.result) {
                        this.imgSrc = 'data:image/png;base64,' + res.data.logo
                    }
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #sysSetup {
        padding: 20px;

        .card {
            background-color: #fff;
            border: 1px solid #DCDEE5;
            padding: 20px 0 0 16px;
            margin-bottom: 16px;

            .title {
                font-size: 14px;
                color: #63656E;
                line-height: 20px;
                height: 20px;
                font-weight: bold;
            }
        }

        .card-log {
            padding-bottom: 20px;

            .content {
                display: flex;
                align-items: center;
                margin-top: 35px;

                .info {
                    font-size: 12px;
                }

                .img {
                    width: 80px;
                    height: 80px;
                    text-align: center;
                    padding-top: 4px;
                    border: 1px solid #C4C6CC;
                    background: #FAFBFD;
                    border-radius: 2px;
                    margin: 0 40px 0 20px;

                    img {
                        height: 68px;
                        width: 68px;
                    }
                }
            }
        }

        .card-sys {
            padding-bottom: 30px;
            padding-right: 46px;

            .content {
                margin-top: 35px;
            }
        }
    }
</style>
