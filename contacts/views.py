from django.shortcuts import render
from contacts.forms import ContactManageForm,ContactAddForm
import contacts.models
from django.http import HttpResponseRedirect
import datetime
from django.db import transaction, Error
from django.db.models.functions import Lower
import contacts.models

# Create your views here.
def contact_list(request: object):
    """
    Shows the contact_list screen, the first contact screen
    :param request:
    :return:
    """
    # Put the contact list on the screen
    # TODO: Add ability to filter the data & clear filters

    if 'contact_list_settings' not in request.session:
        request.session['contact_list_settings'] = \
            [{'db_col': 'person_static_id', 'screen_hdr': 'ID'},
             {'db_col': 'title', 'screen_hdr': 'TITLE'},
             {'db_col': 'first_name', 'screen_hdr': 'FIRST NAME'},
             {'db_col': 'last_name', 'screen_hdr': 'LAST NAME', 'sorted': 'Asc'},
             {'db_col': 'notes', 'screen_hdr': 'NOTES'},
             {'db_col': 'effective_date', 'screen_hdr': 'AS OF'}]

    if 'btn_sort' in request.GET:
        # Set new sort & clear old one
        for ndx in range(len(request.session['contact_list_settings'])):  # NOTE: Range does not use the highest value!
            if 'sorted' in request.session['contact_list_settings'][ndx]:  # This column was the last sort
                if request.session['contact_list_settings'][ndx]['screen_hdr'] == request.GET['btn_sort']:  # Change the sort order
                    if request.session['contact_list_settings'][ndx]['sorted'] == 'Asc':
                        request.session['contact_list_settings'][ndx]['sorted'] = 'Desc'
                    else:
                        request.session['contact_list_settings'][ndx]['sorted'] = 'Asc'
                else:  # We're not sorting by this anymore
                    del request.session['contact_list_settings'][ndx]['sorted']

            # This is the new col to sort by
            elif request.session['contact_list_settings'][ndx]['screen_hdr'] == request.GET['btn_sort']:
                request.session['contact_list_settings'][ndx]['sorted'] = 'Desc'

    request.session.save()  # Without this we were losing the new sort order

    # list comprehension to get the list of db column names!
    db_col_list = [col['db_col'] for col in request.session['contact_list_settings']]

    # Generator expression to get sort order!
    db_sort_col_dict = next(db_sort_ord
                       for db_sort_ord in request.session['contact_list_settings'] if 'sorted' in db_sort_ord)
    db_sort_col = db_sort_col_dict['db_col']
    db_sort_ord = db_sort_col_dict['sorted']
    # TODO: Sorts treat everything as alphanumeric. Change this so they sort ints the right way

    # Query the DB
    if db_sort_ord == 'Asc':
        qs_data = contacts.models.PersonDynamic.objects.exclude(current_record_fg=False).values_list(*db_col_list).\
            order_by(Lower(db_sort_col))
    else:
        qs_data = contacts.models.PersonDynamic.objects.exclude(current_record_fg=False).values_list(*db_col_list).\
            order_by(Lower(db_sort_col).desc())

    hdr_fields = [col['screen_hdr'] for col in request.session['contact_list_settings']]

    return render(request, template_name='contact_list.html',
                  context={'all_contacts': qs_data, 'col_meta': request.session['contact_list_settings']})


def contact_manage(request):
    # TODO: NEED TO HANDLE DELETE!!! It should just be setting end dates & removing current record flags
    curr_datetime = datetime.datetime.now()
    if 'id' not in request.GET:  # This is a request for a contact that's not in the DB yet
        if request.method == 'GET':  # This is a request to show a blank entry form
            form = ContactAddForm()
            return render(request, 'contact_manage.html', {'form': form})
        else:  # This is a request to put entered data into a new contact
            form = ContactAddForm(request.POST)
            if form.has_changed():  # There actually was data typed into the blank form
                #TODO: Move this to the models module
                try:
                    with transaction.atomic():  # Starts a transaction
                        new_contact_static = contacts.models.PersonStatic(
                            effective_date=curr_datetime, current_record_fg=True)
                        new_contact_static.save()
                        # TODO: Need to drop out if first insert fails + test if xsaction works(what happens to # static key?)
                        new_contact_dynamic = contacts.models.PersonDynamic(
                            person_static=new_contact_static, effective_date=curr_datetime,
                            current_record_fg=True, title=form.data['title'], first_name=form.data['first_name'],
                            last_name=form.data['last_name'], notes=form.data['notes'])
                        new_contact_dynamic.save()
                        return HttpResponseRedirect(redirect_to='/contact/edit/?id=' + str(new_contact_static.id))
                except Error as db_err:
                    # TODO: Do something here!!!
                    print(str(db_err))
            return render(request, 'contact_manage.html', {'form': form})

    # We must have received an ID so this is a request to get or update an existing contact
    # TODO: Do we need to handle the possibility that the following doesn't return a record?
    new_contact_dynamic = contacts.models.PersonDynamic.objects.get(person_static=request.GET['id'],
                                                                        current_record_fg=True)
    if request.method == "GET":  # This is a request to show an existing contact
        form = ContactManageForm(new_contact_dynamic.__dict__)
        return render(request, 'contact_manage.html', {'form': form})

    # Only option left is that this is a request to update an existing contact
    form = ContactManageForm(request.POST, initial=new_contact_dynamic.__dict__)
    if not form.has_changed():
        #TODO: Check here in request.POST to see if the delete key was hit. If so, delete the contact!!
        return render(request, 'contact_manage.html', {'form': form})
    if form.is_valid():
        form.clean()
        try:
            # TODO: Move db code into the models module
            with transaction.atomic():  # Starts a transaction
                # TODO: Extend PersonDynamic.save with this code
                # Deactivate the old record
                old_contact_dynamic = contacts.models.PersonDynamic (
                    id = form.data['id'])
                old_contact_dynamic.end_date = curr_datetime
                old_contact_dynamic.current_record_fg = False
                old_contact_dynamic.save(update_fields=['end_date', 'current_record_fg'], force_update=True)
                # Now insert the new record!!!!
                new_contact_dynamic = contacts.models.PersonDynamic (
                    person_static_id=form.data['person_static_id'], effective_date = curr_datetime,
                    current_record_fg = True, title = form.data['title'], first_name = form.data['first_name'],
                    last_name = form.data['last_name'], notes = form.data['notes'])
                new_contact_dynamic.save(force_insert=True)
                # The following ensures that the user doesn't hit enter twice
                return HttpResponseRedirect(redirect_to='/contact/edit/?id='+form.data['person_static_id'])

        except Error as db_err:
            # TODO: Do something here!!!
            print(str(db_err))
    else:
        # TODO: Put error handling code in here for a bad form!!!
        pass
    return render(request, 'contact_manage.html', {'form': form})
