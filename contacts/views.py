from django.shortcuts import render
from contacts.forms import ContactManageForm,ContactAddForm
import contacts.models
from django.http import HttpResponseRedirect
import datetime
from django.db import transaction
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
    # TODO: Add capability to sort asc or desc by column head
    # TODO: Add ability to filter the data & clear filters
    # TODO: Do an if sorted key exists and an if filter value

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
        #TODO: Get rid of the col and just go to len of the request.session dict
        for ndx in range(len(request.session['contact_list_settings'])):  # Range does not use the highest value!
            if 'sorted' in request.session['contact_list_settings'][ndx]:  # This column was the last sort
                if request.session['contact_list_settings'][ndx]['screen_hdr'] == request.GET['btn_sort']:  # Change the sort order
                    if request.session['contact_list_settings'][ndx]['sorted'] == 'Asc':
                        request.session['contact_list_settings'][ndx]['sorted'] = 'Desc'
                    else:
                        request.session['contact_list_settings'][ndx]['sorted'] = 'Asc'
                else:  # We're not sorting by this anymore
                    del request.session['contact_list_settings'][ndx]['sorted']

            elif request.session['contact_list_settings'][ndx]['screen_hdr'] == request.GET['btn_sort']:  # This is the new col to sort by
                request.session['contact_list_settings'][ndx]['sorted'] = 'Desc'

    request.session.save()  # Without this we were losing the new sort order

    # list comprehension!
    db_col_list = [col['db_col'] for col in request.session['contact_list_settings']]

    # Generator expression to get sort order!
    db_sort_col_dict = next(db_sort_ord
                       for db_sort_ord in request.session['contact_list_settings'] if 'sorted' in db_sort_ord)
    db_sort_col = db_sort_col_dict['db_col']
    db_sort_ord = db_sort_col_dict['sorted']
    #TODO: Sorts treat everything as alphanumeric. Change this so they sort ints the right way

    # Query the DB
    if db_sort_ord == 'Asc':
        qs_data = contacts.models.PersonDynamic.objects.values_list(*db_col_list).\
            order_by(Lower(db_sort_col))
    else:
        qs_data = contacts.models.PersonDynamic.objects.values_list(*db_col_list).\
            order_by(Lower(db_sort_col).desc())

    hdr_fields = [col['screen_hdr'] for col in request.session['contact_list_settings']]
    #TODO: BUILD LOGIC TO SAVE SESSION & USE VARIABLES ABOUT CONTACT_LIST SORT ORDER

    return render(request, template_name='contact_list.html',
                  context={'all_contacts': qs_data, 'col_meta': request.session['contact_list_settings']})


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
