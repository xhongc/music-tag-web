<template>
    <div id="newJob">
        <div class="content">
            <p class="title">请选择新建作业方式</p>
            <div class="card-box">
                <div class="card" @click="handleAddJob('single')" style="cursor: pointer;">
                    <i class="iconfont icon-mianxingtubiao-xinjiandangezuoye"></i>
                    <p>通过定义单个作业的名称、描述、跑批系统、Agent等基本信息新建单个作业。</p>
                    <bk-button style="margin-top: 20px;" @click="handleAddJob('single')" v-if="auth.create" :hover-theme="'primary'">单个作业新建</bk-button>
                </div>
                <div class="card" style="margin-left: 16px;cursor: pointer;" @click="handleAddJob('batch')">
                    <i class="iconfont icon-mianxingtubiao-piliangzuoyeliudaoru"></i>
                    <p>通过json文件定义作业的名称、跑批系统、Agent和基本信息批量新建作业。</p>
                    <bk-button style="margin-top: 20px;" @click="handleAddJob('batch')" v-if="auth.create" :hover-theme="'primary'">批量作业导入</bk-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                auth: {}
            }
        },
        created() {
            this.auth = this.hasPerm(this.$route.path)
        },
        methods: {
            handleAddJob(str) {
                if (str === 'single') {
                    this.$router.push({
                        path: '/singlejob',
                        query: {
                            type: 'add'
                        }
                    })
                } else {
                    this.$router.push({
                        path: '/multiplejob',
                        query: {
                            type: 'add'
                        }
                    })
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    #newJob {
        // padding: 20px;
        height: 100%;
        position: relative;

        .content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);

            .title {
                font-size: 16px;
                color: #63656E;
                height: 24px;
                line-height: 24px;
            }

            .card-box {
                margin-top: 16px;
                font-size: 0px;
                display: flex;

                .card {
                    text-align: center;
                    width: 320px;
                    height: 240px;
                    border: 1px solid #DCDEE5;
                    background-color: #fff;
                    padding: 40px;
                    &:hover {
                        // box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
                        box-shadow: 0px 4px 12px 0px rgba(0, 0, 0, 0.08);
                    }

                    p {
                        font-size: 12px;
                        color: #63656E;
                        margin-top: 20px;
                    }

                    i {
                        font-size: 40px;
                        color: #3A84FF;
                        // background-color: #B62AE0;
                    }
                }
            }
        }
    }
</style>
