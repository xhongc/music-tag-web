<template>
    <div id="agengtMonitor">
        <div class="header" v-if="auth.search">
            <div style="float: left;">
                <bk-input clearable
                    width="240px"
                    style="width: 240px;margin-right: 8px;"
                    :placeholder="'请输入Agent名称'"
                    :right-icon="'bk-icon icon-search'"
                    v-model="searchFrom.name"
                    @right-icon-click="handleSearch"
                    @enter="handleSearch">
                </bk-input>
                <bk-button slot="dropdown-trigger" ext-cls :theme="isDropdownShow === true ? 'primary' : 'default'"
                    @click="handleOpenSeniorSearch" :icon-right="isDropdownShow === true ? 'angle-double-up' : 'angle-double-down'">高级搜索</bk-button>
            </div>
            <div class="senior-search-box" v-if="isDropdownShow">
                <bk-container :margin="0">
                    <bk-form :label-width="100">
                        <bk-row>
                            <bk-col :span="6">
                                <bk-form-item label="Agent:">
                                    <bk-input :placeholder="'请输入Agent'" v-model="searchFrom.name" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="IP:">
                                    <bk-input :placeholder="'请输入IP'" v-model="searchFrom.ip" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="Agent状态:">
                                    <bk-select :clearable="true" style="background-color: #fff;" v-model="searchFrom.is_online"
                                        :placeholder="'请选择'">
                                        <bk-option v-for="(item, index) in agentStatusList" :key="index" :id="item.value"
                                            :name="item.key">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                            <bk-col :span="6">
                                <bk-form-item label="跑批系统:">
                                    <bk-select :clearable="true" style="background-color: #fff;" v-model="searchFrom.category"
                                        :placeholder="'请选择'">
                                        <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id" :name="item.name">
                                        </bk-option>
                                    </bk-select>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="margin-top: 20px;">
                            <bk-col :span="6">
                                <bk-form-item label="操作系统">
                                    <bk-input :placeholder="'请输入操作系统'" v-model="searchFrom.os" clearable></bk-input>
                                </bk-form-item>
                            </bk-col>
                        </bk-row>
                        <bk-row style="display: flex;justify-content: center;margin-top: 20px;">
                            <bk-button theme="primary" @click="handleSearch">查询</bk-button>
                            <bk-button style="margin-left: 8px;" @click="handleReset">重置</bk-button>
                            <bk-button style="margin-left: 8px;" @click="handleOpenSeniorSearch">取消</bk-button>
                        </bk-row>
                    </bk-form>
                </bk-container>
            </div>
        </div>
        <div style="clear: both;"></div>
        <div class="content">
            <bk-table ref="table"
                :data="tableList"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange"
                v-bkloading="{ isLoading: tableLoading, zIndex: 10 }"
                ext-cls="customTable"
                :max-height="maxTableHeight">
                <bk-table-column label="Agent名称" prop="name"></bk-table-column>
                <bk-table-column label="所属业务" prop="biz" :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="IP" prop="ip"></bk-table-column>
                <bk-table-column label="跑批系统" prop="category" sortable :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="操作系统" prop="os" sortable :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{props.row.os === '' ? '- -' : props.row.os}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="Agent状态" prop="is_online" sortable :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <div v-if="props.row.is_online === 1">
                            <div class="status-btn" style="background-color: #2DCB56;"></div><span>在线</span>
                        </div>
                        <div v-else-if="props.row.is_online === 0"><div class="status-btn" style="background-color: #EA3636;"></div><span>离线</span></div>
                        <div v-else-if="props.row.is_online === 2"><div class="status-btn" style="background-color: #c4c6cc;"></div><span>未知</span></div>
                    </template>
                </bk-table-column>
                <bk-table-column label="Agent连接时长" prop="duration" sortable :show-overflow-tooltip="true">
                    <template slot-scope="props">
                        <span>{{(props.row.duration === '' || props.row.duration === null) ? '- -' : props.row.duration}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="CPU使用率(%)" prop="cpu_usage" sortable :show-overflow-tooltip="true"></bk-table-column>
                <bk-table-column label="内存使用率(%)" prop="mem_usage" sortable :show-overflow-tooltip="true"></bk-table-column>
            </bk-table>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                maxTableHeight: '',
                auth: {},
                tableLoading: false,
                tableList: [],
                agentStatusList: [{ // agent状态下拉列表
                    key: '未知',
                    value: 2
                }, {
                    key: '在线',
                    value: 1
                }, {
                    key: '离线',
                    value: 0
                }],
                runSysList: [], // 跑批系统下拉选择列表
                isDropdownShow: false,
                searchFrom: {
                    name: '', // agent名称
                    ip: '',
                    is_online: '', // agent状态
                    category: '', // 跑批系统
                    os: '' // 操作系统
                },
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                }

            }
        },
        created() {
            this.getRunSysList()
            this.handleLoad()
            this.auth = this.hasPerm(this.$route.path)
            this.maxTableHeight = this.$store.state.common.defaultTableHeight - 52
        },
        methods: {
            // 表格初始化
            handleLoad() {
                this.tableLoading = true
                this.$api.stationState.list({
                    ...this.searchFrom,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }).then(res => {
                    if (res.result) {
                        this.pagination.count = res.data.count
                        this.tableList = res.data.items
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.tableLoading = false
                })
            },
            // 处理表格size切换
            handlePageLimitChange(val) {
                this.pagination.current = 1
                this.pagination.limit = val
                this.handleLoad()
            },
            // 处理页面跳转
            handlePageChange(page) {
                this.pagination.current = page
                this.handleLoad()
            },
            // 处理搜索
            handleSearch() {
                this.pagination.current = 1
                this.handleLoad()
            },
            // 处理打开高级搜索
            handleOpenSeniorSearch() {
                this.isDropdownShow = !this.isDropdownShow
            },
            // 处理搜索重置
            handleReset() {
                this.searchFrom = {
                    name: '', // agent名称
                    ip: '',
                    is_online: '', // agent状态
                    category: '', // 跑批系统
                    os: '' // 操作系统
                }
            },
            // 获取跑批系统
            getRunSysList() {
                this.runSysList = []
            }
        }
    }
</script>

<style lang="scss" scoped>
    #agengtMonitor {
        padding: 20px;
        height: 100%;

        .header {
            float: left;
            width: 100%;
            font-size: 0;
            margin-bottom: 20px;
            // position: relative;

            .senior-search-box {
                background-color: #fff;
                padding: 20px;
                width: 100%;
                margin-top: 20px;
                float: left;
                box-shadow: 0px 4px 8px 0px rgba(0, 0, 0, .1);
                border: 1px solid rgba(0, 0, 0, .2);
            }
        }

        .content {

            .customTable {
                /deep/ .bk-table-pagination-wrapper {
                    background-color: #fff;
                }
                .status-btn {
                    width: 10px;
                    height: 10px;
                    border-radius: 5px;
                    display: inline-block;
                    margin-right: 6px;
                }

                /deep/ .bk-table-empty-block {
                    background-color: #fff;
                }
            }
        }
    }
</style>
