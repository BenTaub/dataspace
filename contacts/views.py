from django.shortcuts import render
from contacts.forms import ContactManageForm,ContactAddForm
import contacts.models
from django.http import HttpResponseRedirect
import datetime
from django.db import transaction
import contacts.models

# Create your views here.
def contact_list(request):
    if request.method == 'POST':
        return HttpResponseRedirect(redirect_to='/contact/edit')

    hdr_fields = ['person_static_id', 'title', 'first_name', 'last_name', 'notes', ]
    qs_data = contacts.models.PersonDynamic.objects.values_list(*hdr_fields)
    hdr_fields = ('id', 'TITLE', 'FIRST NAME', 'LAST NAME', 'NOTES')

    return render(request, template_name='contact_list.html', context={'all_contacts': qs_data, 'col_hdrs': hdr_fields})


def contact_add(request):
    if request.method == 'POST':
        form = ContactAddForm(request.POST)
        if form.is_valid():
            form.clean()
            curr_datetime = datetime.datetime.now()
            new_contact_static = contacts.models.PersonStatic(
                effective_date = curr_datetime, end_date = curr_datetime, current_record_fg = True)
            try:
                with transaction.atomic():  # Starts a transaction
                    # TODO: Extend PersonDynamic.save with this code
                    # TODO: Need to drop out if first insert fails + test if xsaction works(what happens to static key?)
                    new_contact_static.save()

                    new_contact_dynamic = contacts.models.PersonDynamic (
                        person_static = new_contact_static, effective_date = curr_datetime, end_date = curr_datetime,
                        current_record_fg = True, title = form.data['title'], first_name = form.data['first_name'],
                        last_name = form.data['last_name'], notes = form.data['notes'])
                        # citizenship_status = form.data['citizenship_status'])
                    new_contact_dynamic.save()
                # The following ensures that the user doesn't hit enter twice
                # Modify it to redirect to a page that shows the new contact & allows user to add another or go to main list
                return HttpResponseRedirect('')
            except:
                pass
        else:
            # TODO: Put error handling code in here!!!
            pass
    else:
        form = ContactAddForm()

    return render(request, 'contact_manage.html', {'form': form})
