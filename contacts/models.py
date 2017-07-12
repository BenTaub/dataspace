from django.db import models, transaction, Error
import django.utils.timezone
import datetime

# Create your models here.

class PersonStatic(models.Model):
    # This is info about the person that never changes and serves as a place on which to build relationships
    # For the time being, the only field on this table is the person key
    current_record_fg = models.BooleanField(verbose_name="Current record flag", default=True,
                                      help_text="Set to True for the current version of the record")
    effective_date = models.DateTimeField(verbose_name="Record effective date", default=django.utils.timezone.now,
                                          help_text="The date & time on which this record became active")
    end_date = models.DateTimeField(verbose_name="Record end date",
                                    help_text="The date and time on which this record expired", blank=True, null=True)


class PersonDynamic(models.Model):
    person_static = models.ForeignKey(to=PersonStatic, verbose_name="Time independent person ID",
                                  help_text="A link to the key for this person that never changes")
    title = models.CharField(verbose_name="Person's title e.g. Mr. Dr. or Ms.)",
                             help_text="Person's title, like Mr. Dr. or Ms.", max_length=20, blank=True)
    first_name = models.CharField(verbose_name="Person's first and middle names",
                                  help_text="First name also includes any middle names", max_length=100)
    last_name = models.CharField(verbose_name="Person's last name",
                                 help_text="Last name includes titles such as Phd.", max_length=50)
    notes = models.TextField(help_text="Notes relevant to this person", blank=True)
    # citizenship_status = models.CharField(verbose_name="Citizenship status", default="US Citizen", max_length=50,
    #                                       help_text="Information about whether this person is a US citizen or not",
    #                                       blank=True)
    current_record_fg = models.BooleanField(verbose_name="Current record flag", default=True,
                                      help_text="Set to True for the current version of the record")
    effective_date = models.DateTimeField(verbose_name="Record effective date", default=django.utils.timezone.now,
                                          help_text="The date & time on which this record became active")
    end_date = models.DateTimeField(verbose_name="Record end date",
                                    help_text="The date and time on which this record expired", blank=True, null=True)

    def create(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Overrides the parent class' save method
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        curr_datetime = datetime.datetime.now()
        try:
            with transaction.atomic():  # Starts a transaction
                new_contact_static = PersonStatic(
                    effective_date=curr_datetime, current_record_fg=True)
                new_contact_static.save()
                self.person_static = new_contact_static
                self.save()
                # super(PersonDynamic, self).save(self)
        except Error as db_err:
            # TODO: Do something here!!!
            print(str(db_err))

    def delete(self, using=None, keep_parents=False):
        """
        Overrides the parent class' delete method as all contact deletes will be logical
        :param using:
        :param keep_parents:
        :return:
        """
        curr_datetime = datetime.datetime.now()
        try:
            with transaction.atomic():  # Starts a transaction
                # Logically delete the static record
                self.person_static.end_date = curr_datetime
                self.person_static.current_record_fg = False
                self.person_static.save(force_update=True)

                # Logically delete the dynamic record
                self.end_date = curr_datetime
                self.current_record_fg = True
                self.save(force_update=True)
        except Error as db_err:
            # TODO: Do something here!!!
            print(str(db_err))

    def update(self):
        """
        Creates a logical update of a contact record
        :return:
        """
        # Deactivate the old record
        curr_datetime = datetime.datetime.now()
        try:
            with transaction.atomic():
                self.end_date = curr_datetime
                self.current_record_fg = False
                self.save(update_fields=['end_date', 'current_record_fg'], force_update=True)
                # Now insert the new record!!!!
                self.current_record_fg = True
                self.end_date = None
                self.effective_date = curr_datetime
                self.id = None
                self.save(force_insert=True)
        except Error as db_error:
            # TODO: Do something here!!!
            print(str(db_error))


class AddrElectronic(models.Model):
    """
    Contains electronic contact addresses, including phone, email, twitter, and user defined mechanisms
    """
    # Link to person_dynamic if this is related to a person
    person_dynamic = models.ForeignKey(to=PersonDynamic, verbose_name="The related contact", blank=True, null=True)
    #TODO: Add a link to an organization for situations where that fits
    #TODO: The form should provide the following suggestions in a dropdown which populates this field but also allows the user to just enter what they want here
    #TODO: If type is email, form logic should validate using class EmailValidator(message=None, code=None, whitelist=None)
    addr_type = models.TextField(verbose_name='Address Type', help_text='What kind of address - email, phone...',
                                 choices=[('Email', 'Email'), ('Phone', 'Phone'), ('Twitter', 'Twitter'),
                                          ('URL', 'URL'), ('Facebook', 'Facebook'), ('Other', 'Other')])
    name = models.TextField(verbose_name='E Address Name', help_text='Name of this address. e.g. home, work...',
                            blank=True)
    value = models.TextField(verbose_name='Address', help_text='The actual electronic address')
    #TODO: Add a way to change display sequences
    display_seq = models.IntegerField(verbose_name='Display Sequence',
                              help_text='The order in which this address should appear in lists')

    current_record_fg = models.BooleanField(verbose_name="Current record flag", default=True,
                                      help_text="Set to True for the current version of the record")
    effective_date = models.DateTimeField(verbose_name="Record effective date", default=django.utils.timezone.now,
                                          help_text="The date & time on which this record became active")
    end_date = models.DateTimeField(verbose_name="Record end date",
                                    help_text="The date and time on which this record expired", blank=True, null=True)

    class Meta:
        ordering = ['addr_type', 'display_seq']  # Defaults to grouping address types together

