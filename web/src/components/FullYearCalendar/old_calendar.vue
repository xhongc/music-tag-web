<template>
    <div id="calendar">
        <div id="div1"></div>
        <div class="tipsty">
            <div class="center-rigjt">
                <Poptip trigger="hover" title="日历使用说明" placement="top">
                    <div slot="content" style="width:400px">
                        <p style="float:left">范围选择：先选择好开始日历，摁住Shift,在选择结束日期</p>
                        <p style="float:left">单个选择：直接点击选择日期</p>
                    </div>
                    <span style="font-size: 16px;color: #979BA5;" class="iconfont icon-mianxingtubiao-wenti"></span>
                    <!-- <Icon style="font-size:18px" type="ios-help-circle-outline"/> -->
                </Poptip>
            </div>
        </div>
    </div>
</template>
<script>
    import {fullYearPicker} from './js/fullYearPicker.js'
    import $ from 'jquery'

    export default {
        name: 'calendar',
        props: {
            SetCalendar: {
                disable: { //是否只读
                    default: false
                },
                year: { //指定年份
                    default: ''
                },
                initDate: Array,
                format: { //日期格式化
                    default: 'YYYY-MM-DD'
                },
            },
            newSetCalendar: {},
        },
        data() {
            return {}
        },
        mounted() {
            let _this = this
            _this.swippertab(_this)
        },
        watch: {
            SetCalendar(newVal, oldVal) {
                console.log(newVal)
                // console.log(oldVal)
                this.SetCalendar.year = newVal['year']
                let _this = this
                _this.swippertab(_this)
            },
        },
        methods: {
            swippertab(_this) {
                // console.log(_this.SetCalendar, '子组件被调用')
                $('#div1').fullYearPicker({
                    disable: _this.SetCalendar.disable, //只读
                    year: _this.SetCalendar.year, //指定年份
                    initDate: _this.SetCalendar.initDate, //初始化选中日期
                    yearScale: {min: 1949, max: 9999}, //初始化日历范围
                    format: _this.SetCalendar.format, //日期格式化  YYYY-MM-DD  YYYY-M-D
                    cellClick: function (dateStr, isDisabled) { //当前选中日期回调函数
                    },
                    choose: function (a) { //实时获取所有选中的日期的回调函数
                        _this.$emit('syndata', a)
                    },
                });
            },
        },
    }
</script>
<style>
    #calendar {
        width: 100%;
        height: 400px;
    }

    .tipsty {
        height: 20px;
        float: left;
        margin-top: 4px;
        width: 4%;
        /*border: 1px solid red;*/
    }

    #div1 {
        min-width: 670px;
        height: 500px;
        float: left;
    }

    .fullYearPicker, .fullYearPicker table {
        font-size: 12px;
        font-family: Microsoft Yahei,PingFang SC,Helvetica,Aria;
        -moz-user-select: none;
        -webkit-user-select: none;
        user-select: none
    }

    .fullYearPicker div.year {
        text-align: center
    }

    .fullYearPicker div.year a {
        margin-right: 30px
    }

    .fullYearPicker div.year a.next {
        margin-right: 0;
        margin-left: 30px
    }

    .fullYearPicker table {
        border: 1px solid #dcdee5;
        margin-top: 5px;
        float: left;
        margin-right: 20px;
        width: 150px;
    }

    .fullYearPicker table.right {
        margin-right: 0
    }

    .fullYearPicker table th.head {
        text-align: center;
        line-height: 23px;
        cursor: default;
        background: #fff
    }

    .fullYearPicker table td {
        background: #fff;
        text-align: center;
        line-height: 15px;
        cursor: pointer
    }

    .fullYearPicker table th {
        color: #63656e
    }

    .fullYearPicker table td.weekend, .fullYearPicker table th.weekend {
    }

    .fullYearPicker table td.disabled {
        color: #63656e;
        cursor: not-allowed
    }

    .fullYearPicker table td.selected {
        background: #3a84ff;
        color: #fff
    }

    .fullYearPicker table td.empty {
        cursor: default
    }

    .fullYearPicker br {
        clear: both
    }

    .year {
        display: none
    }

    .arrow_box {
        animation: glow 800ms ease-out infinite alternate
    }

    .center-right {
        float: right;
    }

    /*@keyframes glow {*/
    /*    0% {*/
    /*        border-color: red;*/
    /*        box-shadow: 0 0 5px red, inset 0 0 5px red, 0 1px red*/
    /*    }*/
    /*    100% {*/
    /*        border-color: red;*/
    /*        box-shadow: 0 0 20px red, inset 0 0 10px red, 0 1px 0 red*/
    /*    }*/
    /*}*/

</style>
