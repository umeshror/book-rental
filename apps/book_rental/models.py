from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from simple_history import register
from simple_history.models import HistoricalRecords

register(User)


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

    per_day_charge = models.FloatField(default=1.0,
                                       help_text='Per day charge for the book it was rented'
                                                 'default its Rs. 1.0 per day for all the books'
                                                 'Can be changed for individual book')

    has_charges_paid = models.BooleanField(default=False,
                                           help_text='Has the User paid the bills')

    fine_applied = models.FloatField(default=0,
                                     help_text='Any fine applied to User for given book')

    class Meta:
        unique_together = ('book', 'user', 'rent_date')

    @cached_property
    def days_rented_for(self):
        """
        Gives number of days book was rented
        """
        return ((self.return_date or date.today()) - self.rent_date).days

    @property
    def total_charge(self):
        """
        Total Charges for the user for given book.

        If not has_charges_paid then calculate on per day basis plus any fine applied

        If has_charges_paid then 0 charges
        """
        if not self.has_charges_paid:
            return (self.days_rented_for * self.per_day_charge) + self.fine_applied
        return 0
