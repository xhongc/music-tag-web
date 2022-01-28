<template>
    <div id="jobViewReport">
        <div class="search-header">
            <div class="search-item" style="width: 20%;">
                <span style="flex-basis: 60px;">跑批系统</span>
                <bk-select :clearable="true" style="background-color: #fff;flex: 1;" placeholder="请选择"
                    v-model="searchForm.category" @change="handleRunIdChaneg" :title="searchForm.category">
                    <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id" :name="item.name">
                    </bk-option>
                </bk-select>
            </div>
            <div class="search-item" style="width: 20%;">
                <span style="flex-basis: 60px;">作业名称</span>
                <bk-select :clearable="true" style="background-color: #fff;flex: 1;" placeholder="请选择" searchable
                    v-model="searchForm.name" :title="searchForm.name">
                    <bk-option v-for="(item, index) in jobNameList" :key="index" :id="item" :name="item"
                        v-if="jobNameShow">
                    </bk-option>
                </bk-select>
            </div>
            <div class="search-item" style="width: 38%;">
                <span style="flex-basis: 60px;">时间范围</span>
                <bk-date-picker :placeholder="'选择日期时间'" :type="'datetimerange'" format="yyyy-MM-dd HH:mm:ss"
                    style="flex: 1;" :transfer="true" :value="searchForm.timeRange"
                    @change="handleTimeRangeChange" :title="searchForm.timeRange"></bk-date-picker>
            </div>
            <div class="search-item" style="width: 12%;">
                <bk-button style="margin-right: 12px;" theme="primary" @click="handleSearch">查询</bk-button>
                <bk-button @click="handleReset">重置</bk-button>
            </div>
            <!--            <bk-form form-type="inline" ext-cls="custom-form">
                <bk-form-item label="跑批系统">
                    <bk-select :clearable="true" style="background-color: #fff;width: 240px;" placeholder="请选择"
                        v-model="searchForm.category" @change="handleRunIdChaneg">
                        <bk-option v-for="(item, index) in runSysList" :key="index" :id="item.id" :name="item.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="作业名称" style="margin-left: 12px;">
                    <bk-select :clearable="true" style="background-color: #fff;width: 240px;" placeholder="请选择"
                        searchable v-model="searchForm.name">
                        <bk-option v-for="(item, index) in jobNameList" :key="index" :id="item" :name="item"
                            v-if="jobNameShow">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="时间范围" style="margin-left: 12px;">
                    <bk-date-picker :placeholder="'选择日期时间'" :type="'datetimerange'" format="yyyy-MM-dd HH:mm:ss"
                        style="width: 300px;" :transfer="true" :value="searchForm.timeRange"
                        @change="handleTimeRangeChange"></bk-date-picker>
                </bk-form-item>
                <bk-form-item style="margin-left: 12px;">
                    <bk-button style="margin-right: 8px;" theme="primary" @click="handleSearch">查询</bk-button>
                    <bk-button @click="handleReset">重置</bk-button>
                </bk-form-item>
            </bk-form> -->
        </div>
        <div class="chart1" v-bkloading="{ isLoading: chart1Loading, zIndex: 99 }">
            <div class="title">作业执行情况分析图</div>
            <div class="chart-name">
                <span>作业数（个）</span>
                <span>作业成功率 (%) </span>
            </div>
            <div :id="jobReportChart1Id" style="height: 290px;margin-top: 20px;"></div>
        </div>
        <div style="height: 1px;width: 100%;background-color: #e8eaec;margin-top: 22px;"></div>
        <!-- <bk-divider style="border-color: #e8eaec;margin-top: 25px;"></bk-divider> -->
        <div class="chart2" v-bkloading="{ isLoading: chart2Loading, zIndex: 99 }">
            <div class="title">作业性能分析图</div>
            <div class="chart-name">
                <span>作业执行时间（秒）</span>
            </div>
            <div :id="jobReportChart2Id" style="height: 290px;margin-top: 20px;"></div>
        </div>
    </div>
</template>

