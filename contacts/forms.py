from django import forms
# from django.forms import ModelForm
# from contacts.models import PersonDynamic


class ContactManageForm(forms.Form):
    # Used to edit a contact
    id = forms.IntegerField(widget=forms.HiddenInput)
    person_static_id = forms.IntegerField(widget=forms.HiddenInput)
    title = forms.CharField(max_length=20, required=False)
    first_name = forms.CharField(max_length=100, min_length=1, required=False)
    last_name = forms.CharField(max_length=50, min_length=1)
    notes = forms.CharField(widget=forms.Textarea, required=False)


class ContactAddForm(ContactManageForm):
    def __init__(self, *args, **kwargs):
        super(ContactManageForm, self).__init__(*args, **kwargs)
        self.fields.pop('person_static_id')
        self.fields.pop('id')
