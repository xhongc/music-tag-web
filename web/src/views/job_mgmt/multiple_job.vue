<template>
    <div id="multipleJob">
        <div class="content" :style="{ height: currentFiles.length === 0 ? 240 + 'px' : 290 + 'px' }">
            <div class="title">文件来源</div>
            <div class="upload-box">
                <bk-upload :theme="'button'" :tip="'拓展名为json后缀'" :with-credentials="true" :url="uploadUrl"
                    ext-cls="custom-upload" :header="requestHeader" :handle-res-code="handleRes" :limit="1" @on-delete="handleDelete"></bk-upload>
                <p @click="handleDownload">下载实例文件</p>
                <div class="footer" v-if="currentFiles.length">
                    <bk-button theme="primary" @click="handleSave" style="margin-right: 12px;">保存</bk-button>
                    <bk-button @click="handleCancel">取消</bk-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                requestHeader: {},
                currentFiles: []
            }
        },
        computed: {
            uploadUrl() {
                return window.siteUrl + '/content/upload_contents/'
            }
        },
        created() {
            this.getRequestHeader()
        },
        methods: {
            handleDelete(file, fileList) {
                this.currentFiles = []
            },
            handleSave() {
                this.$router.push({
                    name: 'ScanFile',
                    params: {
                        data: this.currentFiles
                    }
                })
            },
            // 处理取消
            handleCancel() {
                this.$router.go(-1)
            },
            handleRes(res) {
                if (res.result) {
                    this.$cwMessage('上传成功！', 'success')
                    this.currentFiles = res.data
                    return true
                } else {
                    this.$cwMessage(res.message, 'error')
                    return false
                }
            },
            // 处理下载实例文件
            handleDownload() {
                window.open(window.siteUrl + '/export/demo_batch_import_jobs')
            },
            // 获取请求头
            getRequestHeader() {
                const name = window.CSRF_COOKIE_NAME || 'csrftoken'
                let cookieValue = 'NOTPROVIDED'
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';')
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim()
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                            break
                        }
                    }
                }
                this.requestHeader = {
                    name: 'X-CSRFToken',
                    value: cookieValue
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    #multipleJob {
        padding: 20px;
        height: 100%;
        position: relative;

        .content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 656px;
            // height: 240px;
            // overflow: auto;
            background-color: #fff;
            border: 1px solid #DCDEE5;
            padding: 16px 20px;

            .title {
                height: 19px;
                font-size: 14px;
                font-weight: bold;
                color: #313238;
                line-height: 19px;
            }

            .upload-box {
                margin: 29px 0 0 34px;

                .custom-upload {
                    /deep/ .tip {
                        font-size: 12px;
                        color: #979BA5;
                    }
                }

                p {
                    margin-top: 12px;
                    font-size: 12px;
                    color: #3A84FF;
                    height: 20px;
                    line-height: 20px;
                    cursor: pointer;
                }

                .footer {
                    font-size: 0px;
                    margin-top: 36px;
                }
            }
        }
    }
</style>