<script>
    import $ from 'jquery'
    export default {
        props: {
            runSysList: {
                type: Array,
                default: []
            }
        },
        data() {
            return {
                midJobName: '所有作业',
                jobNameShow: true,
                searchForm: {
                    category: '', // 跑批id
                    name: '', // 作业流名称
                    timeRange: ['', ''] // 时间范围
                },
                jobNameList: [],
                chart1Loading: false,
                chart2Loading: false,
                chart1: null,
                chart2: null,
                chart1Option: {},
                chart2Option: {}
            }
        },
        computed: {
            jobReportChart1Id() {
                return 'jobReportChart1' + this._uid
            },
            jobReportChart2Id() {
                return 'jobReportChart2' + this._uid
            }
        },
        created() {
            this.getJobName()
        },
        mounted() {
            this.initChart()
        },
        methods: {
            // 跑批系统改变
            handleRunIdChaneg() {
                this.searchForm.name = ''
                this.getJobName()
            },
            // 获取作业下拉列表
            getJobName() {
                this.jobNameShow = false
                this.jobNameList = []
                this.$api.processReport.getJobName({
                    category: this.searchForm.category
                }).then(res => {
                    if (res.result) {
                        this.jobNameList = res.data
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.jobNameShow = true
                })
            },
            // 时间范围格式转换
            handleTimeRangeChange(e) {
                this.searchForm.timeRange = e
            },
            // 处理初始化报表
            initChart() {
                this.chart1 = this.$echarts.init(document.getElementById(this.jobReportChart1Id))
                this.chart2 = this.$echarts.init(document.getElementById(this.jobReportChart2Id))
                this.chart1Option = this.getChart1Option()
                this.chart2Option = this.getChart2Option()
                this.handleLoad()
                this.handleChartResize()
            },
            // 获取报表数据
            handleLoad() {
                this.chart1Loading = true
                this.chart2Loading = true
                const params = {
                    name: this.searchForm.name,
                    category: this.searchForm.category,
                    time_gte: this.searchForm.timeRange[0],
                    time_lte: this.searchForm.timeRange[1]
                }
                this.$api.processReport.getJobReport(params).then(res => {
                    if (res.result) {
                        const chart1Data = res.data.execute_data
                        const chart2Data = res.data.performance_data
                        this.handleRenderChart1(chart1Data)
                        this.handleRenderChart2(chart2Data)
                        this.mainLoading = false
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.chart1Loading = false
                    this.chart2Loading = false
                })
            },
            handleRenderChart1(chart1Data) {
                this.chart1Loading = true
                this.chart1Option.xAxis[0].data = chart1Data.date // chart1时间x轴
                this.chart1Option.series[0].data = chart1Data.day_content_count // chart1作业总数
                this.chart1Option.series[1].data = chart1Data.day_success_content_count // chart1成功作业数
                this.chart1Option.series[2].data = chart1Data.day_error_content_count // chart1异常作业数
                this.chart1Option.series[3].data = chart1Data.day_confirm_content_count // chart1人工复核作业数
                this.chart1Option.series[4].data = chart1Data.day_rerun_content_count // chart1重执行作业数
                this.chart1Option.series[5].data = chart1Data.day_content_success_rate // chart1作业执行成功率
                const max = this.cal_Max([...chart1Data.day_content_count, ...chart1Data.day_success_content_count, ...chart1Data.day_error_content_count, ...chart1Data.day_confirm_content_count, ...chart1Data
                    .day_rerun_content_count
                ])
                this.chart1Option.yAxis[0].max = (parseInt(max / 50) + 1) * 50
                this.chart1Option.yAxis[0].interval = (parseInt(max / 50) + 1) * 10
                this.chart1Option && this.chart1.setOption(this.chart1Option)
                this.chart1Loading = false
            },
            handleRenderChart2(chart2Data) {
                this.chart2Loading = true
                this.chart2Option.xAxis[0].data = chart2Data.date // chart2时间x轴
                this.chart2Option.series[0].data = chart2Data.day_avg_time // chart2单日平均耗时
                this.chart2Option.series[1].data = chart2Data.week_avg_time // chart2 单周平均耗时
                // const max = this.cal_Max([...chart2Data.day_avg_time, ...chart2Data.week_avg_time])
                // this.chart2Option.yAxis.max = max + 100000
                // this.chart2Option.yAxis.interval = (max + 100000) / 5
                this.chart2Option && this.chart2.setOption(this.chart2Option)
                this.chart2Loading = false
            },
            // 计算最大值
            cal_Max(a) {
                // debugger
                a = $.grep(a, function(n, i) {
                    return i > 0
                })
                const maxval = Math.max.apply(null, a)
                return maxval
            },
            // 获取报表1配置
            getChart1Option() {
                const _this = this
                const option = {
                    color: ['#5C9DF8', '#60C976', '#EC7471', '#FF9D4D', '#F5D162', '#A9D372'],
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow',
                            z: 10,
                            shadowStyle: {
                                color: '#E1ECFF',
                                opacity: 0.8
                            }
                        },
                        textStyle: {
                            color: '#63656E'
                        },
                        formatter: function(params, ticket, callback) {
                            let htmlStr = '' + '<strong>' + _this.midJobName + '</strong>' + '<br/>'
                            for (let i = 0; i < params.length; i++) {
                                const param = params[i]
                                const xName = param.name // x轴的名称
                                const seriesName = param.seriesName // 图例名称
                                const value = param.value // y轴值
                                const color = param.color // 图例颜色

                                if (i === 0) {
                                    htmlStr += xName + '<br/>' // x轴的名称
                                }
                                htmlStr += '<div style="font-size: 12px;">'
                                // 为了保证和原来的效果一样，这里自己实现了一个点的效果
                                htmlStr += '<div style="margin-top: 6px;">' +
                                    '<span style="margin-right:10px;display:inline-block;width:10px;height:10px;border-radius:5px;background-color:' +
                                    color + ';"></span>'
                                // 圆点后面显示的文本
                                htmlStr += seriesName + '：' + value + (seriesName === '作业执行成功率' ? '%' : '') +
                                    '</div>'
                                htmlStr += '</div>'
                            }
                            return htmlStr
                        }
                    },
                    // legend: [{
                    //     data: ['作业总数', '成功作业', '异常作业', '人工复核作业', '重执行作业'],
                    //     bottom: 'bottom',
                    //     right: '40%',
                    //     itemWidth: 12,
                    //     itemHeight: 12,
                    //     textStyle: {
                    //         color: '#979BA5'
                    //     }
                    // }, {
                    //     data: ['作业执行成功率'],
                    //     itemHeight: 12,
                    //     right: '32%',
                    //     bottom: 'bottom',
                    //     textStyle: {
                    //         color: '#979BA5'
                    //     }
                    // }],
                    legend: {
                        data: ['作业总数', '成功作业', '异常作业', '人工复核作业', '重执行作业', {
                            name: '作业执行成功率',
                            itemWidth: 10
                        }],
                        bottom: 'bottom',
                        // itemWidth: 12,
                        itemHeight: 12,
                        textStyle: {
                            color: '#979BA5'
                        }
                    },
                    grid: {
                        left: 0,
                        right: '1%',
                        bottom: '15%',
                        top: '19%',
                        containLabel: true
                    },
                    xAxis: [{
                        type: 'category',
                        data: [],
                        axisTick: {
                            show: false
                        },
                        axisLabel: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#DCDEE5'
                            }
                        }
                    }],
                    yAxis: [{
                                type: 'value',
                                // name: '作业数（个）',
                                // nameTextStyle: {
                                //     padding: [0, 0, 20, 0],
                                //     color: '#979BA5'
                                // },
                                min: 0,
                                // max: 200,
                                splitNumber: 5,
                                // interval: 40,
                                axisLabel: {
                                    formatter: '{value}',
                                    color: '#979BA5'
                                }
                            },
                            {
                                type: 'value',
                                // name: '作业成功率（%）',
                                // nameTextStyle: {
                                //     padding: [0, 0, 20, 0],
                                //     color: '#979BA5'
                                // },
                                min: 0,
                                max: 100,
                                splitNumber: 5,
                                interval: 20,
                                axisLabel: {
                                    formatter: '{value}',
                                    color: '#979BA5'
                                }
                            }
                    ],
                    series: [{
                                 name: '作业总数',
                                 type: 'bar',
                                 data: [],
                                 z: 20
                             },
                             {
                                 name: '成功作业',
                                 type: 'bar',
                                 data: [],
                                 z: 20
                             },
                             {
                                 name: '异常作业',
                                 type: 'bar',
                                 data: [],
                                 z: 20
                             },
                             {
                                 name: '人工复核作业',
                                 type: 'bar',
                                 data: [],
                                 z: 20
                             },
                             {
                                 name: '重执行作业',
                                 type: 'bar',
                                 data: [],
                                 z: 20
                             },
                             {
                                 name: '作业执行成功率',
                                 type: 'line',
                                 yAxisIndex: 1,
                                 data: [],
                                 z: 20
                             }
                    ]
                }
                return option
            },
            // 获取报表2配置
            getChart2Option() {
                const _this = this
                const option = {
                    color: ['#5C9DF8', '#60C976'],
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow',
                            z: 10,
                            shadowStyle: {
                                color: '#E1ECFF',
                                opacity: 0.8
                            }
                        },
                        textStyle: {
                            color: '#63656E'
                        },
                        formatter: function(params, ticket, callback) {
                            let htmlStr = '' + '<strong>' + _this.midJobName + '</strong>' + '<br/>'
                            for (let i = 0; i < params.length; i++) {
                                const param = params[i]
                                const xName = param.name // x轴的名称
                                const seriesName = param.seriesName // 图例名称
                                const value = param.value // y轴值
                                const color = param.color // 图例颜色
                                if (i === 0) {
                                    htmlStr += xName + '<br/>' // x轴的名称
                                }
                                htmlStr += '<div style="font-size: 12px;">'
                                // 为了保证和原来的效果一样，这里自己实现了一个点的效果
                                htmlStr += '<div style="margin-top: 6px;">' +
                                    '<span style="margin-right:10px;display:inline-block;width:10px;height:10px;border-radius:5px;background-color:' +
                                    color + ';"></span>'
                                // 圆点后面显示的文本
                                htmlStr += seriesName + '：' + value + '</div>'
                                htmlStr += '</div>'
                            }
                            return htmlStr
                        }
                    },
                    legend: {
                        data: ['单日平均耗时', '前七天平均耗时'],
                        bottom: 'bottom',
                        textStyle: {
                            color: '#979BA5'
                        }
                    },
                    grid: {
                        left: 0,
                        right: 10,
                        bottom: '15%',
                        top: '19%',
                        containLabel: true
                    },
                    xAxis: [{
                        type: 'category',
                        data: [],
                        axisTick: {
                            show: false
                        },
                        axisLabel: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#DCDEE5'
                            }
                        }
                    }],
                    yAxis: {
                        type: 'value',
                        // name: '作业执行时间（秒）',
                        // // interval: 1000,
                        // nameTextStyle: {
                        //     padding: [0, 0, 20, 0],
                        //     color: '#979BA5'
                        // },
                        splitNumber: 5,
                        min: 0,
                        axisLabel: {
                            formatter: '{value}',
                            color: '#979BA5'
                        }
                    },
                    series: [{
                                 name: '单日平均耗时',
                                 type: 'line',
                                 data: [],
                                 z: 20
                             },
                             {
                                 name: '前七天平均耗时',
                                 type: 'line',
                                 data: [],
                                 z: 20
                             }
                    ]
                }
                return option
            },
            // 处理报表元素大小变化重绘
            handleChartResize() {
                const _this = this
                this.$nextTick(() => {
                    const elementResizeDetectorMaker = require(
                        'element-resize-detector'
                    ) // 导入element-resize-detector，为了使线图饼图自适应左侧菜单栏缩放后的大小
                    // 创建实例
                    const erd = elementResizeDetectorMaker()
                    // 监听元素 大小变化
                    erd.listenTo(document.getElementById('jobViewReport'), function(element) {
                        _this.chart1.resize()
                        _this.chart2.resize()
                    })
                })
            },
            // 处理查询
            handleSearch() {
                if (this.searchForm.name === '') {
                    this.midJobName = '所有作业'
                } else {
                    this.midJobName = this.searchForm.name
                }
                this.handleLoad()
            },
            // 处理重置
            handleReset() {
                this.searchForm = {
                    category: '', // 跑批id
                    name: '', // 作业流名称
                    timeRange: ['', ''] // 时间范围
                }
            }
        }
    }
