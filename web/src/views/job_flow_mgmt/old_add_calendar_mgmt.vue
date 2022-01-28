<template>
    <div id="ces">
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }" class="mgmtForm">
            <bk-form :label-width="100" :model="form" ref="form" :rules="rules">
                <bk-form-item label="日历名" :required="true" :property="'name'">
                    <div class="upload-wrap">
                        <bk-input :disabled="isDetail" ext-cls="ca-input" v-model="form.name" placeholder="请输入日历名称"></bk-input>
                        <input id="uploadFile" style="display: none" @change="uploadFile()" type="file" accept=".xls,.xlsx" />
                        <bk-button theme="primary" class="upload-button" @click="handleChooseFile">导入</bk-button>
                        <span v-bk-tooltips="baseUsage.bottom" class="bottom-middle">
                            <i class="bk-icon icon-info-circle-shape" style="font-size: 16px;color: #979BA5;"></i>
                        </span>
                        <span class="down-wrap" @click="down">下载示例文件</span>
                    </div>
                </bk-form-item>
                <bk-form-item label="描述">
                    <bk-input :disabled="isDetail" ext-cls="des-input" v-model="form.description" placeholder="请输入描述"></bk-input>
                </bk-form-item>
                <bk-form-item label="已选年份">
                    <Tag v-for="(item, index) in selectedYearList" :id="generateId(index)" size="medium" :key="item"
                        :name="item" @on-change="chooseTag(item)" checkable :closable="closable" @on-close="handleClose(item)"
                        :checked="item === targetYear ? true : false" :color="item === targetYear ? '#3a84ff' : ''" style="border: 0;">{{ item }}
                    </Tag>
                </bk-form-item>
                <bk-form-item label="快速设置">
                    <bk-checkbox :value="holidayState" @change="selectHolidaysAndFestivals" :disabled="isDetail" style="margin-right: 16px;">
                        周末
                    </bk-checkbox>
                    <bk-checkbox :value="workState" @change="selectWorkDays" :disabled="isDetail">工作日</bk-checkbox>
                </bk-form-item>
                <bk-form-item label="日历设置">
                    <div class="cesCal">
                        <Calendar ref="myChild" :set-calendar="datas" @syndata="synData"></Calendar>
                        <div style="z-index: 20;display: inline-block">
                            <div @click="yearMinus" class="pre-button">
                                <bk-icon type="angle-left" />
                            </div>
                            <bk-input class="middle-input" size="small" :disabled="isDetail" clearable placeholder="跳转至"
                                @on-enter="jumpTo" v-model="targetYear" />
                            <div @click="yearPlus" class="next-button">
                                <bk-icon type="angle-right" />
                            </div>
                        </div>
                    </div>
                </bk-form-item>
                <bk-form-item>
                    <bk-button v-if="!isDetail" @click="confirm" theme="primary">确定
                    </bk-button>
                    <bk-button :class="{ 'MarginLeft18px': !isDetail }" @click="cancel">
                        <span v-if="!isDetail">取消</span>
                        <span v-if="isDetail">返回</span>
                    </bk-button>
                </bk-form-item>
            </bk-form>
        </div>
    </div>
</template>

