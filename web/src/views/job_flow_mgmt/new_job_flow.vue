<template>
    <div id="newJobFlow">
        <div class="content">
            <p class="title">请选择新建作业流方式</p>
            <div class="card-box">
                <div class="card" style="cursor: pointer;" @click="handleAddJobFlow('single')">
                    <i class="iconfont icon-mianxingtubiao-xinjiandangezuoyeliu"></i>
                    <p>通过定义作业流的名称、调度方式、前置依赖和任务编排等信息新建单个作业流。</p>
                    <bk-button style="margin-top: 20px;" @click="handleAddJobFlow('single')" v-if="auth.create" :hover-theme="'primary'">单个作业流新建</bk-button>
                </div>
                <div class="card" style="margin-left: 16px;cursor: pointer;" @click="handleAddJobFlow('batch')">
                    <i class="iconfont icon-mianxingtubiao-piliangzuoyedaoru"></i>
                    <p>通过json文件定义作业流名称、调度方式、作业节点的关联和前置依赖等信息批量新建作业流。</p>
                    <bk-button style="margin-top: 20px;" @click="handleAddJobFlow('batch')" v-if="auth.create" :hover-theme="'primary'">批量作业流导入</bk-button>
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
            handleAddJobFlow(str) {
                if (str === 'single') {
                    this.$router.push({
                        path: '/singlejobflow',
                        query: {
                            type: 'add'
                        }
                    })
                } else {
                    this.$router.push({
                        path: '/multiplejobflow',
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
    #newJobFlow {
        // padding: 20px;
        height: 100%;
        width: 100%;
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
                    // height: 200px;
                    border: 1px solid #DCDEE5;
                    background-color: #fff;
                    padding: 40px 30px 40px 30px;
                    &:hover {
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
