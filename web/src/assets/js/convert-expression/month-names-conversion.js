/* eslint-disable */
'use strict';
export default (() => {
  var months = ['january','february','march','april','may','june','july',
    'august','september','october','november','december'];
  var shortMonths = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
    'sep', 'oct', 'nov', 'dec'];

  function convertMonthName(expression, items){
    for(const i in expression){
      expression = expression.replace(new RegExp(items[i], 'gi'), parseInt(i, 10) + 1);
    }
    return expression;
  }

  function interprete(monthExpression){
    monthExpression = convertMonthName(monthExpression, months);
    monthExpression = convertMonthName(monthExpression, shortMonths);
    return monthExpression;
  }

  return interprete;
})();
