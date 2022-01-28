<template>
    <div id="scanFile" v-bkloading="{ isLoading: scanFileLoading, zIndex: 10 }">
        <div class="content-box">
            <div class="title">导入结果</div>
            <div class="job-info">
                <p style="width: 152px;">作业流配置检测：OK</p>
                <p class="mt16" v-if="createData.length !== 0">新增作业数：<span>{{createData.length}}</span></p>
                <p class="mt16" v-if="updateData.length !== 0">修改作业数：<span>{{updateData.length}}</span></p>
                <p class="mt16" v-if="messageData.length !== 0">异常作业数：<span>{{messageData.length}}</span></p>
            </div>
        </div>
        <div class="content-box" v-if="createData.length !== 0">
            <div class="title">新增作业</div>
            <div class="table">
                <bk-table ref="table" :data="createData">
                    <bk-table-column label="作业名" prop="name"></bk-table-column>
                    <bk-table-column label="Agent" prop="agent.name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="IP" prop="agent.data.bk_host_innerip"></bk-table-column>
                    <bk-table-column label="系统类型" prop="agent.data.bk_os_name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="执行账号" prop="account" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="脚本" prop="script_content" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="作业描述" prop="desc" :show-overflow-tooltip="true"></bk-table-column>
                </bk-table>
            </div>
        </div>
        <div class="content-box" v-if="updateData.length !== 0">
            <div class="title">修改作业</div>
            <div class="table">
                <bk-table ref="table" :data="updateData">
                    <bk-table-column label="作业名" prop="name"></bk-table-column>
                    <bk-table-column label="Agent" prop="agent.name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="IP" prop="agent.data.bk_host_innerip"></bk-table-column>
                    <bk-table-column label="系统类型" prop="agent.data.bk_os_name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="执行账号" prop="account" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="脚本" prop="script_content" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="作业描述" prop="desc" :show-overflow-tooltip="true"></bk-table-column>
                </bk-table>
            </div>
        </div>
        <div class="content-box" v-if="messageData.length !== 0">
            <div class="title">异常作业</div>
            <div class="table">
                <bk-table ref="table" :data="messageData">
                    <bk-table-column label="作业名" prop="name"></bk-table-column>
                    <bk-table-column label="Agent" prop="ip.name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="IP" prop="ip.bk_host_innerip"></bk-table-column>
                    <bk-table-column label="系统类型" prop="ip.bk_os_name" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="执行账号" prop="account" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="脚本" prop="script_content" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="作业描述" prop="desc" :show-overflow-tooltip="true"></bk-table-column>
                    <bk-table-column label="错误信息" prop="message" :show-overflow-tooltip="true"></bk-table-column>
                </bk-table>
            </div>
        </div>
        <div class="footer">
            <bk-button theme="primary" @click="handleSave" style="margin-right: 12px;">保存</bk-button>
            <bk-button @click="handleCancel">取消本次上传</bk-button>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                createData: [], // 新增作业
                updateData: [], // 修改作业
                messageData: [], // 异常作业
                scanFileLoading: false
            }
        },
        created() {
            if (this.$route.params.data) {
                this.handleCheckData()
            } else {
                this.$cwMessage('请上传文件！', 'error')
            }
        },
        methods: {
            handleSave() {
                this.scanFileLoading = true
                this.$api.content.save_job_data({
                    'update': this.updateData,
                    'create': this.createData
                }).then(res => {
                    if (res.result) {
                        this.$cwMessage('添加成功！', 'success')
                        this.$router.push({
                            path: '/joblist'
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.scanFileLoading = false
                })
            },
            handleCancel() {
                this.$router.go(-1)
            },
            // 处理导入数据检查
            handleCheckData() {
                this.scanFileLoading = true
                this.$api.content.check_job(this.$route.params).then(res => {
                    if (res.result) {
                        this.createData = res.data.create
                        this.updateData = res.data.update
                        this.messageData = res.data.message
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.scanFileLoading = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #scanFile {
        padding: 20px;
        height: 100%;
        overflow: auto;

        .content-box {
            margin-bottom: 20px;

            .title {
                font-size: 14px;
                font-weight: bold;
                color: '#63656E';
                height: 22px;
                line-height: 22px;
                margin-bottom: 12px;
            }

            .job-info {
                p {
                    width: 140px;
                    text-align: right;
                }

                .mt16 {
                    margin-top: 16px;
                }
            }
        }

        .footer {
            font-size: 0px;
        }
    }
</style>
