"""
Form Widget classes specific to the Django admin site.
"""
from __future__ import absolute_import
from itertools import chain
from django import forms
try:
    from django.forms.widgets import ChoiceWidget as RadioChoiceInput
except:
    from django.forms.widgets import RadioFieldRenderer, RadioChoiceInput
from django.utils.encoding import force_text

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.translation import ugettext as _

from .util import vendor


class AdminDateWidget(forms.DateInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'datepicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'date-field form-control', 'size': '10'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminDateWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super(AdminDateWidget, self).render(name, value, attrs, renderer)
        return mark_safe('<div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Today')))


class AdminTimeWidget(forms.TimeInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'clockpicker.js', 'clockpicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'time-field form-control', 'size': '8'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTimeWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super(AdminTimeWidget, self).render(name, value, attrs, renderer)
        return mark_safe('<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Now')))


class AdminSelectWidget(forms.Select):

    @property
    def media(self):
        return vendor('select.js', 'select.css', 'xadmin.widget.select.js')


class AdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """

    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs, renderer).replace('><input', '>\n<input').split('\n') if ht != '']
        # return input_html
        return mark_safe('<div class="datetime clearfix"><div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>'
                         '<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div></div>' % (input_html[0], _(u'Today'), input_html[1], _(u'Now')))

    def format_output(self, rendered_widgets):
        return mark_safe(u'<div class="datetime clearfix">%s%s</div>' %
                         (rendered_widgets[0], rendered_widgets[1]))


class AdminRadioInput(RadioChoiceInput):

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        attrs['class'] = attrs.get('class', '').replace('form-control', '')
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_text(self.choice_label))
        if attrs.get('inline', False):
            return mark_safe(u'<label%s class="radio-inline">%s %s</label>' % (label_for, self.tag(), choice_label))
        else:
            return mark_safe(u'<div class="radio"><label%s>%s %s</label></div>' % (label_for, self.tag(), choice_label))


class AdminRadioFieldRenderer(forms.RadioSelect):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield AdminRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return AdminRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

    def render(self):
        return mark_safe(u'\n'.join([force_text(w) for w in self]))


class AdminRadioSelect(forms.RadioSelect):
    renderer = AdminRadioFieldRenderer


class AdminCheckboxSelect(forms.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        output = []
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))

            if final_attrs.get('inline', False):
                output.append(u'<label%s class="checkbox-inline">%s %s</label>' % (label_for, rendered_cb, option_label))
            else:
                output.append(u'<div class="checkbox"><label%s>%s %s</label></div>' % (label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))


class AdminSelectMultiple(forms.SelectMultiple):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'select-multi'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminSelectMultiple, self).__init__(attrs=final_attrs)


class AdminFileWidget(forms.ClearableFileInput):
    template_with_initial = (u'<p class="file-upload">%s</p>'
                             % forms.ClearableFileInput.initial_text)
    template_with_clear = (u'<span class="clearable-file-input">%s</span>'
                           % forms.ClearableFileInput.clear_checkbox_label)


class AdminTextareaWidget(forms.Textarea):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'textarea-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextareaWidget, self).__init__(attrs=final_attrs)


class AdminTextInputWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'text-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextInputWidget, self).__init__(attrs=final_attrs)


class AdminURLFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'url-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminURLFieldWidget, self).__init__(attrs=final_attrs)


class AdminIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminIntegerFieldWidget, self).__init__(attrs=final_attrs)


class AdminCommaSeparatedIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'sep-int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminCommaSeparatedIntegerFieldWidget,
              self).__init__(attrs=final_attrs)