<script>
    import $ from 'jquery'
    import Calendar from '@/components/FullYearCalendar/calendar'
    import {
        acquireWorkAndHolidays
    } from '@/components/FullYearCalendar/work_holiday_compute'

    export default {
        name: 'add-calendar-mgmt',
        components: {
            Calendar
        },
        data() {
            return {
                datas: {
                    disable: false,
                    year: this.customYear,
                    initDate: [],
                    format: 'YYYY-MM-DD'
                },
                closable: true,
                isDetail: false,
                beforeroute: true,
                isEdit: false,
                loading: false,
                rules: {
                    name: [{
                        required: true
                    }],
                    description: [{
                        required: true
                    }],
                    date: [{
                        required: true
                    }]
                },
                form: {
                    description: '',
                    name: '',
                    date: []
                },
                targetYear: '',
                customYear: 2021,
                selectedYearList: [],
                finalYearData: {},
                show: true,
                newFinalYearData: {},
                importCalendarData: [],
                workDays: [],
                holidaysAndFestivals: [],
                requestData: [],
                earlyIndex: '',
                partOfDays: [],
                holidayState: false,
                workState: false,
                watchChildData: [],
                isChange: false,
                baseUsage: {
                    bottom: {
                        content: '上传的文件只能是xls以及xlsx格式',
                        showOnInit: false,
                        placements: ['bottom']
                    }
                },
                duplicatedDays: {}
            }
        },
        watch: {
            'watchChildData': function() {
                this.isChange = true
            }
        },
        created() {
            this.dataSet()
        },
        mounted() {
            this.targetYear = ''
            if (this.$route.params.form && this.$route.params.form.date) {
                this.finalYearData = this.$route.params.form.date
            }
            this.selectedYearList = Object.keys(this.finalYearData)
            if (Object.keys(this.finalYearData)) {
                const nowYear = Object.keys(this.finalYearData)[0]
                this.customYear = nowYear
                this.targetYear = nowYear
                this.dataSet()
            }
            if (this.$route.params.isDetail) {
                $('.cesCal').css('pointer-events', 'none')
                this.closable = false
                this.workState = this.form.quick.work
                this.holidayState = this.form.quick.holiday
            }
            if (this.$route.params.isEdit) {
                this.workState = this.form.quick.work
                this.holidayState = this.form.quick.holiday
            }
        },
        methods: {
            handleChooseFile() {
                document.getElementById('uploadFile').value = ''
                document.getElementById('uploadFile').click()
            },
            // 导入日历
            uploadFile() {
                const file = document.getElementById('uploadFile').files[0]
                const formData = new FormData()
                formData.append('file', file)
                formData.append('fileName', file.name)
                this.$api.calendar.post_calendar_file(formData).then(res => {
                    if (res.result) {
                        const importedCalendar = res.data
                        this.requestData = importedCalendar
                        const flatten = arr => {
                            return arr.reduce((a, b) => {
                                return a.concat(b)
                            }, [])
                        }
                        // 处理导入的Excel表格数据
                        const dataArr = flatten(Object.values(importedCalendar.date_dict))
                        importedCalendar.add_date_list.forEach(item => {
                            if (!dataArr.includes(item)) {
                                dataArr.push(item)
                            }
                        })
                        importedCalendar.del_date_list.forEach(item => {
                            const interimIndex = dataArr.indexOf(item)
                            if (interimIndex > -1) {
                                dataArr.splice(interimIndex, 1)
                            }
                        })
                        let noDuplicateDate = Array.from(new Set(dataArr))
                        // 需要判断是否为后导入数据，即用户已经选了某些日期，需要求并集
                        if (this.finalYearData[this.customYear]) {
                            noDuplicateDate = Array.from(new Set([...this.finalYearData[this.customYear], ...noDuplicateDate]))
                        }
                        this.importCalendarData = noDuplicateDate
                        // const allYear = Object.keys(this.finalYearData)
                        noDuplicateDate.forEach(item => {
                            const child = item.substring(0, 4)
                            if (Object.keys(this.finalYearData).indexOf(child) === -1) {
                                this.finalYearData[parseInt(child)] = []
                            }
                            this.finalYearData[parseInt(child)].push(item)
                        })
                        const interimYearList = Object.keys(importedCalendar.date_dict).map(item => parseInt(
                            item))
                        const seYearList = this.selectedYearList.map(item => parseInt(item))
                        interimYearList.push(...seYearList)
                        this.selectedYearList = Array.from(new Set(interimYearList))
                        this.customYear = this.customYear || this.selectedYearList[0]
                        this.$cwMessage('成功导入数据！', 'success')
                        this.dataSet()
                    } else {
                        this.$cwMessage('导入数据失败！', 'error')
                    }
                })
            },
            // 下载示例文件
            down() {
                window.open(window.siteUrl + '/export/demo_import_calendar')
            },
            // 增加日期
            addDays(val) {
                const calendarData = this.finalYearData[this.customYear].sort((a, b) => {
                    return a - b
                })
                for (let i = 0; i < val[this.customYear].length; i++) {
                    const daysKeyList = Object.keys(val).map(item => parseInt(item))
                    if (daysKeyList.indexOf(parseInt(this.customYear)) !== -1) {
                        if (val[this.customYear][i] >= calendarData[0]) {
                            this.earlyIndex = i
                            break
                        }
                    }
                }
                const autoAddDays = val[this.customYear].slice(this.earlyIndex, val[this.customYear].length)
                const intersectionDays = {}
                intersectionDays[this.customYear] = this.finalYearData[this.customYear].filter((item) => {
                    return autoAddDays.indexOf(item) > -1
                })
                autoAddDays.forEach(item => {
                    if (!intersectionDays[this.customYear].includes(item)) {
                        this.finalYearData[this.customYear].push(item)
                    }
                })
                this.duplicatedDays = intersectionDays
            },
            // 去除日期
            cancelDays(val) {
                let finalDelData = []
                if (!this.$route.params.isEdit) {
                    // 在删除日期时，需要做一层筛选（由用户手动勾选的数据不须删除）
                    finalDelData = val[this.customYear].filter(item => {
                        return this.duplicatedDays[this.customYear].indexOf(item) === -1
                    })
                } else {
                    finalDelData = val[this.customYear]
                }
                const arrCalendarData = this.finalYearData[this.customYear]
                for (let i = 0; i < arrCalendarData.length; i++) {
                    for (let j = 0; j < finalDelData.length; j++) {
                        if (finalDelData[j] === arrCalendarData[i]) {
                            arrCalendarData.splice(i, 1)
                        }
                    }
                }
            },
            // 选择工作日高亮
            selectWorkDays(val) {
                this.workState = val
                if (Object.keys(this.finalYearData).length === 0) {
                    if (val) {
                        this.$bkMessage({
                            message: '请先勾选日期！'
                        })
                    }
                    return
                }
                const days = acquireWorkAndHolidays()
                this.workDays = days.workDays
                if (val) {
                    this.addDays(this.workDays)
                } else {
                    this.cancelDays(this.workDays)
                }
                this.dataSet()
            },
            // 选择节假日高亮
            selectHolidaysAndFestivals(val) {
                this.holidayState = val
                if (Object.keys(this.finalYearData).length === 0) {
                    if (val) {
                        this.$bkMessage({
                            message: '请先勾选日期！'
                        })
                    }
                    return
                }
                const days = acquireWorkAndHolidays()
                this.holidaysAndFestivals = days.holidaysAndFestivals
                if (val) {
                    this.addDays(this.holidaysAndFestivals)
                } else {
                    this.cancelDays(this.holidaysAndFestivals)
                }
                this.dataSet()
            },
            generateId(index) {
                return this.selectedYearList[index]
            },
            handleClose(year) {
                const index = this.selectedYearList.indexOf(year)
                this.selectedYearList.splice(index, 1) // 在标签栏删除
                delete this.finalYearData[year] // 在日历中清除所选日期
                this.dataSet()
                this.changeNowList(year)
                this.targetYear = year
            },
            chooseTag(item) {
                this.customYear = item
                this.targetYear = item
                // if (this.$store.state.historyItem) {
                //     if (this.$store.state.historyItem !== item) {
                //         $('#' + item).css('backgroundColor', '#6495ED')
                //         $('#' + this.$store.state.historyItem).css('backgroundColor', 'transparent')
                //     } else {
                //         $('#' + item).css('backgroundColor', '#6495ED')
                //     }
                // } else {
                //     $('#' + item).css('backgroundColor', '#6495ED')
                // }
                // console.log(checked)
                // if(!checked) {
                //   $('#' + item).css('backgroundColor', '#6495ED')
                // }else {
                //   $('#' + item).css('backgroundColor', '#f7f7f7')
                // }
                // this.$store.state.historyItem = item
                this.dataSet()
            },
            dataSet() {
                this.isEdit = this.$route.params.isEdit
                this.isDetail = this.$route.params.isDetail
                if (this.$route.params.form) {
                    if (this.$route.params.form.date.length !== 0) {
                        let isDetails = false
                        isDetails = !!this.$route.params.isDetail
                        const ModifiedData = this.importCalendarData
                        this.datas = {
                            disable: isDetails,
                            year: this.customYear,
                            initDate: ModifiedData,
                            format: 'YYYY-MM-DD'
                        }
                    }
                    this.form = this.$route.params.form
                    this.changeNowList(this.customYear)
                } else {
                    this.changeNowList(this.customYear)
                }
            },
            // 子组件传过来的值
            synData(date) {
                if (date.length > 0) {
                    this.watchChildData = date
                    this.customYear = parseInt(date[0].substring(0, 4))
                    this.finalYearData[this.customYear] = date
                    if (this.$route.params.isEdit) {
                        this.importCalendarData = this.$route.params.form.date
                    }
                    const currentYearDate = this.finalYearData[this.customYear]
                    this.finalYearData[this.customYear] = Array.from(new Set([...currentYearDate, ...this.importCalendarData]))
                    this.targetYear = this.customYear
                    if (this.finalYearData[this.customYear].length === 0) {
                        const index = this.selectedYearList.indexOf(this.customYear)
                        this.selectedYearList.splice(index, 1)
                    } else {
                        const selectedYear = this.selectedYearList.map(item => parseInt(item))
                        if (selectedYear.indexOf(this.customYear) === -1) {
                            this.selectedYearList.push(this.customYear)
                        }
                        this.selectedYearList = Array.from(new Set(this.selectedYearList))
                    }
                }
            },
            // 新增日历
            confirm() {
                this.form.date = this.finalYearData
                this.form.quick = {
                    holiday: this.holidayState,
                    work: this.workState
                }
                this.showModal = false
                // 根据弹框modal标题判断新增还是更新
                if (this.form.name === '' || this.form.name === undefined) {
                    this.$cwMessage('请填写日历名', 'warning')
                } else if (this.form.description === '' || this.form.description === undefined) {
                    this.$cwMessage('请填写描述', 'warning')
                } else if (this.form.date === '') {
                    this.$cwMessage('请选择日期', 'warning')
                } else if (this.selectedYearList.length === 0) {
                    this.$cwMessage('请选择日期', 'warning')
                } else {
                    if (!this.isEdit) {
                        this.loading = true
                        this.$api.calendar.create(this.form).then(res => {
                            if (res.result) {
                                this.beforeroute = false
                                this.$cwMessage('新增成功', 'success')
                                this.$router.push({
                                    path: '/calendarmgmt'
                                })
                            } else {
                                this.$cwMessage('新增失败\n' + res.message, 'error')
                            }
                            this.loading = false
                        })
                    } else {
                        if (!this.isChange) {
                            this.$router.push({
                                path: '/calendarmgmt'
                            })
                        } else {
                            this.loading = true
                            this.form.date = this.finalYearData
                            // 深拷贝转换后的参数，必须深拷贝
                            const params = JSON.parse(JSON.stringify(this.form))
                            this.$api.calendar.update(this.form.id, params).then(res => {
                                if (res.result) {
                                    this.beforeroute = false
                                    this.$cwMessage('修改成功', 'success')
                                    this.$router.push({
                                        path: '/calendarmgmt'
                                    })
                                } else {
                                    this.$cwMessage('修改失败\n' + res.message, 'error')
                                }
                                this.loading = false
                            })
                            this.isChange = false
                        }
                    }
                }
            },
            // 取消
            cancel() {
                window.history.back(-1)
            },
            yearMinus() {
                if (this.customYear > 2021 && this.customYear < 9999) {
                    this.customYear--
                }
                this.targetYear = this.customYear
                this.dataSet()
            },
            yearPlus() {
                if (this.customYear >= 2021 && this.customYear < 9999) {
                    this.customYear++
                }
                this.targetYear = this.customYear
                this.dataSet()
            },
            jumpTo(val) {
                if (this.targetYear >= 2021) {
                    this.customYear = this.targetYear
                    this.dataSet()
                } else {
                    this.$cwMessage('请输入不小于2021的年份数', 'primary')
                }
            },
            changeNowList(val) {
                if (val) {
                    this.datas = {
                        disable: false,
                        year: val,
                        initDate: this.finalYearData[val],
                        format: 'YYYY-MM-DD'
                    }
                }
            }
        }
    // beforeRouteLeave(to, from, next) {
    //     if (!this.$route.params.isEdit && this.beforeroute) {
    //         this.$CWConfirm({
    //             type: 'edit',
    //             title: '提示',
    //             content: '此操作将不保留当前内容，是否继续跳转?',
    //             okText: '确定',
    //             cancelText: '取消',
    //         }).then(() => {
    //             next()
    //         }).catch(() => {
    //             this.$store.state.changeRoute = !this.$store.state.changeRoute
    //         })
    //     } else {
    //         next()
    //     }
    // },
    }
