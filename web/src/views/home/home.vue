<template>
    <div id="home">
        <bk-container :margin="0">
            <bk-row class="first-line" v-bkloading="{ isLoading: overViewLoading, zIndex: 10 }">
                <bk-col :span="6">
                    <div class="first-line-box">
                        <div class="first-line-box-left">
                            <div class="num">{{overview_data.today_error_job_num}}</div>
                            <div class="text">当日异常作业数</div>
                        </div>
                        <div class="first-line-box-right">
                            <div class="circle" style="background-color: #FFDDDD;color: #FF5656;"><i class="iconfont icon-mianxingtubiao-shijianzhongxin"></i></div>
                        </div>
                    </div>
                </bk-col>
                <bk-col :span="6">
                    <div class="first-line-box">
                        <div class="first-line-box-left">
                            <div class="num">{{overview_data.today_job_num}}</div>
                            <div class="text">当日作业数</div>
                        </div>
                        <div class="first-line-box-right">
                            <div class="circle" style="background-color: #E1ECFF;color: #3A84FF;"><i class="iconfont icon-mianxingtubiao-dangrizuoyezongshu"></i></div>
                        </div>
                    </div>
                </bk-col>
                <bk-col :span="6">
                    <div class="first-line-box">
                        <div class="first-line-box-left">
                            <div class="num">{{overview_data.today_wait_job_num}}</div>
                            <div class="text">当日未执行作业数</div>
                        </div>
                        <div class="first-line-box-right">
                            <div class="circle" style="background-color: #FFE8C3;color: #FF9C01;"><i class="iconfont icon-mianxingtubiao-zuoyelishi"></i></div>
                        </div>
                    </div>
                </bk-col>
                <bk-col :span="6">
                    <div class="first-line-box">
                        <div class="first-line-box-left">
                            <div class="num">{{overview_data.today_job_flow_num}}</div>
                            <div class="text">当日作业流数</div>
                        </div>
                        <div class="first-line-box-right">
                            <div class="circle" style="background-color: #DCFFE2;color: #45E35F;"><i class="iconfont icon-mianxingtubiao-dangrizuoyeliushu"></i></div>
                        </div>
                    </div>
                </bk-col>
            </bk-row>
            <bk-row class="second-line">
                <bk-col :span="12">
                    <div class="second-line-box" v-bkloading="{ isLoading: todayJobLoading, zIndex: 10 }">
                        <div class="content">
                            <div :id="todayJobId" style="height: 100%;width: 100%;"></div>
                        </div>
                    </div>
                </bk-col>
                <bk-col :span="12">
                    <div class="second-line-box" v-bkloading="{ isLoading: weeklyJobLoading, zIndex: 10 }">
                        <div class="content">
                            <div :id="weeklyJobId" style="height: 100%;width: 100%;"></div>
                        </div>
                    </div>
                </bk-col>
            </bk-row>
            <bk-row class="third-line">
                <bk-col :span="12">
                    <div class="third-line-box" v-bkloading="{ isLoading: top5AgentLoading, zIndex: 10 }">
                        <div class="content">
                            <div :id="top5AgentId" style="height: 100%;width: 100%;"></div>
                        </div>
                    </div>
                </bk-col>
                <bk-col :span="12">
                    <div class="third-line-box" v-bkloading="{ isLoading: jobDynamicLoading, zIndex: 10 }">
                        <div class="header">
                            <p style="color: rgb(60,60,60);margin-left: 5px;">作业管理动态</p>
                            <span @click="handleCheckMore">查看更多</span>
                        </div>
                        <div class="content">
                            <bk-timeline :list="jobDynamicState" ext-cls="custom-timeline">
                            </bk-timeline>
                        </div>
                    </div>
                </bk-col>
            </bk-row>
        </bk-container>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                statusList1: [{
                                  tag: 'pony审批通过，并附“同意”',
                                  content: '<span class="timeline-update-time">2020-03-06 11:23</span>',
                                  color: 'green',
                                  filled: true
                              },
                              {
                                  tag: 'tony审批通过，并附“同意”',
                                  content: '<span class="timeline-update-time">2020-03-07 10:20</span>',
                                  color: 'green',
                                  filled: true
                              },
                              {
                                  tag: 'allen正在审批',
                                  color: 'green',
                                  filled: true,
                                  content: '<span class="timeline-update-time">2020-03-06 11:23</span>'
                              },
                              {
                                  tag: '等待mark审批',
                                  color: 'green',
                                  filled: true,
                                  content: '<span class="timeline-update-time">2020-03-06 11:23</span>'
                              },
                              {
                                  tag: '等待mark审批',
                                  color: 'green',
                                  filled: true,
                                  content: '<span class="timeline-update-time">2020-03-06 11:23</span>'
                              }
                ],
                overViewLoading: false,
                todayJobLoading: false,
                top5AgentLoading: false,
                weeklyJobLoading: false,
                jobDynamicLoading: false,
                jobDynamicState: [],
                weeklyJobChart: null,
                top5AgentChart: null,
                todayJobChart: null,
                weeklyJob: {
                    weekly_time: [],
                    weekly_job_num: [],
                    weekly_error_job_num: []
                },
                todayJob: {
                    finished_job_num: [],
                    error_job_num: [],
                    unfinished_job_num: [],
                    time_line: []
                },
                top5Agent: {
                    top5_agent_name: [],
                    top5_agent_num: []
                },
                overview_data: {
                    today_wait_job_num: 0, // 当日为执行作业数
                    today_job_num: 0, // 当日作业数
                    today_job_flow_num: 0, // 当日作业流数
                    today_error_job_num: 0, // 当日异常作业数
                    jobDynamicState: []
                }
            }
        },
        computed: {
            weeklyJobId() {
                return 'weeklyJobId' + this._uid
            },
            top5AgentId() {
                return 'top5AgentId' + this._uid
            },
            todayJobId() {
                return 'todayJobId' + this._uid
            }
        },
        mounted() {
            this.getWeeklyJob()
            this.getTop5Agent()
            this.getTodayJob()
            this.getJobtTrend()
            const _this = this
            const elementResizeDetectorMaker = require('element-resize-detector') // 导入element-resize-detector，为了使线图饼图自适应左侧菜单栏缩放后的大小
            // 创建实例
            const erd = elementResizeDetectorMaker()
            // 监听id为home的元素 大小变化
            this.$nextTick(() => {
                erd.listenTo(document.getElementById('home'), function(element) {
                    _this.weeklyJobChart.resize()
                    _this.top5AgentChart.resize()
                    _this.todayJobChart.resize()
                })
            })
        },
        created() {
            this.getOverViewData()
        },
        methods: {
            // 处理查看更多
            handleCheckMore() {
                this.$router.push({
                    path: '/log',
                    query: {
                        object_repr: '作业',
                        log: 'fromHome'
                    }
                })
            },
            // 获取头部预览数据
            getOverViewData() {
                this.overViewLoading = true
                this.$api.home.overview().then(res => {
                    if (res.result) {
                        this.overview_data = res.data
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.overViewLoading = false
                })
            },
            // 获取近七天作业执行情况
            getWeeklyJob() {
                this.weeklyJobLoading = true
                this.weeklyJobChart = this.$echarts.init(document.getElementById(this.weeklyJobId))
                const option = {
                    color: ['#3A84FF', '#FF5656'],
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    title: {
                        text: '近七天作业执行情况'
                    },
                    legend: {
                        x: '15',
                        y: 'top',
                        top: '13%',
                        data: ['作业总数', '异常作业数'],
                        textStyle: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        }
                    },
                    grid: {
                        height: 210,
                        width: '98%',
                        left: '20px',
                        right: '0px',
                        bottom: '40px',
                        containLabel: true
                    },
                    toolbox: {
                        feature: {
                            saveAsImage: {
                                show: true,
                                // icon: 'M158.496 503.584c3.712 0 6.816 2.592 7.648 6.08l0.192 1.792v334.368h691.328v-334.4c0-3.68 2.56-6.816 6.08-7.616l1.76-0.224h53.376c3.744 0 6.848 2.592 7.68 6.08l0.192 1.792v372.032a31.392 31.392 0 0 1-27.744 31.2l-3.68 0.192H128.672a31.392 31.392 0 0 1-31.2-27.712l-0.224-3.68V511.456c0-3.712 2.592-6.848 6.08-7.68l1.792-0.192h53.376zM537.888 109.12c3.712 0 6.816 2.56 7.648 6.048l0.192 1.792V695.04l175.776-146.88a7.872 7.872 0 0 1 9.504 0.48l1.408 1.536 30.176 44.032a7.84 7.84 0 0 1-0.48 9.504l-1.568 1.408-244.96 194.304a7.84 7.84 0 0 1-7.2 0.896l-1.728-0.896-243.2-194.336a7.84 7.84 0 0 1-2.976-9.056l0.96-1.856 30.272-43.936a7.872 7.872 0 0 1 9.056-2.944l1.888 0.96 174.016 146.56V116.928c0-3.712 2.56-6.816 6.016-7.648l1.824-0.192h53.376z',
                                // iconStyle: {
                                //    color: '#bfbfbf'
                                // },
                                emphasis: {
                                    iconStyle: {
                                        textFill: '#fff'
                                    }
                                }
                            }
                        }
                    },
                    calculable: true,
                    xAxis: [{
                        type: 'category',
                        axisTick: {
                            show: false
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#DCDEE5'
                            }
                        },
                        axisLabel: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        },
                        data: this.weeklyJob.weekly_time
                    }],
                    yAxis: [{
                        type: 'value',
                        axisLine: { // y轴
                            show: false
                        },
                        axisTick: {
                            show: false
                        },
                        splitLine: {
                            lineStyle: {
                                color: '#F0F1F5'
                            }
                        },
                        min: 0,
                        minInterval: 1,
                        axisLabel: {
                            formatter: '{value}',
                            color: 'rgba(0, 0, 0, 0.45)'
                        }
                    }],
                    series: [{
                                 name: '作业总数',
                                 type: 'bar',
                                 barWidth: 24,
                                 label: '1222',
                                 data: this.weeklyJob.weekly_job_num
                                 // data: [2, 10, 30, 7, 6, 0]
                             },
                             {
                                 name: '异常作业数',
                                 type: 'bar',
                                 barGap: '20%',
                                 barWidth: 24,
                                 label: '2333',
                                 data: this.weeklyJob.weekly_error_job_num
                             }
                    ]
                }
                this.$api.home.weekly_job().then(res => {
                    if (res.result) {
                        this.weeklyJob = res.data
                        option.xAxis[0].data = this.weeklyJob.weekly_time
                        option.series[0].data = this.weeklyJob.weekly_job_num
                        option.series[1].data = this.weeklyJob.weekly_error_job_num
                        this.drawline(this.weeklyJobChart, option)
                    } else {
                        this.$cwMessage(res.message, 'error')
                        this.drawline(this.weeklyJobChart, option)
                    }
                    this.weeklyJobLoading = false
                })
            },
            // 获取日均作业top5的agent
            getTop5Agent() {
                this.top5AgentLoading = true
                this.top5AgentChart = this.$echarts.init(document.getElementById(this.top5AgentId))
                const option = {
                    color: ['#3A84FF'],
                    xAxis: {
                        type: 'category',
                        data: this.top5Agent.top5_agent_name,
                        axisTick: {
                            show: false
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#DCDEE5'
                            }
                        },
                        axisLabel: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        }
                    },
                    legend: {
                        data: []
                    },
                    title: {
                        text: '日均作业Top5的Agent'
                    },
                    grid: {
                        height: 210,
                        width: '100%',
                        left: '20px',
                        bottom: '30px',
                        containLabel: true
                    },
                    toolbox: {
                        feature: {
                            saveAsImage: {
                                show: true,
                                emphasis: {
                                    iconStyle: {
                                        textFill: '#fff'
                                    }
                                }
                            }
                        }
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    yAxis: {
                        type: 'value',
                        axisLine: { // y轴
                            show: false
                        },
                        axisTick: {
                            show: false
                        },
                        splitLine: {
                            lineStyle: {
                                color: '#F0F1F5'
                            }
                        },
                        name: '日均作业数',
                        nameTextStyle: {
                            color: '#63656E'
                        },
                        min: 0,
                        minInterval: 1,
                        axisLabel: {
                            formatter: '{value}',
                            color: 'rgba(0, 0, 0, 0.45)'
                        }
                    },
                    series: [{
                        data: this.top5Agent.top5_agent_num,
                        barWidth: 24,
                        type: 'bar'
                    }]
                }
                this.$api.home.top5_agent().then(res => {
                    if (res.result) {
                        this.top5Agent.top5_agent_name = res.data.top5_agent_name
                        this.top5Agent.top5_agent_num = res.data.top5_agent_num
                        // option.xAxis[0].data = this.top5Agent.top5_agent_name
                        option.xAxis.data = this.top5Agent.top5_agent_name
                        option.series[0].data = this.top5Agent.top5_agent_num
                        this.drawline(this.top5AgentChart, option)
                    } else {
                        this.$cwMessage(res.message, 'error')
                        this.drawline(this.top5AgentChart, option)
                    }
                    this.top5AgentLoading = false
                })
            },
            // 获取当日作业执行情况
            getTodayJob() {
                this.todayJobLoading = true
                this.todayJobChart = this.$echarts.init(document.getElementById(this.todayJobId))
                // 当日作业执行情况
                const option = {
                    color: ['#45E35F', '#FF9C01', '#FF5656'],
                    tooltip: {
                        trigger: 'axis',
                        // formatter: '{b0}<br/>{a0}: {c0}<br />{a1}: {c1}<br />{a2}: {c2}',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    title: {
                        text: '当日作业执行情况'
                    },
                    grid: {
                        height: 190,
                        width: '100%',
                        left: '40px',
                        bottom: '60px'
                    },
                    toolbox: {
                        feature: {
                            saveAsImage: {
                                show: true,
                                emphasis: {
                                    iconStyle: {
                                        textFill: '#fff'
                                    }
                                }
                            }
                        }
                    },
                    legend: {
                        x: '10',
                        y: 'top',
                        top: '15%',
                        data: ['已完成的作业总数', '待完成的作业总数', '异常作业总数'],
                        textStyle: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        }
                    },
                    xAxis: [{
                        type: 'category',
                        axisTick: {
                            show: false
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#DCDEE5'
                            }
                        },
                        axisLabel: {
                            color: 'rgba(0, 0, 0, 0.45)'
                        },
                        data: this.todayJob.time_line
                    }],
                    yAxis: [{
                        type: 'value',
                        axisLine: { // y轴
                            show: false
                        },
                        axisTick: {
                            show: false
                        },
                        splitLine: {
                            lineStyle: {
                                color: '#F0F1F5'
                            }
                        },
                        min: 0,
                        axisLabel: {
                            formatter: '{value}',
                            color: 'rgba(0, 0, 0, 0.45)'
                        }
                    }],
                    series: [{
                                 name: '已完成的作业总数',
                                 type: 'line',
                                 data: this.todayJob.finished_job_num
                             },
                             {
                                 name: '待完成的作业总数',
                                 type: 'line',
                                 barWidth: 30,
                                 data: this.todayJob.unfinished_job_num
                             },
                             {
                                 name: '异常作业总数',
                                 type: 'line',
                                 data: this.todayJob.error_job_num
                             }
                    ]
                }
                this.$api.home.today_job().then(res => {
                    if (res.result) {
                        this.todayJob.finished_job_num = res.data.finished_job_num
                        this.todayJob.error_job_num = res.data.error_job_num
                        this.todayJob.unfinished_job_num = res.data.unfinished_job_num
                        this.todayJob.time_line = res.data.time_line
                        option.series[0].data = this.todayJob.finished_job_num
                        option.series[1].data = this.todayJob.unfinished_job_num
                        option.series[2].data = this.todayJob.error_job_num
                        option.xAxis[0].data = this.todayJob.time_line
                        this.drawline(this.todayJobChart, option)
                    } else {
                        this.$cwMessage(res.message, 'error')
                        this.drawline(this.todayJobChart, option)
                    }
                    this.todayJobLoading = false
                })
            },
            // 获取作业管理动态
            getJobtTrend() {
                this.jobDynamicLoading = true
                this.$api.home.job_dynamic().then(res => {
                    if (res.result) {
                        const data = res.data.slice(0, 4)
                        this.jobDynamicState = data.map(item => {
                            return {
                                tag: item.condition,
                                color: 'green',
                                filled: true,
                                content: `<span class="timeline-update-time">${item.finish_time}</span>`

                            }
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.jobDynamicLoading = false
                })
            },
            drawline(obj, option) {
                obj.setOption(option)
            }
        }
    }
</script>

<style scoped lang="scss">
    #home {
        padding: 20px;
        height: 100%;

        .first-line {
            .first-line-box {
                height: 96px;
                border-radius: 2px;
                background-color: #fff;
                padding: 16px 24px 20px 24px;
                box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.1);
                display: flex;

                &:hover {
                    box-shadow: 0px 4px 12px 0px rgba(0, 0, 0, 0.08);
                }

                .first-line-box-left {
                    width: 60%;

                    .num {
                        font-size: 24px;
                        color: #313238;
                    }

                    .text {
                        font-size: 14px;
                        color: #979BA5;
                    }
                }

                .first-line-box-right {
                    position: relative;
                    width: 40%;

                    .circle {
                        position: absolute;
                        right: 0;
                        height: 56px;
                        width: 56px;
                        border-radius: 28px;

                        i {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            font-size: 32px;
                            transform: translate(-50%, -50%);
                        }
                    }
                }
            }
        }

        .second-line {
            margin-top: 16px;

            .second-line-box {
                padding: 16px 20px 0 20px;
                height: 356px;
                background: #FFFFFF;
                border-radius: 2px;
                box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.1);

                &:hover {
                    box-shadow: 0px 4px 12px 0px rgba(0, 0, 0, 0.08);
                }

                .content {
                    height: 340px;
                    width: 100%;
                }
            }
        }

        .third-line {
            margin-top: 16px;

            .third-line-box {
                padding: 16px 20px 0 20px;
                height: 356px;
                background: #FFFFFF;
                border-radius: 2px;
                box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.1);

                &:hover {
                    box-shadow: 0px 4px 12px 0px rgba(0, 0, 0, 0.08);
                }

                .header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;

                    p {
                        font-size: 18px;
                        font-weight: bold;
                    }

                    span {
                        cursor: pointer;
                        color: #3A84FF;
                        font-size: 12px;
                    }
                }

                .content {
                    height: 340px;
                    width: 100%;
                    overflow: hidden;

                    .custom-timeline {
                        margin-left: 15px;

                        /deep/ li {
                            padding-bottom: 10px;

                            .timeline-update-time {
                                font-size: 12px;
                                color: #979BA5;
                            }
                        }
                    }
                }
            }
        }
    }
</style>
