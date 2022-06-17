/* eslint-disable */
'use strict';
export default (() => {
  function convertSteps(expressions){
    var stepValuePattern = /^(.+)\/(\d+)$/;
    for(const i in expressions){
      var match = stepValuePattern.exec(expressions[i]);
      var isStepValue = match !== null && match.length > 0;
      if(isStepValue){
        var values = match[1].split(',');
        var setpValues = [];
        var divider = parseInt(match[2], 10);
        for(const j in values){
          var value = parseInt(values[j], 10);
          if(value % divider === 0){
            setpValues.push(value);
          }
        }
        expressions[i] = setpValues.join(',');
      }
    }
    return expressions;
  }

  return convertSteps;
})();

