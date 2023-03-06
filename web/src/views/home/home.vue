<template>
    <div>
        <div>
            <bk-input :clearable="true" v-model="value"></bk-input>
            <bk-tree
                ref="tree1"
                :data="treeListOne"
                :node-key="'id'"
                :has-border="true"
                @on-click="nodeClickOne"
                @on-expanded="nodeExpandedOne">
            </bk-tree>
        </div>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                treeListOne: [
                    {
                        name: 'tree node1',
                        title: 'tree node1',
                        expanded: true,
                        id: 1,
                        children: [
                            {
                                name: 'tree node 1-1',
                                title: 'tree node 1-1',
                                expanded: true,
                                children: [
                                    {name: 'tree node 1-1-1', title: 'tree node 1-1-1', id: 2},
                                    {name: 'tree node 1-1-2', title: 'tree node 1-1-2', id: 3},
                                    {name: 'tree node 1-1-3', title: 'tree node 1-1-3', id: 4}
                                ]
                            },
                            {
                                title: 'tree node 1-2',
                                name: 'tree node 1-2',
                                id: 5,
                                expanded: true,
                                children: [
                                    {name: 'tree node 1-2-1', title: 'tree node 1-2-1', id: 6},
                                    {name: 'tree node 1-2-2', title: 'tree node 1-2-2', id: 7}
                                ]
                            }
                        ]
                    }
                ]
            }
        },
        methods: {
            nodeClickOne(node) {
                console.log(node)
            },
            nodeExpandedOne(node, expanded) {
                console.log(node)
                console.log(expanded)
            }
        }
    }
</script>
<style lang="postcss">
.bk-table-header .custom-header-cell {
    color: inherit;
    text-decoration: underline;
    text-decoration-style: dashed;
    text-underline-position: under;
}
</style>
