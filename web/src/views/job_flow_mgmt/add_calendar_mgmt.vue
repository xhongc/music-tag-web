<template>
    <div id="addCalendar" v-bkloading="{ isLoading: mainLoading, zIndex: 9999 }">
        <bk-form :label-width="100" :model="form" ref="form" :rules="rules">
            <bk-form-item label="日历名" :required="true" :error-display-type="'normal'" :property="'name'">
                <div class="upload-wrap">
                    <bk-input v-model="form.name" placeholder="请输入日历名称" ext-cls="ca-input" :disabled="disabled">
                    </bk-input>
                    <input id="uploadFile" style="display: none" @change="uploadFile" type="file" accept=".xls,.xlsx" />
                    <bk-button theme="primary" @click="handleChooseFile" class="upload-btn" :disabled="disabled">导入</bk-button>
                    <span v-bk-tooltips="uploadTooltip" style="margin-right: 8px;">
                        <i class="bk-icon icon-info-circle-shape" style="font-size: 16px;color: #979BA5;"></i>
                    </span>
                    <span class="down-wrap" @click="hanldeDownExFile">下载示例文件</span>
                </div>
            </bk-form-item>
            <bk-form-item label="描述" :required="true" :error-display-type="'normal'" :property="'description'">
                <bk-input v-model="form.description" :disabled="disabled" style="width: 70%;"></bk-input>
            </bk-form-item>
            <bk-form-item label="已选年份">
                <bk-tag v-for="(item, index) in chooseYearList" :key="index" :closable="!disabled" theme="info"
                    @close="handleCloseTag(item)" :type="item === targetYear ? 'filled' : ''">
                    <span @click="handleChooseTag(item)" style="cursor: pointer;">{{item}}</span>
                </bk-tag>
            </bk-form-item>
            <bk-form-item label="快速设置">
                <bk-checkbox :disabled="disabled" @change="handleCheckWeekend" :before-change="handleCheckBefore">周末</bk-checkbox>
                <bk-checkbox style="margin-left: 16px;" :disabled="disabled" @change="handleCheckWorkDays" :before-change="handleCheckBefore">工作日
                </bk-checkbox>
            </bk-form-item>
            <bk-form-item label="日历设置" :required="true" ext-cls="calendar-panel">
                <calendar ref="calendar" :options="options" @getAllData="handleGetCalendar"></calendar>
                <div class="calendar-year-set">
                    <div class="pre-button" @click="handleSwitch('end')">
                        <bk-icon type="angle-left" />
                    </div>
                    <bk-input class="middle-input" style="width: 80px;" size="small" :disabled="disabled"
                        placeholder="跳转至" @enter="changeYear" v-model.number="midYear" type="number">
                    </bk-input>
                    <div class="next-button" @click="handleSwitch('front')">
                        <bk-icon type="angle-right" />
                    </div>
                </div>
            </bk-form-item>
            <div style="clear: both;"></div>
            <bk-form-item style="font-size: 0;">
                <bk-button style="margin-right: 8px;" theme="primary" @click="handleSave"
                    v-if="$route.query.type !== 'detail'">确定</bk-button>
                <bk-button @click="handleCancel">{{ $route.query.type === 'detail' ? '返回' : '取消' }}</bk-button>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    import calendar from '@/components/FullYearCalendar/calendar'
    import {
        getYearWeekDay,
        getWorkDays
    } from '../../common/date.js'
    export default {
        components: {
            calendar
        },
        data() {
            return {
                options: {
                    year: '',
                    disable: false,
                    data: []
                },
                midYear: '',
                targetYear: '',
                disabled: false,
                mainLoading: false,
                form: {
                    name: '', // 日历名称
                    description: '', // 描述信息
                    date: {} // 所选日历
                },
                chooseYearList: [],
                uploadTooltip: {
                    content: '上传的文件只能是xls以及xlsx格式',
                    showOnInit: false,
                    placements: ['bottom']
                },
                rules: {
                    name: [{
                        required: true,
                        message: '日历名不能为空',
                        trigger: 'change'
                    }],
                    description: [{
                        required: true,
                        message: '描述信息不能为空',
                        trigger: 'change'
                    }]
                }
            }
        },
        created() {
            if (this.$route.query.type !== 'add') {
                this.handleInitData()
                if (this.$route.query.type === 'detail') {
                    this.options.disable = true
                    this.disabled = true
                }
            }
        },
        methods: {
            handleCheckBefore() {
                if (!this.targetYear) {
                    this.$cwMessage('已选年份为空，请先选择一个日期！', 'primary')
                    return false
                }
            },
            // 处理快速设置周末
            handleCheckWeekend(e) {
                const arr1 = getYearWeekDay(this.targetYear)
                const arr2 = this.form.date[this.targetYear]
                if (e) {
                    this.form.date[this.targetYear] = Array.from(new Set(arr2.concat(arr1)))
                } else {
                    const arr = []
                    arr2.forEach(item => {
                        if (arr1.indexOf(item) === -1) {
                            arr.push(item)
                        }
                    })
                    this.form.date[this.targetYear] = arr
                }
                this.options.data = this.form.date[this.targetYear]
                this.options.year = this.targetYear
                this.handleSetCalendar()
            },
            // 处理快速设置工作日
            handleCheckWorkDays(e) {
                const arr1 = getWorkDays(this.targetYear)
                const arr2 = this.form.date[this.targetYear]
                if (e) {
                    this.form.date[this.targetYear] = Array.from(new Set(arr2.concat(arr1)))
                } else {
                    const arr = []
                    arr2.forEach(item => {
                        if (arr1.indexOf(item) === -1) {
                            arr.push(item)
                        }
                    })
                    this.form.date[this.targetYear] = arr
                }
                this.options.data = this.form.date[this.targetYear]
                this.options.year = this.targetYear
                this.handleSetCalendar()
            },
            // 处理数据初始化
            handleInitData() {
                this.mainLoading = true
                this.$api.calendar.list({
                    name: this.$route.query.name
                }).then(res => {
                    if (res.result) {
                        const data = res.data.items[0]
                        this.form.date = data.date
                        this.form.description = data.description
                        this.form.name = data.name
                        const arr = Object.keys(this.form.date).map(item => Number(item))
                        if (arr.length) {
                            this.chooseYearList = arr
                            this.targetYear = arr[0]
                            this.options.data = this.form.date[this.targetYear]
                            this.options.year = this.targetYear
                            this.handleSetCalendar()
                        }
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                    this.mainLoading = false
                })
            },
            // 处理前后切换年份
            handleSwitch(str) {
                if (this.midYear) {
                    this.midYear = str === 'front' ? this.midYear + 1 : this.midYear - 1
                    this.changeYear()
                }
            },
            // 处理下载实例文件
            hanldeDownExFile() {
                window.open(window.siteUrl + '/export/demo_import_calendar')
            },
            // 处理选择上传文件
            handleChooseFile() {
                document.getElementById('uploadFile').value = ''
                document.getElementById('uploadFile').click()
            },
            uploadFile() {
                const file = document.getElementById('uploadFile').files[0]
                const formData = new FormData()
                formData.append('file', file)
                formData.append('fileName', file.name)
                this.$api.calendar.post_calendar_file(formData).then(res => {
                    if (res.result) {
                        const calendarData = res.data
                        // 说明已选年份不为空
                        if (this.chooseYearList.length) {
                            // 遍历导入数据字典
                            Object.keys(calendarData.date_dict).forEach(key => {
                                // 已选年份中有和导入数据字典相同的年份
                                if (this.chooseYearList.indexOf(Number(key)) > -1) {
                                    // 合并数据并去重
                                    this.form.date[key] = Array.from(new Set(this.form.date[key].concat(
                                        calendarData.date_dict[key])))
                                } else {
                                    // 这里表明已选年份中没有和导入数据字典相同的，且该年份导入数据不为空
                                    if (calendarData.date_dict[key].length) {
                                        // 新建已选年份并填充数据
                                        this.form.date[key] = calendarData.date_dict[key]
                                    }
                                }
                            })
                        } else {
                            // 已选年份为空，遍历导入数据字典
                            Object.keys(calendarData.date_dict).forEach(key => {
                                // 只要导入数据字典年份日历数据不为空，填充赋值。
                                if (calendarData.date_dict[key].length) {
                                    this.form.date[key] = calendarData.date_dict[key]
                                }
                            })
                        }
                        console.log(this.form.date)
                        // 去除表格中的del_date
                        Object.keys(this.form.date).forEach(key => {
                            for (let i = 0; i < this.form.date[key].length; i++) {
                                if (calendarData.del_date_list.indexOf(this.form.date[key][i]) > -1) {
                                    this.form.date[key].splice(i, 1)
                                    i--
                                }
                            }
                        })
                        this.chooseYearList = Object.keys(this.form.date).map(key => Number(key))
                        if (!this.targetYear) {
                            this.targetYear = this.chooseYearList[0]
                        }
                        this.options.data = this.form.date[this.targetYear]
                        this.options.year = this.targetYear
                        this.handleSetCalendar()
                        this.$cwMessage('成功导入数据！', 'success')
                    } else {
                        this.$cwMessage('导入数据失败！', 'error')
                    }
                })
            },
            // 处理关闭标签
            handleCloseTag(key) {
                const index = this.chooseYearList.findIndex(item => item === key)
                this.chooseYearList.splice(index, 1)
                if (this.targetYear === key) {
                    if (this.chooseYearList.length) {
                        this.targetYear = this.chooseYearList[0]
                        this.options.data = this.form.date[this.targetYear]
                        this.options.year = this.targetYear
                    } else {
                        this.options.data = []
                        this.options.year = ''
                    }
                    this.handleSetCalendar()
                }
                delete this.form.date[key]
            },
            // 处理实时获取日历
            handleGetCalendar(date) {
                if (!this.chooseYearList.length && date.length) {
                    const item = Number(date[0].split('-')[0])
                    this.chooseYearList.push(item)
                    this.targetYear = item
                }
                if (!date.length) {
                    this.chooseYearList.splice(this.chooseYearList.indexOf(this.targetYear), 1)
                    delete this.form.date[this.targetYear]
                    if (this.chooseYearList.length) {
                        this.targetYear = this.chooseYearList[0]
                        this.options.data = this.form.date[this.targetYear]
                        this.options.year = this.targetYear
                        this.handleSetCalendar()
                    } else {
                        this.targetYear = ''
                    }
                } else {
                    this.form.date[this.targetYear] = date
                }
            },
            // 处理年份改变
            changeYear() {
                if (this.midYear < 1949 || this.midYear > 9999) {
                    return false
                }
                this.targetYear = this.midYear
                if (this.chooseYearList.indexOf(this.targetYear) === -1) {
                    this.chooseYearList.push(this.targetYear)
                    this.chooseYearList = this.chooseYearList.sort((a, b) => {
                        return a - b
                    })
                }
                if (this.form.date.hasOwnProperty(this.targetYear)) {
                    this.options.data = this.form.date[this.targetYear]
                } else {
                    this.form.date[this.targetYear] = []
                    this.options.data = []
                }
                this.options.year = this.targetYear
                this.handleSetCalendar()
            },
            // 处理选择标签
            handleChooseTag(item) {
                this.targetYear = item
                this.options.year = this.targetYear
                this.options.data = this.form.date[this.targetYear]
                this.handleSetCalendar()
            },
            // 处理更新日历面板
            handleSetCalendar() {
                this.$refs.calendar.initCalendar()
            },
            // 处理保存
            handleSave() {
                this.$refs.form.validate().then(validator => {
                    if (validator) {
                        if (!this.chooseYearList.length) {
                            return this.$cwMessage('请至少选择一个日期！', 'warning')
                        } else {
                            if (Object.values(this.form.date).some(item => !item.length)) {
                                return this.$cwMessage('所选年份中日期不能为空，请检查您的选择！', 'warning')
                            }
                            // this.mainLoading = true
                            if (this.$route.query.type === 'add') {
                                this.$api.calendar.create(this.form).then(res => {
                                    if (res.result) {
                                        this.$cwMessage('新增成功', 'success')
                                        this.$router.push({
                                            path: '/calendarmgmt'
                                        })
                                    } else {
                                        this.$cwMessage('新增失败\n' + res.message, 'error')
                                    }
                                    this.mainLoading = false
                                })
                            } else {
                                console.log(this.form)
                                // this.$api.calendar.update(parseInt(this.$route.query.id), this.form).then(res => {
                                //     if (res.result) {
                                //         this.$cwMessage('修改成功', 'success')
                                //         this.$router.push({
                                //             path: '/calendarmgmt'
                                //         })
                                //     } else {
                                //         this.$cwMessage('修改失败\n' + res.message, 'error')
                                //     }
                                //     this.mainLoading = false
                                // })
                            }
                        }
                    }
                }).catch(e => {
                    this.$cwMessage('输入有误, 请检查您的输入！', 'warning')
                })
            },
            // 处理取消
            handleCancel() {
                window.history.back(-1)
            }
        }
    }
</script>

<style lang="scss" scoped>
    #addCalendar {
        padding: 30px 20px 20px 20px;

        .upload-wrap {
            display: flex;

            .ca-input {
                width: 70%;
                margin-right: 12px
            }

            .upload-btn {
                margin-right: 12px
            }

            .down-wrap {
                color: #3a84ff;
                cursor: pointer;
            }
        }

        .calendar-panel {
            position: relative;

            .calendar-year-set {
                z-index: 20;
                position: absolute;
                top: 5px;
                left: 700px;
                display: flex;
                align-items: center;

                .pre-button {
                    width: 26px;
                    height: 26px;
                    line-height: 26px;
                    text-align: center;
                    background-color: #fff;
                    border: 1px solid #c4c6cc;
                    border-right: 0;
                    cursor: pointer;

                    .bk-icon {
                        font-size: 20px !important;
                    }
                }

                .next-button {
                    width: 26px;
                    height: 26px;
                    line-height: 26px;
                    text-align: center;
                    background-color: #fff;
                    border: 1px solid #c4c6cc;
                    border-left: 0;
                    cursor: pointer;

                    .bk-icon {
                        font-size: 20px !important;
                    }
                }
            }
        }
    }
</style>
