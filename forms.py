from django import forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit
from django.utils.translation import ugettext_lazy as _
from .models import Entity, Location
from schedule.models import Event

class CalendarDateTimeWidget(forms.DateTimeInput):
    class Media:
        css = {
            'all': ('css/bootstrap-datetimepicker.min.css',)
        }
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

        self.fields['entity'].queryset = Entity.objects.filter(owner=owner).order_by('name')
        self.fields['location'].queryset = Location.objects.order_by('city', 'name')

        # http://tothinkornottothink.com/post/7157151391/be-careful-how-you-use-static-variables-in-forms
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Create a meeting',
                'entity',
                'start',
                'location',
                'agenda',
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

    # Make "title" & "end" fields not required so we can set this field value
    # programmatically in form_valid of MeetingCreateView in views.py
    title = forms.CharField(required=False)
    end = forms.DateTimeField(required=False)

    def clean(self):
        cleaned_data = super(MeetingCreateViewForm, self).clean()
        contact_email = cleaned_data.get('contact_email')
        contact_phone = cleaned_data.get('contact_phone')
        website = cleaned_data.get('website')
        start = cleaned_data.get('start')
        location = cleaned_data.get('location')
        meeting_id = self.instance.id

        if not contact_email and not contact_phone and not website:
            raise forms.ValidationError(
                '''You must fill in at least one of the three fields below:
                "Contact phone," "Contact email" or "Website."'''
            )

        #
        # This check appears to be using out-of-date arguments, backing out ... 
        #
        # try:
        #     already_exists = Event.objects.exclude(id=meeting_id).get(start=start, location=location)
        #     raise forms.ValidationError(
        #         '''An event starting at this time at this location already exists: 
        #         {0}'''.format(already_exists.__str__())
        #     )
        # except Event.DoesNotExist:
        #     already_exists = None

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
            'location': _('<div class="alert alert-info"><a href="mailto:webdesk@registerguard.com?subject=Civic%20calendar%20app%20meeting%20location%20suggestion">Not finding an address? <b>Suggest</b></a> a meeting location.</div>'),
            'agenda': _('<div class="alert alert-info"><b>OPTIONAL</b>: A <b><i>brief</i></b> description of agenda. <a href="#calendar-examples"><b>See the examples below</b></a> or check the Calendar item in <i>The Register-Guard</i> City/Region section for others.<br><b>Note:</b> 500-character limit.</div>'),
            'website': _(
                '''
                <div class="alert alert-info">
                    You must supply at least one of <b>Contact phone</b>, <b>Contact email</b>, <b>Website</b>; the more, the merrier.
                </div>
                '''
            ),
        }
    # https://docs.djangoproject.com/en/1.10/ref/forms/api/#django.forms.Form.use_required_attribute
    # Removes HTML5 standalone 'required' attribute from form tags as client-side form validation was
    # halting the POST/server-side validation & subsequent form.errors.
    use_required_attribute = False
