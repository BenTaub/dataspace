from django.db import models
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
