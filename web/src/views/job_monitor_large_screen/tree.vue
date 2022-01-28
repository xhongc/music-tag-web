<template>
    <div id="tree">
        <div>
            <bk-input @change="filterTree" placeholder="输入系统名称" :right-icon="'bk-icon icon-search'" v-model="treeSeachVal"></bk-input>
        </div>
        <div class="topo-tree-wrap" v-bkloading="{ isLoading: topoTreeLoading, zIndex: 10 }" style="margin-top: 12px;">
            <bk-big-tree ref="topoTree" :data="treeList" :options="defaultProps" :display-matched-node-descendants="true"
                :ext-cls="'custom-tree'" @select-change="handleNodeSelect" :expand-on-click="false" :default-expand-all="true"
                :default-selected-node="defaultNode" :selectable="true">
            </bk-big-tree>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                treeSeachVal: '',
                treeList: [{
                    id: 'all',
                    label: '所有系统'
                    // child: []
                }],
                topoTreeLoading: false,
                defaultProps: {
                    idKey: 'id',
                    nameKey: 'label',
                    childrenKey: 'child'
                },
                defaultNode: 'all'
            }
        },
        created() {
            this.initTopoTree()
        },
        methods: {
            // 节点搜索
            filterTree(value = '') {
                this.$refs.topoTree.filter(value)
            },
            handleNodeSelect(e) {
                this.$emit('node-select', e)
            },
            initTopoTree() {
                this.topoTreeLoading = true
                this.$api.category.get_topology().then(res => {
                    if (res.result) {
                        this.$set(this.treeList[0], 'child', res.data.nodes)
                        this.$refs.topoTree.setData(this.treeList)
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.topoTreeLoading = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    #tree {
        height: 100%;

        .topo-tree-wrap {
            height: 100%;

            .custom-tree {
                height: 100%;
            }
        }
    }
</style>
