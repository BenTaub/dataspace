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
                self.current_record_fg = False
                self.save(force_update=True)
        except Error as db_err:
            # TODO: Do something here!!!
            print(str(db_err))

