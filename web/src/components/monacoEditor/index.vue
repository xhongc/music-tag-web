<template>
    <div id="editor">
        <div :style="{height: height, width: width}" ref="codeEditor" id="codeEditor"></div>
    </div>
</template>

<script>
    // 引用组件
    import * as monaco from 'monaco-editor'
    export default {
        props: {
            codes: {
                type: String,
                default: ''
            },
            height: {
                default: '100px'
            },
            width: {
                default: '100%'
            },
            language: {
                type: String,
                default: function() {
                    return 'shell'
                }
            },
            readOnly: {
                type: Boolean,
                default: false
            }
        },
        data() {
            return {
                monacoEditor: null,
            }
        },
        mounted() {
            this.initEditor()
        },
        methods: {
            //修改为只读
            changeReadOnly() {
                //此例为更改编辑器为只读模式,其余以此类推
                this.monacoEditor.updateOptions({
                    readOnly: true
                })
            },
            //更改编辑器语言
            changeModel(e, str) {
                let value = ''
                var oldModel = this.monacoEditor.getModel(); //获取旧模型
                if (str) {
                    value = str
                } else {
                    value = this.monacoEditor.getValue(); //获取旧的文本
                }
                //第一个参数为编辑器默认文本，第二个参数为语言
                var newModel = monaco.editor.createModel(value, e);
                //将旧模型销毁
                if (oldModel) {
                    oldModel.dispose();
                }
                //设置新模型
                this.monacoEditor.setModel(newModel);
            },
            initEditor() {
                // 初始化编辑器，确保dom已经渲染
                console.log(this.codes)
                this.monacoEditor = monaco.editor.create(this.$refs.codeEditor, {
                    value: this.codes, //编辑器初始显示文字
                    language: this.language, //语言支持自行查阅demo
                    automaticLayout: true, //自动布局
                    theme: 'vs-dark', //官方自带三种主题vs, hc-black, or vs-dark
                    readOnly: this.readOnly
                });
            },
        }
    }
</script>

<style lang="scss" scoped>
    #editor {
        // position: relative;
        // overflow: hidden;
    }
</style>
