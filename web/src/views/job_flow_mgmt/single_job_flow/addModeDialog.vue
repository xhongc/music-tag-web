<template>
    <div id="addModeDialog">
        <bk-radio-group v-model="modeValue">
            <bk-radio :value="'node'" style="margin-right: 24px;">前置节点</bk-radio>
            <bk-radio :value="'flow'">前置作业流</bk-radio>
        </bk-radio-group>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                modeValue: 'flow'
            }
        }
    }
</script>

<style>
</style>
