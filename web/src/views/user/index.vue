<template>
    <div>
        <div>
            <div style="margin: 20px;">
                <bk-button :theme="'default'" type="submit" :title="'基础按钮'" @click="handleClick" class="mr10">
                    新增用户
                </bk-button>
            </div>
            <div style="margin: 20px;">
                <bk-table
                    :data="data"
                    :size="size"
                    :pagination="pagination"
                    custom-header-color="#e2ebf0"
                    custom-header-color-hover="#cfd9df"
                    @page-change="handlePageChange">
                    <bk-table-column type="selection" width="60"></bk-table-column>
                    <bk-table-column type="index" label="序列" width="60"></bk-table-column>
                    <bk-table-column label="名称/内网IP" prop="ip"></bk-table-column>
                    <bk-table-column label="来源" prop="source"></bk-table-column>
                    <bk-table-column label="状态" prop="status"></bk-table-column>
                    <bk-table-column label="创建时间" prop="create_time"></bk-table-column>
                    <bk-table-column label="操作" width="150">
                        <template slot-scope="props">
                            <bk-button class="mr10" theme="primary" text @click="edit(props.row)">编辑</bk-button>
                            <bk-button class="mr10" theme="primary" text @click="remove(props.row)">删除</bk-button>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
        </div>
        <bk-dialog v-model="exampleSetting1.primary.visible"
            theme="primary"
            :mask-close="false"
            :header-position="exampleSetting1.primary.headerPosition"
            :title="exampleSetting1.primary.title">
            <bk-form :label-width="80" :model="formData">
                <bk-form-item label="手机号" :required="true" :property="'username'">
                    <bk-input v-model="formData.username"></bk-input>
                </bk-form-item>
                <bk-form-item label="用户密码" :required="true" :property="'pwd'">
                    <bk-input v-model="formData.pwd" :type="'password'"></bk-input>
                </bk-form-item>
                <bk-form-item label="角色" :required="true" :property="'role'">
                    <bk-select
                        :disabled="false"
                        v-model="formData.role"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                        searchable>
                        <bk-option v-for="option in roleList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                size: 'small',
                data: [
                    {
                        ip: '192.168.0.1',
                        source: 'QQ',
                        status: '创建中',
                        create_time: '2018-05-25 15:02:24',
                        children: [
                            {
                                name: '用户管理',
                                count: '23',
                                creator: 'person2',
                                create_time: '2017-10-10 11:12',
                                desc: '用户管理'
                            },
                            {
                                name: '模块管理',
                                count: '2',
                                creator: 'person1',
                                create_time: '2017-10-10 11:12',
                                desc: '无数据测试'
                            }
                        ]
                    },
                    {
                        ip: '192.168.0.2',
                        source: '微信',
                        status: '正常',
                        create_time: '2018-05-25 15:02:24',
                        children: [
                            {
                                name: '用户管理',
                                count: '23',
                                creator: 'person2',
                                create_time: '2017-10-10 11:12',
                                desc: '用户管理'
                            },
                            {
                                name: '模块管理',
                                count: '2',
                                creator: 'person1',
                                create_time: '2017-10-10 11:12',
                                desc: '无数据测试'
                            }
                        ]
                    },
                    {
                        ip: '192.168.0.3',
                        source: 'QQ',
                        status: '创建中',
                        create_time: '2018-05-25 15:02:24',
                        children: [
                            {
                                name: '用户管理',
                                count: '23',
                                creator: 'person2',
                                create_time: '2017-10-10 11:12',
                                desc: '用户管理'
                            },
                            {
                                name: '模块管理',
                                count: '2',
                                creator: 'person1',
                                create_time: '2017-10-10 11:12',
                                desc: '无数据测试'
                            }
                        ]
                    }
                ],
                pagination: {
                    current: 1,
                    count: 500,
                    limit: 15
                },
                exampleSetting1: {
                    primary: {
                        visible: false,
                        headerPosition: 'left',
                        title: '新增用户'
                    }
                },
                formData: {},
                roleList: [
                    {id: 1, name: '角色1'},
                    {id: 2, name: '角色2'},
                    {id: 3, name: '角色3'}
                ]
            }
        },
        methods: {
            handlePageChange(page) {
                this.pagination.current = page
            },
            remove(row) {
                const index = this.data.indexOf(row)
                if (index !== -1) {
                    this.data.splice(index, 1)
                }
            },
            edit(row) {
                this.formData = row
                this.exampleSetting1.primary.visible = true
                this.exampleSetting1.primary.title = '修改用户'
            },
            handleClick() {
                this.exampleSetting1.primary.visible = true
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
