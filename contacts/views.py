from django.shortcuts import render
from contacts.forms import ContactManageForm, ContactAddForm, ElectronicAddressManageForm, \
    ElectronicAddressFormSet, AddrElectronic
import contacts.models
from django.http import HttpResponseRedirect
from django.db.models.functions import Lower
from django.forms import formset_factory, ChoiceField
import contacts.models


# Create your views here.
def contact_list(request: object):
    """
    Shows the contact_list screen, the first contact screen
    :param request:
    :return:
    """
    # Put the contact list on the screen
    if 'contact_list_settings' not in request.session:
        request.session['contact_list_settings'] = \
            [{'db_col': 'person_static_id', 'screen_hdr': 'ID', 'type': 'number'},
             {'db_col': 'title', 'screen_hdr': 'TITLE', 'type': 'text'},
             {'db_col': 'first_name', 'screen_hdr': 'FIRST NAME', 'type': 'text'},
             {'db_col': 'last_name', 'screen_hdr': 'LAST NAME', 'sorted': 'Asc', 'type': 'text'},
             {'db_col': 'notes', 'screen_hdr': 'NOTES', 'type': 'textarea'},
             {'db_col': 'effective_date', 'screen_hdr': 'AS OF', 'type': 'date'}]

    if 'btn_sort' in request.GET:
        # Set new sort & clear old one
        for ndx in range(len(request.session['contact_list_settings'])):  # NOTE: Range does not use the highest value!
            if 'sorted' in request.session['contact_list_settings'][ndx]:  # This column was the last sort
                # Change the sort order
                if request.session['contact_list_settings'][ndx]['screen_hdr'] == request.GET['btn_sort']:
                    if request.session['contact_list_settings'][ndx]['sorted'] == 'Asc':
                        request.session['contact_list_settings'][ndx]['sorted'] = 'Desc'
                    else:
                        request.session['contact_list_settings'][ndx]['sorted'] = 'Asc'
                else:  # We're not sorting by this anymore
                    del request.session['contact_list_settings'][ndx]['sorted']

            # This is the new col to sort by
            elif request.session['contact_list_settings'][ndx]['screen_hdr'] == request.GET['btn_sort']:
                request.session['contact_list_settings'][ndx]['sorted'] = 'Desc'

    # list comprehension to get the list of db column names!
    db_col_list = [col['db_col'] for col in request.session['contact_list_settings']]

    # Store the new filter in the session variables
    if 'btn_filter' in request.GET:
        # Clear out old filters & put in new ones
        for session_col in request.session['contact_list_settings']:
            if 'filter' in session_col:
                session_col.pop('filter')
            if session_col['db_col'] in request.GET.keys() and request.GET[session_col['db_col']] != '':
                session_col['filter'] = request.GET[session_col['db_col']]

    if 'btn_clear_filter' in request.GET:
        for session_col in request.session['contact_list_settings']:
            if 'filter' in session_col:
                session_col.pop('filter')

    request.session.save()  # Without this we were losing the new sort order

    # Generator expression to get sort order!
    # TODO: Sorts treat everything as alphanumeric. Change this so they sort ints the right way
    db_sort_col_dict = next(
        db_sort_ord for db_sort_ord in request.session['contact_list_settings'] if 'sorted' in db_sort_ord)
    db_sort_col = db_sort_col_dict['db_col']
    db_sort_ord = db_sort_col_dict['sorted']

    # Build the filter
    qry_filter = {'current_record_fg': True}
    for col in request.session['contact_list_settings']:
        if 'filter' in col and col['filter'] != None:
            if col['type'] =='number':
                dict_key = col['db_col']
            elif col['type'] == 'date':
                dict_key = col['db_col'] + "__date"
            else:
                dict_key = col['db_col'] + "__istartswith"
            qry_filter[dict_key]  = col['filter']

    # Query the DB
    #TODO: change order_by to this, Django syntax: order_by(*fields) --> ignore lowercase issues, it's DB dependent
    #TODO: add top email & ph number to this query from their related tables
    if db_sort_ord == 'Asc':
        qs_data = contacts.models.PersonDynamic.objects.filter(**qry_filter).values_list(*db_col_list).\
            order_by(Lower(db_sort_col))
    else:
        qs_data = contacts.models.PersonDynamic.objects.filter(**qry_filter).values_list(*db_col_list).\
            order_by(Lower(db_sort_col).desc())

    # hdr_fields = [col['screen_hdr'] for col in request.session['contact_list_settings']]

    return render(request, template_name='contact_list.html',
                  context={'all_contacts': qs_data, 'col_meta': request.session['contact_list_settings']})


