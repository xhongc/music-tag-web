/* eslint-disable */
'use strict';
import convertExpression from './convert-expression'
var commonConfig = {}
var KEYSMAP = [
    {
        key: 'second',
        error_en: 'is a invalid expression for second',
        error_ch: '在 “秒” '
    },
    {
        key: 'minute',
        error_en: 'is a invalid expression for minute',
        error_ch: '在 “分” '
    },
    {
        key: 'hour',
        error_en: 'is a invalid expression for hour',
        error_ch: '在 “小时” '
    },
    {
        key: 'day',
        error_en: 'is a invalid expression for day of month',
        error_ch: '在 “天” '
    },
    {
        key: 'month',
        error_en: 'is a invalid expression for month',
        error_ch: '在 “月” '
    },
    {
        key: 'week',
        error_en: 'is a invalid expression for second',
        error_ch: '在 “周” '
    }
]

export default ( () => {
  function isValidExpression(expression, min, max){
    var options = expression.split(',');
    var regexValidation = /^\d+$|^\*$|^\*\/\d+$/;
    for(const i in options){
      var option = options[i];
      var optionAsInt = parseInt(options[i], 10);
      if(optionAsInt < min || optionAsInt > max || !regexValidation.test(option)) {
        return false;
      }
    }
    return true;
  }
  function isIncludeDecimals(patterns) {
    for(var i = 0; i < patterns.length; i++){
        if(patterns[i].indexOf('.') > 0) {
          return {valid: true, index: i};
        }
    }
    return {valid: false};
  }
  function isInvalidSecond(expression){
    return !isValidExpression(expression, 0, 59);
  }

  function isInvalidMinute(expression){
    return !isValidExpression(expression, 0, 59);
  }

  function isInvalidHour(expression){
    return !isValidExpression(expression, 0, 23);
  }

  function isInvalidDayOfMonth(expression){
    return !isValidExpression(expression, 1, 31);
  }

  function isInvalidMonth(expression){
    return !isValidExpression(expression, 1, 12);
  }

  function isInvalidWeekDay(expression){
    return !isValidExpression(expression, 0, 6);
  }

  function validateFields(patterns, executablePatterns, ErrorException){
    var errorKey = 'error_ch'
    if (isIncludeDecimals(patterns).valid) {
        var currIndex = isIncludeDecimals(patterns).index
        throw new ErrorException(patterns[currIndex] + KEYSMAP[currIndex][errorKey]);
    }
    if (isInvalidSecond(executablePatterns[0])) {
      throw new ErrorException(patterns[0] + KEYSMAP[0][errorKey]);
    }

    if (isInvalidMinute(executablePatterns[1])) {
      throw new ErrorException(patterns[1] + KEYSMAP[1][errorKey]);
    }

    if (isInvalidHour(executablePatterns[2])) {
      throw new ErrorException(patterns[2] + KEYSMAP[2][errorKey]);
    }

    if (isInvalidDayOfMonth(executablePatterns[3])) {
      
      throw new ErrorException(patterns[3] + KEYSMAP[3][errorKey]);
    }

    if (isInvalidMonth(executablePatterns[4])) {
      throw new ErrorException(patterns[4] + KEYSMAP[4][errorKey]);
    }

    if (isInvalidWeekDay(executablePatterns[5])) {
      throw new ErrorException(patterns[5] + KEYSMAP[5][errorKey]);
    }
  }
  /**
   * 接受: 
   * [a-z] , - * / \d
   * 排除：
   * [A-Z]
   * \d[a-z]
   * *[^\/]
  */
  function basicCheck (patterns) {
    var allowValue = /[^\,|\-|\*|\/|\w]|\d[a-z]|[A-Z]|\*[^\/]/
    for (const pattern in patterns) {
        if (allowValue.test(patterns[pattern])) {
            throw '表达式非法，请校验'
        }
    }
  }
  function WeekExchangeDay (pattern) {
    var patterns = pattern.split(' ');
    var week = patterns[2]
    var day = patterns[3]
    var moth = patterns[4]
    patterns[2] = day
    patterns[3] = moth
    patterns[4] = week
    return patterns.join(' ')
  }
  function validate(pattern, common_config, ErrorException){
    commonConfig = common_config
    if (typeof pattern !== 'string'){
      throw new ErrorException('pattern must be a string!');
    }
    if (pattern.split(' ').length !== 5) {
      throw  '表达式非法，请校验'
    }
    pattern = WeekExchangeDay(pattern);
    var patterns = pattern.split(' ');
    // 先基础验证下
    basicCheck(patterns, ErrorException)
    // 对应的表达式解析成数字
    var executablePattern = convertExpression(pattern);
    var executablePatterns = executablePattern.split(' ');
    if(patterns.length === 5){
      patterns = ['0'].concat(patterns);
    }
    validateFields(patterns, executablePatterns, ErrorException);
  }

  return validate;
})();