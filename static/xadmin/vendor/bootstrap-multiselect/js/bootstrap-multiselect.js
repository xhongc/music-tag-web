/**
 * bootstrap-multiselect.js 1.0.0
 * https://github.com/davidstutz/bootstrap-multiselect
 *
 * Copyright 2012 David Stutz
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
!function ($) {

	"use strict"; // jshint ;_;

	if(typeof ko != 'undefined' && ko.bindingHandlers && !ko.bindingHandlers.multiselect){
		ko.bindingHandlers.multiselect = {
		    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {},
		    update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
		        var ms = $(element).data('multiselect');
		        if (!ms) {
		            $(element).multiselect(ko.utils.unwrapObservable(valueAccessor()));
		        }
		        else if (allBindingsAccessor().options().length !== ms.originalOptions.length) {
		            ms.updateOriginalOptions();
		            $(element).multiselect('rebuild');
		        }
		    }
		};
	}

	function Multiselect(select, options) {
		
		this.options = this.getOptions(options);
		this.$select = $(select);
		this.originalOptions = this.$select.clone()[0].options; //we have to clone to create a new reference
	    this.query = '';
		this.searchTimeout = null;
		
		this.options.multiple = this.$select.attr('multiple') == "multiple";
		
		this.$container = $(this.options.buttonContainer)
	        .append('<button type="button" class="multiselect dropdown-toggle ' + this.options.buttonClass + '" data-toggle="dropdown">' + this.options.buttonText(this.getSelected(), this.$select) + '</button>')
	        .append('<div class="multiselect-container dropdown-menu" style="position:absolute;"></div>');

		if (this.options.buttonWidth) {
			$('button', this.$container).css({
				'width': this.options.buttonWidth
			});
		}

		this.buildDropdown();
		
		this.updateButtonText();
		
		this.$select
			.hide()
			.after(this.$container);
	};

	Multiselect.prototype = {
		
		defaults: {
			// Default text function will either print 'None selected' in case no option is selected,
			// or a list of the selected options up to a length of 3 selected options.
			// If more than 3 options are selected, the number of selected options is printed.
			buttonText: function(options, select) {
				if (options.length == 0) {
					return 'None selected <b class="caret"></b>';
				}
				else if (options.length > 3) {
					return options.length + ' selected <b class="caret"></b>';
				}
				else {
					var selected = '';
					options.each(function() {
						var label = ($(this).attr('label') !== undefined) ? $(this).attr('label') : $(this).text();

						selected += label + ', ';
					});
					return selected.substr(0, selected.length -2) + ' <b class="caret"></b>';
				}
			},
			// Is triggered on change of the selected options.
			onChange: function(option, checked) {
				
			},
			buttonClass: 'btn',
			dropRight: false,
			selectedClass: 'active',
			buttonWidth: 'auto',
			buttonContainer: '<div class="btn-group" />',
			// Maximum height of the dropdown menu.
			// If maximum height is exceeded a scrollbar will be displayed.
			maxHeight: false,
			includeSelectAllOption: false,
			selectAllText: ' Select all',
			enableFiltering: false,
			filterPlaceholder: 'Search'
		},

		constructor: Multiselect,
		
		// Will build an dropdown element for the given option.
		createOptionValue: function(element) {
			if ($(element).is(':selected')) {
				$(element).attr('selected', 'selected').prop('selected', true);
			}
			
			// Support the label attribute on options.
			var label = $(element).attr('label') || $(element).text();
			var value = $(element).val();
			var inputType = this.options.multiple ? "checkbox" : "radio";

			var $li = $('<li><a href="javascript:void(0);" style="padding:0;"><label style="margin:0;padding:3px 20px 3px 20px;height:100%;cursor:pointer;"><input style="margin-bottom:5px;" type="' + inputType + '" /></label></a></li>');

			var selected = $(element).prop('selected') || false;
			var $checkbox = $('input', $li);
			$checkbox.val(value);
		    if (value == 'select-all-option') $checkbox.parent().parent().addClass('multiselect-all');
			$('label', $li).append(" " + label);

			$('.multiselect-container ul', this.$container).append($li);

			if ($(element).is(':disabled')) {
				$checkbox.attr('disabled', 'disabled').prop('disabled', true).parents('li').addClass('disabled');
			}
			
			$checkbox.prop('checked', selected);

			if (selected && this.options.selectedClass) {
				$checkbox.parents('li').addClass(this.options.selectedClass);
			}
		},

		// Build the dropdown and bind event handling.
		buildDropdown: function () {
			$('.multiselect-container', this.$container).html('<ul style="list-style-type: none;margin:0;padding:0;"></ul>');
			
			// Set max height of dropdown menu to activate auto scrollbar.
			if (this.options.maxHeight) {
			    $('.multiselect-container ul', this.$container).css({
					'max-height': this.options.maxHeight + 'px',
					'overflow-y': 'auto',
					'overflow-x': 'hidden'
				});
	
				$('input[type="text"]', this.$container).width('75%');
			}
			
		    var alreadyHasSelectAll = this.$select[0][0] ? this.$select[0][0].value == 'select-all-option' : false;
		    
			// If options.includeSelectAllOption === true, add the include all checkbox.
		    if (this.options.includeSelectAllOption && this.options.multiple && !alreadyHasSelectAll) {
				this.$select.prepend('<option value="select-all-option">' + this.options.selectAllText + '</option>');
		    }
		
			this.$select.children().each($.proxy(function (index, element) {
				// Support optgroups and options without a group simultaneously.
				var tag = $(element).prop('tagName').toLowerCase();
				if (tag == 'optgroup') {
					var group = element;
					var groupName = $(group).prop('label');
					
					// Add a header for the group.
					var $li = $('<li><label style="margin:0;padding:3px 20px 3px 20px;height:100%;" class="multiselect-group"></label></li>');
					$('label', $li).text(groupName);
					$('.multiselect-container ul', this.$container).append($li);
					
					// Add the options of the group.
					$('option', group).each($.proxy(function (index, element) {
						this.createOptionValue(element);
					}, this));
				}
				else if (tag == 'option') {
					this.createOptionValue(element);
				}
				else {
					// Ignore illegal tags.
				}
			}, this));
			
			// Bind the change event on the dropdown elements.
			$('.multiselect-container ul li input', this.$container).on('change', $.proxy(function (event) {
				var checked = $(event.target).prop('checked') || false;
				var isSelectAllOption = $(event.target).val() == 'select-all-option';
				
				// Apply or unapply the configured selected class.
				if (this.options.selectedClass) {
					if (checked) {
						$(event.target).parents('li').addClass(this.options.selectedClass);
					}
					else {
						$(event.target).parents('li').removeClass(this.options.selectedClass);
					}
				}

				var $option = $('option', this.$select).filter(function() {
					return $(this).val() == $(event.target).val();
				});
				
				var $optionsNotThis = $('option', this.$select).not($option);
				var $checkboxesNotThis = $('input', this.$container).not($(event.target));

				// Toggle all options if the select all option was changed.
				if (isSelectAllOption) {
					$checkboxesNotThis.filter(function () { return $(this).is(':checked') != checked; }).trigger('click');
				}
				
				if (checked) {
				    $option.prop('selected', true);
					
				    if (this.options.multiple) {
						$option.attr('selected', 'selected');
				    }
				    else {
						if (this.options.selectedClass) {
							$($checkboxesNotThis).parents('li').removeClass(this.options.selectedClass);
						}

						$($checkboxesNotThis).prop('checked', false);
 
						$optionsNotThis.removeAttr('selected').prop('selected', false);

						// It's a single selection, so close.
						$(this.$container).find(".multiselect.dropdown-toggle").click();
					}

					if (this.options.selectedClass == "active") {
						$optionsNotThis.parents("a").css("outline", "");
					}					

				}
				else {
					$option.removeAttr('selected').prop('selected', false);
				}
				
				this.updateButtonText();

				this.options.onChange($option, checked);

				this.$select.change();
			}, this));

			$('.multiselect-container ul li a', this.$container).on('touchstart click', function (event) {
				event.stopPropagation();
			});

			// Keyboard support.
			this.$container.on('keydown', $.proxy(function (event) {
			    if ($('input[type="text"]', this.$container).is(':focus')) return;
				if ((event.keyCode == 9 || event.keyCode == 27) && this.$container.hasClass('open')) {
					// Close on tab or escape.
					$(this.$container).find(".multiselect.dropdown-toggle").click();
				}
				else {
					var $items = $(this.$container).find("li:not(.divider):visible a");

					if (!$items.length) {
						return;
					}

					var index = $items.index($items.filter(':focus'));

					// Navigation up.
					if (event.keyCode == 38 && index > 0) {
						index--;
					}
					// Navigate down.
					else if (event.keyCode == 40 && index < $items.length - 1) {
						index++;
					}
					else if (!~index) {
						index = 0;
					}

					var $current = $items.eq(index);
					$current.focus();

					// Override style for items in li:active.
					if (this.options.selectedClass == "active") {
						$current.css("outline", "thin dotted #333").css("outline", "5px auto -webkit-focus-ring-color");

						$items.not($current).css("outline", "");
					}

					if (event.keyCode == 32 || event.keyCode == 13) {
						var $checkbox = $current.find('input');

						$checkbox.prop("checked", !$checkbox.prop("checked"));
						$checkbox.change();
					}

					event.stopPropagation();
					event.preventDefault();
				}
			}, this));
			
			// Enable filtering.
			if (this.options.enableFiltering) {
			    $('.multiselect-container', this.$container).prepend('<div class="input-prepend" style="padding:3px;"><span class="add-on"><i class="icon-search"></i></span><input class="multiselect-search" type="text" placeholder="' + this.options.filterPlaceholder + '"></div>');
			    
			    $('.multiselect-search', this.$container).val(this.query).on('click', function (event) {
			        event.stopPropagation();
			    }).on('keydown', $.proxy(function (event) {
			        // This is useful to catch "keydown" events after the browser has updated the control.
			        clearTimeout(this.searchTimeout);
			        
			        this.searchTimeout = this.asyncFunction($.proxy(function () {
			            var inputValue = event.target.value;
			            
			            if (inputValue != this.query) {
			                this.query = inputValue;
			                this.$select.empty();
	
			                var filteredValues = this.getFilteredOptions();
			                var newOptions = '';
			                for (var i = 0; i < filteredValues.length; i++) {
			                    var option = filteredValues[i];
			                    newOptions += '<option value="' + option.value + '">' + option.text + '</option>';
			                }
			                
			                this.$select.html(newOptions);
			                this.rebuild();
			            }
			        }, this), 300, this);
			    }, this));
			}
		},

		// Destroy - unbind - the plugin.
		destroy: function() {
			this.$container.remove();
			this.$select.show();
		},

		// Refreshs the checked options based on the current state of the select.
		refresh: function() {
			$('option', this.$select).each($.proxy(function(index, element) {
			    var $input = $('.multiselect-container ul li input', this.$container).filter(function () {
					return $(this).val() == $(element).val();
				});

				if ($(element).is(':selected')) {
					$input.prop('checked', true);

					if (this.options.selectedClass) {
						$input.parents('li').addClass(this.options.selectedClass);
					}
				}
				else {
					$input.prop('checked', false);

					if (this.options.selectedClass) {
						$input.parents('li').removeClass(this.options.selectedClass);
					}
				}

				if ($(element).is(":disabled"))	{
				    input.attr('disabled', 'disabled').prop('disabled', true).parents('li').addClass('disabled');
				}
				else {
				    input.removeAttr('disabled').prop('disabled', false).parents('li').removeClass('disabled');
				}				
			}, this));
			
			this.updateButtonText();
		},
		
		// Select an option by its value.
		select: function(value) {
			var $option = $('option', this.$select).filter(function () { return $(this).val() == value; });
			var $checkbox = $('.multiselect-container ul li input', this.$container).filter(function () { return $(this).val() == value; });
			
			if (this.options.selectedClass) {
				$checkbox.parents('li').addClass(this.options.selectedClass);
			}

			$checkbox.prop('checked', true);
			
			$option.attr('selected', 'selected').prop('selected', true);
			
			this.updateButtonText();
		},
		
		// Deselect an option by its value.
		deselect: function(value) {
			var $option = $('option', this.$select).filter(function () { return $(this).val() == value; });
			var $checkbox = $('.multiselect-container ul li input', this.$container).filter(function () { return $(this).val() == value; });

			if (this.options.selectedClass) {
				$checkbox.parents('li').removeClass(this.options.selectedClass);
			}

			$checkbox.prop('checked', false);
			
			$option.removeAttr('selected').prop('selected', false);
			
			this.updateButtonText();
		},
		
		// Rebuild the whole dropdown menu.
		rebuild: function() {
		    $('.multiselect-container', this.$container).html('');
			this.buildDropdown(this.$select, this.options);
			this.updateButtonText();
		},

		// Get options by merging defaults and given options.
		getOptions: function(options) {
			return $.extend({}, this.defaults, options);
		},
		
		updateButtonText: function() {
			var options = this.getSelected();
			$('button', this.$container).html(this.options.buttonText(options, this.$select));
		},
		
		// Get all selected options.
		getSelected: function () {
			return $('option:selected[value!="select-all-option"]', this.$select);
		},
		
		// Get filtered options.
		getFilteredOptions: function () {
		    if (this.query == '') return this.originalOptions;
		    var query = this.query;
		    
		    return $(this.originalOptions).filter(function () {
		        return this.text.substring(0, query.length) == query
	        });
	   },
	   
	   updateOriginalOptions: function() {
	        this.originalOptions = this.$select.clone()[0].options;
	   },
	   
	   asyncFunction: function (callback, timeout, self) {
		    var args = Array.prototype.slice.call(arguments, 3);
		    return setTimeout(function () {
		        callback.apply(self || window, args);
		    }, timeout);
		}
	};

    $.fn.multiselect = function(option, parameter) {
        return this.each(function() {
            var data = $(this).data('multiselect'),
                options = typeof option == 'object' && option;

            // Initialize the multiselect.
            if (!data) {
                $(this).data('multiselect', (data = new Multiselect(this, options)));
            }

            // Call multiselect method.
            if (typeof option == 'string') {
                data[option](parameter);
            }
        });
    };
	 
	$.fn.multiselect.Constructor = Multiselect;	 
	
	$(function() {
		$("select[data-role=multiselect]").multiselect();
	});
	
}(window.jQuery);
