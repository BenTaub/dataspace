from django import forms
# from django.forms import ModelForm
from contacts.models import PersonDynamic


class ContactAddForm(forms.Form):
    title = forms.CharField(max_length=20)
    first_name = forms.CharField(max_length=100, min_length=1)
    last_name = forms.CharField(max_length=50, min_length=1)
    notes = forms.CharField(widget=forms.Textarea)
    # citizenship_status = forms.ChoiceField(choices=[(1, 'US Citizen'), (2, 'Other')], label='Citizenship',
    #                                        initial=2)


# class ContactAddForm(forms.ModelForm):
#     class Meta:
#         model = PersonDynamic  # This makes the form build from the data structure - no need to specify fields
#         fields = '__all__'  # Required as of Django 1.8 if you want to use a ModelForm class
#         # exclude = ('person_static', 'current_record_fg', 'effective_date', 'end_date', )
#         widgets = {'person_static': forms.HiddenInput, 'current_record_fg': forms.HiddenInput,
#                    'effective_date': forms.HiddenInput, 'end_date': forms.HiddenInput}
#
#     title = forms.CharField(label='Title')

