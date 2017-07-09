from django import forms
from django.forms import ModelForm
from contacts.models import AddrElectronic


class ContactManageForm(forms.Form):
    # Used to edit a contact
    id = forms.IntegerField(widget=forms.HiddenInput)
    person_static_id = forms.IntegerField(widget=forms.HiddenInput)
    title = forms.CharField(max_length=20, required=False)
    first_name = forms.CharField(max_length=100, min_length=1, required=False)
    last_name = forms.CharField(max_length=50, min_length=1)
    notes = forms.CharField(widget=forms.Textarea, required=False)


class ContactAddForm(ContactManageForm):
    """Used when we are adding a new contact"""
    def __init__(self, *args, **kwargs):
        super(ContactManageForm, self).__init__(*args, **kwargs)
        self.fields.pop('person_static_id')
        self.fields.pop('id')


class ElectronicAddressManageForm(ModelForm):
    """Used to add and manage electronic contact addresses"""
    addr_type = forms.ChoiceField(choices=AddrElectronic._meta.get_field('addr_type').choices)
    # addr_type = forms.ChoiceField(choices=[('email', 'email'), ('url', 'url')]) --> This works!!!!

    class Meta:
        model = AddrElectronic
        fields = ['id', 'person_dynamic', 'name', 'value', 'display_seq']
        widgets = {'id': forms.HiddenInput, 'person_dynamic': forms.HiddenInput}
        #TODO: Start by getting this to work!!!

                   # 'addr_type': forms.ChoiceField(choices=AddrElectronic._meta.get_field('addr_type').choices)}
        # current_record_fg
        # effective_date =
        # end_date = models]