</script>

<style lang="scss" scoped>
#ces {
    width: 100%;
    height: 100%;
    overflow: auto;
    padding: 20px;

    .mgmtForm {
        margin-top: 10px;
        margin-bottom: 10px;

        .cesCal {
            // background-color: #fff;
            // border: 1px solid #DCDCDC;
            width: 840px;
            height: 482px;
            text-align: center;
            margin-left: -6px;
        }
    }

    .upload-wrap {
        display: inline-block;
        width: 100%;

        .ca-input {
            width: 70%;
            float: left;
            margin-right: 12px
        }

        .upload-button {
            float: left;
            margin-right: 12px;

            /deep/ .file-wrapper {
                height: 32px !important;
            }
        }

        .down-wrap {
            color: #3a84ff;
            cursor: pointer;
            height: 32px;
            line-height: 32px
        }
    }

    /deep/ .pre-button {
        margin-left: -46px;
        margin-top: -416px;
        position: absolute;
        width: 27px;
        height: 26px;
        line-height: 26px;
        background-color: #fff;
        border: 1px solid #c4c6cc;
        cursor: pointer;

        .bk-icon {
            font-size: 20px !important;
        }
    }

    .middle-input {
        width: 70px;
        margin-top: -416px;
        margin-left: -20px;
        position: absolute
    }

    .next-button {
        margin-top: -416px;
        position: absolute;
        margin-left: 49px;
        cursor: pointer;
        background-color: #fff;
        width: 26px;
        height: 26px;
        line-height: 26px;
        border: 1px solid #c4c6cc;

        .bk-icon {
            font-size: 20px !important;
        }
    }

    .des-input {
        width: 70%;
    }

    .MarginLeft18px {
        margin-left: 6px;
    }
}
</style>
