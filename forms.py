from django import forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit
from django.utils.translation import ugettext_lazy as _
from .models import Entity, Location
from schedule.models import Event

class CalendarDateTimeWidget(forms.DateTimeInput):
    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.15.0/moment.min.js',
            'js/bootstrap-datetimepicker.min.js',
        )


class MeetingCreateViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # passed by get_form_kwargs override in views.MeetingCreateView
        owner = kwargs.pop('owner')
        # now kwargs don't contain 'owner', so we can safely pass it to the
        # base class method
        super(MeetingCreateViewForm, self).__init__(*args, **kwargs)

        # http://tothinkornottothink.com/post/7157151391/be-careful-how-you-use-static-variables-in-forms
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Create a meeting',
                'entity',
                'start',
                'title',
                'location',
                'agenda',
                'description',
                'contact_phone',
                'contact_email',
                'website',
            ),
            FormActions(
                Submit('submit', 'Save',),
            )
        )
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        # Don't hardwire form to one URL! Then we can use same form to create or
        # update. i.e., don't set "self.helper.form_action = 'create'"

    # Make "end" field not required we can set this field value
    # programmatically in form_valid of MeetingCreateView in views.py
    end = forms.DateTimeField(required=False)

    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'start': CalendarDateTimeWidget(),
            'agenda': forms.Textarea(
                attrs={
                    'maxlength': '500',
                }
            ),
        }
        help_texts = {
            'start': _('<div class="alert alert-info"><b>Note:</b> Use military time: e.g., 1 p.m. is 13:00.</div>'),
            'location': _('<div class="alert alert-info"><a href="mailto:webeditors@registerguard.com?subject=Civic%20calendar%20app%20meeting%20location%20suggestion">Not finding an address? <b>Suggest</b></a> a meeting location.</div>'),
            'agenda': _('<div class="alert alert-info"><b>OPTIONAL</b>: A <b><i>brief</i></b> description of agenda. <a href="#calendar-examples"><b>See the examples below</b></a> or check the Calendar item in <i>The Register-Guard</i> City/Region section for others.<br><b>Note:</b> 500-character limit.</div>'),
        }
    # https://docs.djangoproject.com/en/1.10/ref/forms/api/#django.forms.Form.use_required_attribute
    # Removes HTML5 standalone 'required' attribute from form tags as client-side form validation was
    # halting the POST/server-side validation & subsequent form.errors.
    use_required_attribute = False
