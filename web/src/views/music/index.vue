<template>
    <div>
        <div>
            <div class="input-demo">
                <bk-input v-model="value"></bk-input>
            </div>
            <bk-button :theme="'primary'" :title="'主要按钮'" class="mr10" @click="handleMergeArtist">
                合并艺术家
            </bk-button>
        </div>
        <div>
            <div class="input-demo">
                <bk-input v-model="value2"></bk-input>
            </div>
            <bk-button :theme="'primary'" :title="'主要按钮'" class="mr10" @click="handleMergeAlbum">
                合并专辑
            </bk-button>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'index',
        data() {
            return {
                value: '',
                value2: ''
            }
        },
        methods: {
            // 合并艺术家
            handleMergeArtist() {
                this.$api.Task.mergeArtist({full_text: this.value}).then((res) => {
                    console.log(res)
                    if (res.result) {
                        this.$cwMessage('修改成功', 'success')
                    } else {
                        this.$cwMessage('修改失败', 'error')
                    }
                })
            },
            // 合并专辑
            handleMergeAlbum() {
                this.$api.Task.mergeAlbum({full_text: this.value2}).then((res) => {
                    console.log(res)
                    if (res.result) {
                        this.$cwMessage('修改成功', 'success')
                    } else {
                        this.$cwMessage('修改失败', 'error')
                    }
                })
            }
        }
    }
</script>

<style scoped>

</style>
