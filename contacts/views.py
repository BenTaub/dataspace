from django.shortcuts import render
from contacts.forms import ContactAddForm
import contacts.models
from django.http import HttpResponseRedirect
import datetime
from django.db import transaction


# Create your views here.
def contact_add(request):
    if request.method == 'POST':
        form = ContactAddForm(request.POST)
        if form.is_valid():
            form.clean()
            curr_datetime = datetime.datetime.now()
            new_contact_static = contacts.models.PersonStatic(
                effective_date = curr_datetime, end_date = curr_datetime, current_record_fg = True)
            #todo: Need to do this in a transaction & to drop out if first insert fails
            try:
                with transaction.atomic():  # Starts a transaction
                    new_contact_static.save()

                    new_contact_dynamic = contacts.models.PersonDynamic (
                        person_static = new_contact_static, effective_date = curr_datetime, end_date = curr_datetime,
                        current_record_fg = True, title = form.data['title'], first_name = form.data['first_name'],
                        last_name = form.data['last_name'], notes = form.data['notes'],
                        citizenship_status = form.data['citizenship_status'])
                    new_contact_dynamic.save()
            except:
                pass
    else:
        form = ContactAddForm

    return render(request, 'contact_add.html', {'form': form})
