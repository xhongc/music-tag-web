<template>
    <div id="varChange" v-bkloading="{ isLoading: varChangeLoading, zIndex: 10 }">
        <bk-form ext-cls="costum-form" :model="form" :rules="rules" ref="form" :label-width="90">
            <bk-form-item label="变量表名:" :error-display-type="'normal'" :required="true" :property="'name'">
                <bk-input v-model="form.name" :disabled="disabled"></bk-input>
            </bk-form-item>
            <bk-form-item label="描述:">
                <bk-input v-model="form.description" :disabled="disabled"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-table ref="table" :data="tableList" ext-cls="customTable">
                    <bk-table-column label="变量类型" prop="type" :show-overflow-tooltip="true" align="center">
                        <template slot-scope="props">
                            <bk-select v-if="props.row.edit" v-model="props.row.type" style="background-color: #fff;">
                                <bk-option v-for="option in variableTypeList" :key="option.id" :id="option.value"
                                    :name="option.label"></bk-option>
                            </bk-select>
                            <div v-else>
                                <span v-if="props.row.type === 'common'">普通变量</span>
                                <span v-if="props.row.type === 'sensitive'">敏感变量</span>
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column label="变量名" prop="name" :show-overflow-tooltip="true" align="center">
                        <template slot-scope="props">
                            <bk-input v-model="props.row.name" v-if="props.row.edit"></bk-input>
                            <span v-else>{{props.row.name}}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column label="变量值" prop="value" :show-overflow-tooltip="true" align="center">
                        <template slot-scope="props">
                            <bk-input v-model="props.row.value" v-if="props.row.edit"></bk-input>
                            <span v-else>{{props.row.value}}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column label="操作" v-if="$route.query.type === 'detail' ? false : true">
                        <template slot-scope="props">
                            <bk-button class="mr10" theme="primary" text v-if="!props.row.edit"
                                @click="props.row.edit = !props.row.edit">解锁</bk-button>
                            <bk-button class="mr10" theme="primary" text v-if="props.row.edit"
                                @click="handleLock(props.row)">锁定</bk-button>
                            <bk-button class="mr10" theme="primary" text @click="handleDelete(props.$index)">删除
                            </bk-button>
                        </template>
                    </bk-table-column>
                </bk-table>
                <div class="addBtn" v-if="$route.query.type === 'detail' ? false : true" style="text-align: center;">
                    <bk-button theme="default" title="新增" icon="plus" style="width: 120px;font-size: 12px;"
                        @click="handleAdd">新增</bk-button>
                </div>
            </bk-form-item>
            <bk-form-item style="font-size: 0px;">
                <bk-button theme="primary" style="margin-right: 8px;" @click="handleConfim"
                    v-if="$route.query.type === 'detail' ? false : true">确定</bk-button>
                <bk-button @click="handleCancel" v-if="$route.query.type === 'detail' ? false : true">取消</bk-button>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                disabled: false,
                varChangeLoading: false,
                variableTypeList: [{
                                       id: 1,
                                       label: '普通变量',
                                       value: 'common'
                                   },
                                   {
                                       id: 2,
                                       label: '敏感变量',
                                       value: 'sensitive'
                                   }
                ],
                tableList: [],
                form: {
                    name: '',
                    description: ''
                },
                rules: {
                    name: [{
                        required: true,
                        message: '变量表名不能为空',
                        trigger: 'change'
                    }]
                }
            }
        },
        created() {
            if (this.$route.query.type !== 'add') {
                this.handleLoad()
                if (this.$route.query.type === 'detail') {
                    this.disabled = true
                }
            }
        },
        methods: {
            // 处理初始化数据
            handleLoad() {
                this.varChangeLoading = true
                this.$api.varTable.retrieve(parseInt(this.$route.query.id)).then(res => {
                    if (res.result) {
                        const data = res.data
                        this.tableList = data.data.map(item => {
                            return {
                                type: item.type,
                                name: item.name,
                                value: item.value,
                                edit: false
                            }
                        })
                        this.form.name = data.name
                        this.form.description = data.description
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.varChangeLoading = false
                })
            },
            // 处理确定
            handleConfim() {
                this.$refs.form.validate().then(validator => {
                    if (this.tableList.length === 0) {
                        return this.$cwMessage('至少新增一条变量！', 'warning')
                    } else {
                        // 判断表格中是否有某行未锁定，未锁定即表明未填完
                        const flag = this.tableList.some(item => {
                            return item.edit === true
                        })
                        if (flag) {
                            return this.$cwMessage('请补充完整表格数据后锁定确认！', 'warning')
                        } else {
                            const params = {
                                ...this.form,
                                data: this.tableList.map(item => {
                                    return {
                                        type: item.type,
                                        name: item.name,
                                        value: item.value
                                    }
                                })
                            }
                            if (this.$route.query.type === 'add') {
                                this.handleSaveAdd(params)
                            } else {
                                this.handleSaveUpdate(params)
                            }
                        }
                    }
                }).catch(e => {
                    this.$cwMessage('您的输入有误，请检查输入！', 'warning')
                })
            },
            // 处理新增保存
            handleSaveAdd(params) {
                this.varChangeLoading = true
                this.$api.varTable.create(params).then(res => {
                    if (res.result) {
                        this.$cwMessage('新增成功！', 'success')
                        this.$router.push({
                            path: '/variablemgmt'
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.varChangeLoading = false
                })
            },
            // 处理修改保存
            handleSaveUpdate(params) {
                this.varChangeLoading = true
                this.$api.varTable.update(parseInt(this.$route.query.id), params).then(res => {
                    if (res.result) {
                        this.$cwMessage('修改成功！', 'success')
                        this.$router.push({
                            path: '/variablemgmt'
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.varChangeLoading = false
                })
            },
            // 处理取消
            handleCancel() {
                this.$router.go(-1)
            },
            // 处理锁定
            handleLock(row) {
                if (row.type === '') {
                    return this.$cwMessage('变量类型不能为空！', 'warning')
                }
                if (row.name === '') {
                    return this.$cwMessage('变量名不能为空！', 'warning')
                }
                if (row.value === '') {
                    return this.$cwMessage('变量值不能为空！', 'warning')
                }
                row.edit = false
            },
            // 处理新增
            handleAdd() {
                const item = {
                    type: '',
                    name: '',
                    value: '',
                    edit: true
                }
                this.tableList.push(item)
            },
            // 处理删除
            handleDelete(index) {
                this.tableList.splice(index, 1)
            }
        }
    }
</script>

<style lang="scss" scoped>
    #varChange {
        padding: 20px;

        .costum-form {
            width: 900px;

            .customTable {
                /deep/ .bk-table-empty-block {
                    background-color: #fff;
                }
            }

            .addBtn {
                padding: 10px 20px;
                border: 1px dashed #ccc;
                border-top: 0px;
                background-color: #fff;
            }
        }
    }
</style>
