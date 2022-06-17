<template>
    <div class="loop-rule-select">
        <div class="loop-rule-title bk-button-group">
            <bk-button
                :theme="currentWay === 'selectGeneration' ? 'primary' : 'default'"
                class="rule-btn"
                @click="onSwitchWay('selectGeneration')">
                选择生成
            </bk-button>
            <bk-button
                :theme="currentWay === 'manualInput' ? 'primary' : 'default'"
                class="rule-btn"
                @click="onSwitchWay('manualInput')">
                手动输入
            </bk-button>
        </div>
        <div class="content-wrapper">
            <div class="selected-input" v-show="currentWay === 'selectGeneration'">
                <bk-input :value="expressionShowText" :disabled="true"></bk-input>
                <span class="clear-selected" @click.stop="clearRule">
                    清空
                </span>
            </div>
            <!-- 自动生成 -->
            <bk-tab
                style="background: #fff"
                v-show="currentWay === 'selectGeneration'"
                :type="'border-card'"
                :active="tabName"
                @tab-changed="tabChanged">
                <bk-tab-panel
                    v-for="(item, index) in autoRuleList"
                    :key="index"
                    :name="item.key"
                    :label="item.title">
                    <div class="tabpanel-container">
                        <bk-radio-group v-model="item.radio" @change="renderRule">
                            <bk-radio :value="0">{{ autoWay.loop.name }}</bk-radio>
                            <bk-radio :value="1">{{ autoWay.appoint.name }}</bk-radio>
                        </bk-radio-group>
                        <!-- 循环生成 -->
                        <div v-if="item.radio === 0" class="loop-select-bd">
                            {{ item.key !== 'week' ? autoWay.loop.start : autoWay.loop.startWeek }}
                            <bk-input
                                v-model.number="item.loop.start"
                                v-validate="item.loop.reg"
                                :name="item.key + 'Rule'"
                                class="loop-time"
                                @blur="renderRule()">
                            </bk-input>
                            {{ item.key !== 'week' ? item.title : ''}}{{ autoWay.loop.center }}
                            <bk-input
                                v-model.number="item.loop.inter"
                                v-validate="{ required: true, integer: true }"
                                name="interval"
                                class="loop-time"
                                @blur="renderRule()">
                            </bk-input>
                            {{ item.key !== 'week' ? item.title : '天' }}{{ autoWay.loop.end }}
                            <!-- 星期说明 -->
                            <i v-if="item.key === 'week'" v-bk-tooltips="'0 表示星期天，6 表示星期六'" class="common-icon-info month-tips top-start"></i>
                            <!-- startInput 错误提示 -->
                            <div v-show="errors.has(item.key + 'Rule') || errors.has('interval')"
                                class="local-error-tip error-msg">
                                {{ errors.first(item.key + 'Rule') || errors.first('interval') }}
                            </div>
                        </div>
                        <!-- 指定 -->
                        <div v-else class="appoint-select-bd">
                            <bk-checkbox
                                v-for="(box, i) in item.checkboxList"
                                :key="i"
                                v-model="box.checked"
                                @change="renderRule">
                                {{ box.value | addZero(item.key) }}
                            </bk-checkbox>
                        </div>
                    </div>
                </bk-tab-panel>
            </bk-tab>
            <!-- 手动输入 -->
            <div v-show="currentWay === 'manualInput'" class="hand-input">
                <bk-input
                    :clearable="true"
                    name="periodicCron"
                    class="step-form-content-size"
                    v-model="periodicCron"
                    v-validate="{ required: true, cronRlue: true }">
                </bk-input>
            </div>
        </div>
        <bk-icon class="common-icon-info rule-tips" type="question-circle" v-bk-tooltips="ruleTipsHtmlConfig"></bk-icon>
        <!-- corn 规则 tips -->
        <div id="periodic-cron-tips-html">
            <img style="width:100%" class="ui-img" :src="periodicCronImg">
        </div>
        <!-- 手动输入错误提示 -->
        <span v-show="errors.has('periodicCron') && currentWay === 'manualInput'"
            class="common-error-tip error-msg">
            {{ errors.first('periodicCron') }}
        </span>
    </div>
