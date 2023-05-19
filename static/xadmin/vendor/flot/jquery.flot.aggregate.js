/* Flot plugin for plotting grouping and aggregating data based on a common axis value.

Copyright (c) 2014 Jairus Martin (frmdstryr@gmail.com)
Licensed under the MIT license.

To enable it, you must specify aggregate: "count","min","max","avg", or "sum" 
on the axis to use as the grouping axis.

	$.plot("#placeholder", data, { xaxis: { aggregate: "avg" } });
	
The possible values for aggregate are:
	null,"count","min","max","avg", or "sum"

Can be used with categories consider a dataset like
	$.plot("#placeholder", data, { xaxis: { mode:"categories", aggregate: "count" } }); 
	[["Pass", 1], ["Fail", 1], ["Pass", 1]...].

*/

(function ($) {
    var options = {
        xaxis: {
            aggregate:null // null,"count","min","max","avg", or "sum"
        },
        yaxis: {
            aggregate:null // null,"count","min","max","avg", or "sum"
        }
    };
    
    function groupByAxis(data,axis) {
    	var groupedData = {};
    	$.each(data,function(i,point){
    		if (!(point[axis] in groupedData)) {
    			groupedData[point[axis]] = [point];
    		} else {
    			groupedData[point[axis]].push(point);
    		}
    	});
    	return groupedData;
    }
    
    function processRawData(plot, series, data, datapoints) {
        // if categories are enabled, we need to disable
        // auto-transformation to numbers so the strings are intact
        // for later processing

        var xAggregate = series.xaxis.options.aggregate != null,
            yAggregate = series.yaxis.options.aggregate != null;
        
        if (!(xAggregate || yAggregate))
            return;
        
        
        var aggregateMethod = null;
        var groupAxis = 0;
        var axis = 1;
        if (xAggregate) {
        	aggregateMethod = series.xaxis.options.aggregate;
        } else if (yAggregate) {
        	aggregateMethod = series.yaxis.options.aggregate;
        	groupAxis = 1;
        	axis = 0;
        }
        
        var groupedData = groupByAxis(data,groupAxis);
    	var newData = [];
    	switch (aggregateMethod) {
        	case "count":
        		$.each(groupedData,function(group,points) {
        			if (xAggregate){
        				newData.push([group,points.length]);
        			} else {
        				newData.push([points.length,group]);
        			}
        		});
        		break;
        	case "min":
        		$.each(groupedData,function(group,points) {
        			var yMin = points[0][axis];
        			$.each(points,function(i,point){yMin = Math.min(yMin,point[axis]);});
        			if (xAggregate){
        				newData.push([group,yMin]);
        			} else {
        				newData.push([yMin,group]);
        			}
        		});
        		break;
        	case "max":
        		$.each(groupedData,function(group,points) {
        			var yMax = points[0][axis];
        			$.each(points,function(i,point){yMax = Math.max(yMax,point[axis]);});
        			if (xAggregate){
        				newData.push([group,yMax]);
        			} else {
        				newData.push([yMax,group]);
        			}
        		});
        		break;
        	case "avg":
        		$.each(groupedData,function(group,points) {
        			var sum = 0;
        			$.each(points,function(i,point){sum+=point[axis];});
        			var avg = sum/points.length;
        			if (xAggregate){
        				newData.push([group,avg]);
        			} else {
        				newData.push([avg,group]);
        			}
        		});
        		break;
        	case "sum":
        		$.each(groupedData,function(group,points) {
        			var sum = 0;
        			$.each(points,function(i,point){sum+=point[axis];});
        			if (xAggregate){
        				newData.push([group,sum]);
        			} else {
        				newData.push([sum,group]);
        			}
        		});
        		break;
        	default:
        		return;
    	}
    	series.data = newData;
    	data = newData;
    }
   

    function init(plot) {
        plot.hooks.processRawData.push(processRawData);
    }
    
    $.plot.plugins.push({
        init: init,
        options: options,
        name: 'aggregate',
        version: '1.0'
    });
})(jQuery);
