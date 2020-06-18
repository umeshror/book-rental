from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from simple_history.models import HistoricalRecords

CATEGORY_CHOICES = (
    ('regular', 'Regular'),
    ('fiction', 'Fiction'),
    ('novels', 'Novels'),
)


class AuditMixin(models.Model):
    """
    AuditMixin is used for audting purpose.
    By inheriting this model we can track who created
    the object at what time and who updated

    Apart from basic auding it also captures historic data
    Which helps to store every create, update, or delete occurs operation.
    """
    created_by = models.ForeignKey('auth.User',
                                   on_delete=models.PROTECT,
                                   related_name='+',
                                   help_text='User who created the object')

    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time at which object was created')

    updated_by = models.ForeignKey('auth.User',
                                   null=True,
                                   related_name='+',
                                   on_delete=models.PROTECT,
                                   help_text='User who updated the object')

    updated_at = models.DateTimeField(auto_now=True,
                                      null=True,
                                      help_text='Time at which object was updated')

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class Category(AuditMixin):
    """
    Stores Genre/Category of the Book.
    e.g. Fiction, Horror
    """
    name = models.CharField(max_length=50,
                            blank=False,
                            default='regular',
                            choices=CATEGORY_CHOICES,
                            help_text='Name of the Category')

    slug = models.SlugField(unique=True,
                            help_text="Human readable slug used "
                                      "for hyperlinking e.g. 'drama-fiction'")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Before saving change the slug with name,
        which letter will be used in hyperlinked and urls
        """
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        # custom plural name will overrite 'Categorys'
        verbose_name_plural = "Categories"


@receiver(post_save, sender=Category)
def add_default_category_day_charges(sender, instance, **kwargs):
    """
    This will add default Category charges if not exist to
    from_Day : 0
    to_day : null
    per_day_charge : Rs. 1
    min_charge : Rs. 0

    This will make sure that every new category will have default CategoryDayCharge
    """
    # note: cannot use .exists() on related manager
    if instance.dayswise_charges.count() == 0:
        instance.dayswise_charges.create(created_by=instance.created_by)


class CategoryDayCharge(AuditMixin):
    """
    Stores Category and days wise charges of the Book.
    e.g

    Regular Book                       min_charge  min_days
    0 - 2 days    Rs. 1 per day        Rs. 2         2
    2 days to --  Rs. 1.5 per day


    X Book                                   min_charge     min_days
    0 - 2 days          Rs. 1 per day        Rs. 2            2
    2 days to 30 days   Rs. 1.5 per day      -----            --
    30 days to  --      Rs. 2 per day        Rs. 50          --

    Y Book                                   min_charge    min_days
    0 - -- days         Rs. 1 per day        --             --
    """
    category = models.ForeignKey(Category,
                                 related_name='dayswise_charges',
                                 on_delete=models.PROTECT,
                                 help_text="Category for which this charge is applied")

    days_from = models.IntegerField(default=0,
                                    help_text="From this number of day per_day_charge starts")

    days_to = models.IntegerField(null=True,
                                  blank=True,
                                  help_text="Till this number of day per_day_charge will be applied")

    per_day_charge = models.FloatField(default=1.0,
                                       help_text='Per day charge for the book of this category'
                                                 'default is Rs. 1.0 per day for all the category'
                                                 'Can be changed for individual category')

    min_charge = models.FloatField(default=0,
                                   help_text='Minimum charges are considered when number of '
                                             'days are less than min_days')

    min_days = models.IntegerField(null=True,
                                   blank=True,
                                   help_text="Minimum days to apply min_charges")

    def __str__(self):
        return "{} to {}: {}".format(self.days_from, self.days_to or "-", self.per_day_charge)

    class Meta:
        unique_together = ('category', 'days_from')


class Book(AuditMixin):
    """
    Stores Book related data.
    Book has a name
    Book has a author
    Book has a category
    Book has a quantity
    """
    name = models.CharField(max_length=255,
                            help_text="Name of the book")

    slug = models.SlugField(unique=True,
                            help_text='Slug of the book')

    description = models.TextField(help_text="Extra information of the Book",
                                   blank=True)

    author = models.ForeignKey('auth.User',
                               help_text="Author of the book",
                               on_delete=models.PROTECT)

    category = models.ForeignKey(Category,
                                 help_text='Genre of the book',
                                 on_delete=models.PROTECT)

    book_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Before saving change the slug with name,
        which letter will be used in hyperlinked and urls
        """
        self.slug = slugify(self.name)
        super(Book, self).save(*args, **kwargs)