</template>
<script>
    import { PERIODIC_REG } from '@/constants/index.js'
    const autoRuleList = [
        {
            key: 'min',
            title: '分钟',
            radio: 0,
            long: 60,
            max: 59,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([0-9]|0[1-9]|[0-5][0-9])$/
                }
            }
        },
        {
            key: 'hour',
            title: '小时',
            radio: 0,
            long: 24,
            max: 23,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([0-9]|0[1-9]|[0-1][0-9]|20|21|23)$/
                }
            }
        },
        {
            key: 'week',
            title: '星期',
            radio: 0,
            long: 7,
            max: 6,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^[0-6]$/
                }
            }
        },
        {
            key: 'day',
            title: '日期',
            radio: 0,
            long: 31,
            max: 31,
            loop: {
                start: 1,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([1-9]|0[1-9]|1[0-9]|2[0-9]|30|31)$/
                }
            }
        },
        {
            key: 'month',
            title: '月份',
            radio: 0,
            long: 12,
            max: 12,
            loop: {
                start: 1,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([1-9]|0[1-9]|10|11|12)$/
                }
            }
        }
    ]
    const loopStarZeroList = ['min', 'hour', 'week']
    const loopStarOneList = ['day', 'month']
    const autoWay = {
        'loop': {
            name: '循环',
            start: '从第',
            startWeek: '从星期',
            center: '开始，每隔',
            end: '执行一次'
        },
        'appoint': {
            name: '指定'
        }
    }
    const numberMap = {
        1: '星期一',
        2: '星期二',
        3: '星期三',
        4: '星期四',
        5: '星期五',
        6: '星期六',
        0: '星期天'
    }
    export default {
        name: 'loop-rule-select',
        filters: {
            addZero(v, k) {
                return k === 'week' ? v : (v < 10 ? '0' + v : v)
            }
        },
        props: {
            manualInputValue: {
                type: String,
                default: '*/5 * * * *'
            }
        },
        data() {
            return {
                periodicRule: {
                    required: true,
                    regex: PERIODIC_REG
                },
                expressionList: ['*', '*', '*', '*', '*'],
                periodicCronImg: require('@/assets/base/img/task-example.png'),
                // 规则列表
                autoRuleList: [],
                // 循环选择方式
                autoWay: autoWay,
                // manualInput 手动 / selectGeneration 选择生成
                currentWay: 'selectGeneration',
                currentRadio: 'loop',
                tabName: 'min',
                tName: '',
                periodicCron: '',
                templateNameRule: '',
                ruleTipsHtmlConfig: {
                    allowHtml: true,
                    width: 560,
                    trigger: 'mouseenter',
                    theme: 'light',
                    content: '#periodic-cron-tips-html',
                    placement: 'top'
                }
            }
        },
        computed: {
            expressionShowText() {
                return this.expressionList.join('^').replace(/\^/g, ' ')
            }
        },
        watch: {
            manualInputValue: {
                handler(v) {
                    this.periodicCron = v
                    this.setValue(v)
                },
                immediate: true
            }
        },
        created() {
            this.autoRuleList = this.cloneDeep(autoRuleList)
            this.initializeAutoRuleListData()
            this.renderRule()
        },
        methods: {
            onSwitchWay(way) {
                this.currentWay = way
            },
            /**
             * 周期选择方式切换触发
             * @param {String} name -tab name
             */
            tabChanged(name) {
                this.tabName = name
            },
            /**
             * 周期循环方式切换,循环/指定
             * @param {Number} index - 下标
             * @param {Number} value - 改变的值
             */
            onAutoWaySwitch(index, value) {
                this.$set(this.autoRuleList[index], 'radio', Number(value))
                this.renderRule()
            },
            /**
             * 初始化数据
             * @description 根据 autoRuleList 动态插入 radio 项
             */
            initializeAutoRuleListData() {
                this.autoRuleList.forEach((item, index) => {
                    const pushArr = []
                    for (let i = 0; i < item.long; i++) {
                        const realityIndex = loopStarOneList.includes(item.key) ? i + 1 : i
                        pushArr.push({
                            name: `${item.key}${i}`,
                            checked: true,
                            v: i,
                            value: item.key !== 'week' ? realityIndex : numberMap[realityIndex]
                        })
                    }
                    this.$set(this.autoRuleList[index], 'checkboxList', pushArr)
                })
            },
            // 清空已选
            clearRule() {
                this.autoRuleList.forEach((item, index) => {
                    item.checkboxList.forEach((m, i) => {
                        m.checked = false
                    })
                    item.loop.start = loopStarZeroList.includes(item.key) ? 0 : 1
                    item.loop.inter = 1
                })
                this.renderRule()
            },
            /**
             *  渲染规则
             *  @description
             *  1. min-max/1  <=> *
             *  2. min-max/n  <=> 星/d
             *  @param {String} key --tab key
             *  @param {String} way --自动/手动
             *  @param {Number} index --下标
             */
            renderRule() {
                this.autoRuleList.forEach((m, i) => {
                    const { radio, loop, checkboxList, max } = m
                    let loopRule = ''
                    if (loop.start === (loopStarZeroList.includes(m.key) ? 0 : 1)) {
                        loopRule = `*/${loop.inter}`
                        if (loop.inter === 1) {
                            loopRule = '*'
                        }
                    } else {
                        loopRule = `${loop.start}-${max}/${loop.inter}`
                    }
                    const pointRule = checkboxList
                        .filter(res => res.checked)
                        .map(res => {
                            // satrt 1 时 显示 i + 1
                            return loopStarOneList.includes(m.key) ? res.v + 1 : res.v
                        })
                        .join(',') || '*'
                    const data = radio === 0 ? loopRule : pointRule
                    this.$set(this.expressionList, i, data)
                })
            },
            /**
             * 合并相近数字 1,2,3 => 1-3
             * @param {Object} arr 数字数组
             */
            mergeCloseNumber(arr) {
                if (Array.isArray(arr)) {
                    let hasMergeList = []
                    const exportList = []
                    for (let i = 0; i < arr.length; i++) {
                        if (hasMergeList.some(t => t === arr[i])) continue
                        const mergeItem = []
                        let nowValue = arr[i]
                        mergeItem.push(arr[i])
                        for (let j = i + 1; j < arr.length; j++) {
                            if (nowValue + 1 === arr[j]) {
                                mergeItem.push(arr[j])
                                nowValue = arr[j]
                                continue
                            }
                            break
                        }
                        exportList.push(mergeItem)
                        hasMergeList = [...hasMergeList, ...mergeItem]
                    }
                    return exportList.map(m => m.length > 1 ? `${m[0]}-${m[m.length - 1]}/1` : `${m[0]}`)
                } else {
                    return arr
                }
            },
            /**
             * 提交时验证表达式
             * @returns {Boolean} true/false
             */
            validationExpression() {
                let flag = true
                this.autoRuleList.forEach(m => {
                    if (this.$validator.errors.has(m.key + 'Rule') && this.currentWay === 'selectGeneration') {
                        this.tabName = m.key
                        flag = false
                    }
                })
                if (this.currentWay === 'manualInput' && this.$validator.errors.has('periodicCron')) {
                    this.currentWay = 'manualInput'
                    flag = false
                }
                return {
                    check: flag,
                    rule: this.currentWay === 'manualInput' ? this.periodicCron : this.expressionShowText
                }
            },
            /**
             * 根据表达式设置选中状态
             * @param {String} v
             * 目前传入值仅支持 4 中形式
             * 1. *
             * 2. min-max/d
             * 3. d,d,d,d
             * 4. ※/d <===> min-max/d
             */
            setValue(setValue) {
                this.$nextTick(() => {
                    const periodicList = setValue.split(' ')
                    periodicList.forEach((m, i) => {
                        const item = this.autoRuleList[i]
                        if (m === '*') {
                            item.radio = 0
                            item.checkboxList.forEach(t => {
                                t.checked = true
                            })
                        } else if (m.indexOf('/') !== -1 && m.split('/')[0].split('-')[1] * 1 === item.max) {
                            // min-max/d
                            item.radio = 0
                            item.loop.start = m.split('/')[0].split('-')[0] * 1
                            item.loop.inter = m.split('/')[1] * 1
                        } else if (m.indexOf('*/') !== -1) {
                            // */d
                            item.radio = 0
                            item.loop.start = loopStarZeroList.includes(item.key) ? 0 : 1
                            item.loop.inter = m.split('/')[1] * 1
                        } else if (!/[^(\d{1,2},)]|[^(\d{1,2})]/g.test(m)) {
                            // d,d,d,d
                            item.radio = 1
                            item.checkboxList.forEach((box, boxIndex) => {
                                box.checked = m.split(',').some(s => {
                                    return loopStarOneList.includes(item.key) ? s * 1 - 1 === box.v * 1 : s * 1 === box.v * 1
                                })
                            })
                        } else {
                            // 匹配不到
                            this.currentWay = 'manualInput'
                        }
                    })
                    this.renderRule()
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
$commonBorderColor: #dddddd;
$blueBtnBg: #c7dcff;
$colorBalck: #313238;
$colorBlue: #3a84ff;
$colorGrey: #63656e;
$bgBlue: #3a84ff;

.ui-checkbox-group {
    margin-top: 20px;
    margin-right: 18px;
    display: inline-block;
    .ui-checkbox-input {
        display: none;
    }
    .ui-checkbox-icon {
        box-sizing: border-box;
        display: inline-block;
        position: relative;
        width: 16px;
        height: 16px;
        border: 1px solid #979BA5;
        text-align: center;
        padding-left: 12px;
        line-height: 1;
    }
    .ui-checkbox-label {
        user-select: none;
        cursor: pointer;
        color: $colorGrey;
        .ui-checkbox-tex,
        .ui-checkbox-icon {
            vertical-align: middle;
        }
    }
    .ui-checkbox-input:checked + .ui-checkbox-label > .ui-checkbox-icon::after {
        content: "";
        position: absolute;
        left: 2px;
        top: 2px;
        height: 4px;
        width: 8px;
        border-left: 2px solid;
        border-bottom: 2px solid;
        border-color: #ffffff;
        -webkit-transform: rotate(-45deg);
        transform: rotate(-45deg);
    }
    .ui-checkbox-input:checked + .ui-checkbox-label > .ui-checkbox-icon {
        background: $bgBlue;
        border-color: $bgBlue;
    }
}
.bk-form-radio {
    margin-right: 30px;
}
.bk-form-checkbox {
    margin-top: 20px;
    margin-right: 22px;
    min-width: 40px;
}
.rule-tips {
    position: absolute;
    top: 0;
    right: 0;
    margin-right: -26px;
    margin-top: 8px;
    color: #c4c6cc;
    font-size: 14px !important;
    &:hover {
        color: #f4aa1a;
    }
}
.local-error-tip {
    margin-top: 10px;
    font-size: 14px;
    line-height: 1;
    color: #ff5757;
}
.loop-rule-select {
    position: relative;
    width: 500px;
    .loop-rule-title {
        width: 100%;
        white-space: nowrap;
        .rule-btn {
            width: 50%;
            border-radius: 0;
        }
        .bk-button.bk-primary {
            position: relative;
            z-index: 4;
            color: #3a84ff;
            background-color: #c7dcff;
            border-radius: 2px;
            border: 1px solid #3a84ff;
        }
    }
    // content
    .content-wrapper {
        margin-top: 18px;
        // background-color: $whiteDefault;
        .selected-input {
            margin-bottom: 18px;
            & > .bk-form-control {
                width: 450px;
            }
            .clear-selected {
                float: right;
                margin-top: 11px;
                font-size: 12px;
                color: #3a84ff;
                cursor: pointer;
            }
            /deep/.bk-form-input {
                color: #333333;
                cursor: text;
            }
        }
        /deep/ .tab2-nav-item {
            width: 20%;
            border-bottom: 1px solid $commonBorderColor;
            line-height: 40px !important;
            &:not(:first-child) {
                border-left: 1px solid $commonBorderColor !important;
            }
        }
        /deep/.bk-tab2-nav .active {
            border-bottom: none;
            border-right: none !important;
        }
        /deep/ .bk-tab2 {
            border: 1px solid $commonBorderColor;
        }
        /deep/ .bk-tab-label-list {
            width: 100%;
            .bk-tab-label-item {
                width: 20.05%;
            }
        }
        .tabpanel-container {
            padding: 20px;
            .loop-select-bd {
                margin-top: 18px;
                font-size: 14px;
                color: $colorBalck;
                .loop-time {
                    display: inline-block;
                    margin: 0 10px;
                    width: 46px;
                }
                .month-tips {
                    margin-left: 6px;
                    color: #c4c6cc;color: #c4c6cc;
                    font-size: 14px;
                    &:hover {
                        color: #f4aa1a;
                    }
                }
            }
            .appoint-select-bd {
                margin-top: 18px;
                padding: 0 20px 20px 20px;
                border: 1px solid $commonBorderColor;
            }
        }
    }
    .periodic-img-tooltip {
        position: absolute;
        right: -18px;
        top: 10px;
        color: #c4c6cc;
        font-size: 14px;
        z-index: 4;
        &:hover {
            color: #f4aa1a;
        }
        /deep/ .bk-tooltip-arrow {
            display: none;
        }
        /deep/ .bk-tooltip-inner {
            max-width: 520px;
            padding: 0px;
            border: none;
            background-color: transparent;
        }
    }
}
</style>
