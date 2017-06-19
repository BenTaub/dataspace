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
    def build_col_sort(sort_orders: list):
        """
        Creates the sort order portion of the queryset
        :param sort_orders: A list of the columns to sort
        :return: str - the order by portion of the queryset call
        """
        # TODO: Modify this to allow sorting by multiple columns and in different directions. Can't figure
        # out how to do this with Django querysets,

        ret_val = "Lower("
        for this_col in sort_orders:
            ret_val += "'" + this_col + "',"
        ret_val = ret_val[:len(ret_val) -1]  # Trim off the last comma
        ret_val += ")"

        # ret_val = "(Lower('effective_date', 'last_name'))" --> Doesn't work!
        # ret_val = "(-(Lower('last_name')))" --> Doesn't work!
        # ret_val = "Lower('effective_date')" --> works
        # ret_val = "Lower('effective_date').desc()" --> works
        # ret_val = "Lower('last_name').desc()"  --> This one works!
        # ret_val = "Lower('last_name').desc(), 'effective_date'" --> doesn't work
        return ret_val

    if request.method == 'POST':  # View is called b/c someone hit the 'new' button
        #TODO: Add capability to sort by column head, filter, clear filter
        return HttpResponseRedirect(redirect_to='/contact/edit')  # Go to the edit form

    # Put the contact list on the screen
    hdr_fields = ['person_static_id', 'title', 'first_name', 'last_name', 'notes', 'effective_date']
    if 'contact_list_sort' not in request.session:
        request.session['contact_list_sort'] = ['last_name']

    # TODO: REPLACE THIS WITH THE SORT VALUES CHOSEN BY THE USER
    request.session['contact_list_sort'] = ['last_name']

    qs_data = contacts.models.PersonDynamic.objects.values_list(*hdr_fields).\
        order_by(eval(build_col_sort(request.session['contact_list_sort'])))
        # order_by(eval(tmp))

    # qs_data = contacts.models.PersonDynamic.objects.values_list(*hdr_fields).order_by(Lower('last_name').desc(), 'effective_date')


    hdr_fields = ('id', 'TITLE', 'FIRST NAME', 'LAST NAME', 'NOTES', 'LAST UPDATE')
    # BUILD LOGIC TO SAVE SESSION & USE VARIABLES ABOUT CONTACT_LIST SORT ORDER
    request.session['session_tester'] = 'This is a session variable!'

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