</script>

<style scoped lang="scss">
    #jobViewReport {
        .search-header {
            display: flex;
            // .custom-form {
            //     /deep/ .bk-label {
            //         padding: 0 8px 0 0;
            //     }
            // }

            .search-item {
                display: flex;
                margin-right: 16px;

                span {
                    display: inline-block;
                    height: 32px;
                    line-height: 32px;
                    font-size: 14px;
                    margin-right: 8px;
                }
            }
        }

        .chart1 {
            height: 325px;
            margin-top: 25px;
            position: relative;

            .chart-name {
                color: #979BA5;
                display: flex;
                justify-content: space-between;
                position: absolute;
                font-size: 14px;
                top: 45px;
                width: 100%;
            }

            .title {
                width: 160px;
                height: 21px;
                font-size: 16px;
                font-weight: bold;
                color: #313238;
                line-height: 21px;
            }
        }

        .chart2 {
            height: 325px;
            margin-top: 25px;
            position: relative;

            .chart-name {
                color: #979BA5;
                display: flex;
                justify-content: space-between;
                position: absolute;
                font-size: 14px;
                top: 45px;
                width: 100%;
            }

            .title {
                width: 160px;
                height: 21px;
                font-size: 16px;
                font-weight: bold;
                color: #313238;
                line-height: 21px;
            }
        }
    }
</style>
