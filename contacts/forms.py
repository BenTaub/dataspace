from django import forms
# from django.forms import ModelForm
from contacts.models import PersonDynamic


class ContactManageForm(forms.Form):
    # Used to edit a contact
    contact_static_id = forms.IntegerField()
    title = forms.CharField(max_length=20, required=False)
    first_name = forms.CharField(max_length=100, min_length=1)
    last_name = forms.CharField(max_length=50, min_length=1)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    # citizenship_status = forms.ChoiceField(choices=[(1, 'US Citizen'), (2, 'Other')], label='Citizenship',
    #                                        initial=2)

class ContactAddForm(ContactManageForm):
    def __init__(self, *args, **kwargs):
        super(ContactManageForm, self).__init__(*args, **kwargs)
        self.fields.pop('contact_static_id')

