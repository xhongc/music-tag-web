<template>
    <div id="topMenu">
        <div class="view-btn">
            <i class="iconfont icon-mianxingtubiao-xitong" @click="handleOpenScreen" :style="{ color: viewBtnActive === 1 ? '#3A84FF' : '#979BA5', background: viewBtnActive === 1 ? '#E1ECFF' : 'rgb(244,246,249)' }"></i>
            <i class="iconfont icon-mianxingtubiao-dangrizuoyezongshu" @click="handleOpenJob" :style="{ color: viewBtnActive === 2 ? '#3A84FF' : '#979BA5', background: viewBtnActive === 2 ? '#E1ECFF' : 'rgb(244,246,249)' }"></i>
        </div>
        <div class="graph-btn">
            <i class="iconfont icon-xianxingtubiao-fuwei" @click="handleReset" title="复位"></i>
            <i class="iconfont icon-xianxingtubiao-quanping" @click="handleFullScreen" title="全屏"></i>
            <i class="iconfont icon-xianxingtubiao-baocun" @click="handleSave" title="保存"></i>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                viewBtnActive: 1
            }
        },
        methods: {
            // 处理打开大屏
            handleOpenScreen() {
                if (this.viewBtnActive === 1) return false
                this.viewBtnActive = 1
                this.$emit('open-sys-screen', 'all')
            },
            // 处理打开作业流
            handleOpenJob() {
                if (this.viewBtnActive === 2) return false
                this.viewBtnActive = 2
                this.$emit('open-job-flow', 'all')
            },
            // 处理复位
            handleReset() {
                this.$emit('on-reset')
            },
            // 处理打开全屏
            handleFullScreen() {
                this.$emit('full-screen')
            },
            // 处理保存
            handleSave() {
                this.$cwMessage('保存配置成功！', 'success')
            }
        }
    }
</script>

<style lang="scss" scoped>
    #topMenu {
        .view-btn {
            display: inline-block;
            font-size: 0px;
            margin-right: 20px;
            border: 1px solid #DCDEE5;

            i {
                font-size: 20px;
                width: 36px;
                text-align: center;
                height: 32px;
                line-height: 32px;
                display: inline-block;
                cursor: pointer;
            }
        }
        .graph-btn {
            display: inline-block;
            i {
                font-size: 20px;
                margin-right: 12px;
                color: #979BA5;
                cursor: pointer;
            }
        }
    }
</style>
