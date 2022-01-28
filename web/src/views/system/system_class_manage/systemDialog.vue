<template>
    <div id="system">
        <bk-form ref="form" :label-width="120" :rules="rules" :model="form">
            <bk-form-item label="系统类别名称" :error-display-type="'normal'" :required="true" :property="'name'">
                <bk-input placeholder="请输入系统类别名称" v-model="form.name"></bk-input>
            </bk-form-item>
            <bk-form-item label="描述" :error-display-type="'normal'" :required="true" :property="'description'">
                <bk-input placeholder="请输入描述" v-model="form.description"></bk-input>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    export default {
        // props: ['systemForm'],
        props: {
            systemForm: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                form: {
                    name: '',
                    description: ''
                },
                rules: {
                    name: [{
                        required: true,
                        message: '系统类别名称不能为空',
                        trigger: 'blur'
                    }],
                    description: [{
                        required: true,
                        message: '描述不能为空',
                        trigger: 'blur'
                    }]
                }
            }
        },
        created() {
            this.form = this.systemForm
        }
    }
</script>

<style lang="scss" scoped>
    #system {}
</style>
