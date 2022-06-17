/* eslint-disable */
'use strict';
import validation from './pattern-validation'
function ErrorException (value) {
    this.value = value;
    this.message = "是一个非法表达式，请校验";
    this.toString = function() {
        return this.value + this.message;
    };
}
export default (() => {

  function validate(expression, config) {
    var common_config = Object.assign({ language: 'en'}, config || {})
    try {
      validation(expression, common_config, ErrorException);
    } catch(e) {
      if (e instanceof ErrorException) {
        return {status: false, msg: e.toString()};
      }
      return { status: false, msg: common_config.language === 'en' ? 'this is a invalid expression' : '非法表达式，请校验'}
      
    }

    return {status: true, msg: ''};
  }

  return {
    validate: validate
  };
})();