def contact_manage(request):
    """
    Handles requests to add, view, and manage contacts
    :param request: A Django request object
    :return:
    """
    #TODO: Need an 'are you sure' if user entered data but then goes to list
    if 'id' not in request.GET:  # This is a request for a contact that's not in the DB yet
        if request.method == 'GET':  # This is a request to show a blank entry form_contact
            form_contact = ContactAddForm()
            electronic_addr_formset_class = formset_factory(ElectronicAddressManageForm)
            electronic_addr_formset = electronic_addr_formset_class(request.POST, prefix='e_addr')
            return render(request, 'contact_manage.html',
                          {'form_contact': form_contact, 'formset_e_addr': electronic_addr_formset})
            # return render(request, 'contact_manage.html', {'form_contact': form_contact})
        else:  # This is a request to put entered data into a new contact
            form_contact = ContactAddForm(request.POST)
            if form_contact.has_changed():  # There actually was data typed into the blank form_contact
                new_contact_dynamic = contacts.models.PersonDynamic(
                    title=form_contact.data['title'], first_name=form_contact.data['first_name'],
                    last_name=form_contact.data['last_name'], notes=form_contact.data['notes'])
                new_contact_dynamic.create()
                return HttpResponseRedirect(redirect_to='/contact/edit/?id=' +
                                                        str(new_contact_dynamic.person_static.id))
            return render(request, 'contact_manage.html', {'form_contact': form_contact})

    # We must have received an ID so this is a request to get or update or delete an existing contact
    # TODO: Do we need to handle the possibility that the following doesn't return a record?
    qry_filters = {'person_static': request.GET['id'], 'current_record_fg': True}
    new_contact_dynamic = contacts.models.PersonDynamic.objects.get(**qry_filters)
    electronic_addresses = contacts.models.AddrElectronic.objects.filter(**qry_filters)
    if request.method == "GET":  # This is a request to show an existing contact
        form_contact = ContactManageForm(new_contact_dynamic.__dict__)
        # electronic_addr_formset_class = formset_factory(ElectronicAddressManageForm)
        # electronic_addr_formset = electronic_addr_formset_class(initial=electronic_addresses.values(),
        #                                                         prefix='e_addr')

        electronic_addr_formset = ElectronicAddressFormSet(queryset=electronic_addresses, prefix='e_addr')
        # electronic_addr_formset = ElectronicAddressFormSet(
        #     queryset=electronic_addresses,
        #     initial=[{'addr_type': ChoiceField(choices=AddrElectronic._meta.get_field('addr_type').choices)}])

        return render(request, 'contact_manage.html',
                      {'form_contact': form_contact, 'formset_e_addr': electronic_addr_formset})

    form_contact = ContactManageForm(request.POST, initial=new_contact_dynamic.__dict__)
    #TODO: NEED TO PUT IN STUFF FOR FORM_EADDRESSES
    if request.POST.get("delete"):
        # TODO: Put in some 'are you sure?' code
        new_contact_dynamic.delete()
        return HttpResponseRedirect(redirect_to='/contact/list/')

    if not form_contact.has_changed():
        # Form didn't change so just display it again
        return render(request, 'contact_manage.html', {'form_contact': form_contact})

    # Only option left is that this is a request to update an existing contact
    if form_contact.is_valid():
        form_contact.clean()
        try:
            new_contact_dynamic.title = form_contact.data['title']
            new_contact_dynamic.first_name = form_contact.data['first_name']
            new_contact_dynamic.last_name = form_contact.data['last_name']
            new_contact_dynamic.notes = form_contact.data['notes']
            new_contact_dynamic.update()
            # The following ensures that the user doesn't hit enter twice
            return HttpResponseRedirect(redirect_to='/contact/edit/?id='+form_contact.data['person_static_id'])
        except:
            # TODO: Do something here!!!
            print("ERROR!")
    else:
        # TODO: Put error handling code in here for a bad form_contact!!!
        pass
    return render(request, 'contact_manage.html', {'form_contact': form_contact})


def electronic_addr_manage(request):
    """Manage email, phone and other, non-physical addresses"""
    electronic_addr_formset = formset_factory(ElectronicAddressManageForm)
    # electronic_addr_formset_class = formset_factory(ElectronicAddressManageForm)
    # electronic_addr_formset = electronic_addr_formset_class(request.POST, prefix='e_addr')
    # electronic_addr_formset = electronic_addr_formset_class(request.POST, prefix='e_addr')
    return render(request, 'electronic_address_manage.html', {'formset_e_addr': electronic_addr_formset})