class RentedBook(AuditMixin):
    """
    Rented Books of user
    Model consist of standard per day charge. and if any fine applied
    """
    book = models.ForeignKey(Book,
                             on_delete=models.PROTECT,
                             help_text='Book who has taken the book on rent')

    user = models.ForeignKey('auth.User',
                             on_delete=models.PROTECT,
                             help_text='User who has taken the book on rent'
                             )

    rent_date = models.DateField(default=date.today,
                                 help_text='Date at which book was rented')

    return_date = models.DateField(null=True,
                                   blank=True,
                                   help_text='Date at which book was returned')

    has_charges_paid = models.BooleanField(default=False,
                                           help_text='Has the User paid the bills')

    fine_charged = models.FloatField(default=0,
                                     help_text='Any fine applied to User for given book')

    class Meta:
        unique_together = ('book', 'user', 'rent_date')

    @property
    def days_rented(self):
        """
        Gives number of days book was rented
        """
        return ((self.return_date or date.today()) - self.rent_date).days

    @property
    def total_charge(self):
        """
        Note: make sure you use prefetch_related before calling this method
        else it will do multiple db hits

        Total Charges for the user for given book.

        If not has_charges_paid then calculate on per day basis plus any fine applied

        If has_charges_paid then 0 charges
        """
        """
        Scenerios:
        
        X Book              per_day_charge      min_charge    min_days
        0 - 2 days          Rs. 1 per day        Rs. 2          2
        3 days to 30 days   Rs. 1.5 per day      Rs. 10         5
        31 days to  --      Rs. 2 per day        Rs. 50         --

                                        charges
        days_rented =  1 day           2(min_charge)
        days_rented =  2 days          2*1.0
        days_rented =  4 days          2*1.0 + 10(min_charge)
        days_rented =  12 days         2*1.0 + 10*1.5
        days_rented =  35 days         2*1.0 + 28*1.5 + 5*2.0
        
        
        Y Book                                   min_charge    min_days
        0 - -- days         Rs. 1 per day        --             --
        """
        if self.has_charges_paid:
            return 0

        days_rented = self.days_rented

        days_calculated = 0
        total_charges = 0
        for dayswise in self.book.category.dayswise_charges.all():

            # if days_calculated is equal to days_rented means no more days left for calculation
            if days_calculated == days_rented:
                break

            # if days_rented is less than min_days then apply min_charge
            # e.g days_rented = 1  and (days_from = 2  : days_to = 4 , min_days= 2)
            if dayswise.min_days and days_rented <= dayswise.min_days:
                total_charges += dayswise.min_charge
                break

            # if days_to has no limit in this slot
            # e.g days_rented = 4  and (days_from = 2  : days_to = -- (no limit))
            if not dayswise.days_to:
                total_charges += ((days_rented - days_calculated) * dayswise.per_day_charge)
                break

            # if days_rented is between days_from and days_to
            # e.g days_rented = 4  and (days_from = 2  : days_to = 10)
            if dayswise.days_from <= days_rented <= dayswise.days_to:
                days_duration = days_rented - days_calculated
                total_charges += (days_duration * dayswise.per_day_charge)
                days_calculated += days_duration

            # if days_rented is between greater days_from but less tha days_to
            # e.g days_rented = 15  and (days_from = 2  : days_to = 10)
            elif dayswise.days_from <= days_rented > dayswise.days_to:
                days_duration = dayswise.days_to - dayswise.days_from
                total_charges += (days_duration * dayswise.per_day_charge)
                days_calculated += days_duration

        return total_charges + self.fine_charged
