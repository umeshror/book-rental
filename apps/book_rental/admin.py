from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from apps.book_rental.models import Category, Book, RentedBook, CategoryDayCharge


class CategoryDayChargeAdmin(SimpleHistoryAdmin):
    list_display = ('category', 'days_from', 'days_to', 'per_day_charge', 'min_charge')
    search_fields = ['category__name']

    def get_queryset(self, request):
        """
        Get the category and author, so we don't have hundreds of queries. i.e. DB hits
        """
        return super(
            CategoryDayChargeAdmin, self
        ).get_queryset(
            request
        ).select_related(
            'category',
        )


admin.site.register(CategoryDayCharge, CategoryDayChargeAdmin)


class CategoryDayChargeInlineAdmin(admin.TabularInline):
    """
    Adding an inline CategoryDayCharge model admin for
    convenience while working with Category in admin
    """
    model = CategoryDayCharge
    extra = 1

    def get_queryset(self, request):
        """
        Fetches related models to avoid extra queries
        """
        return super(
            CategoryDayChargeInlineAdmin, self
        ).get_queryset(
            request
        ).select_related('category')


class CategoryAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'slug')
    search_fields = ['name']
    fields = ('name', 'slug', 'created_by')
    inlines = (CategoryDayChargeInlineAdmin,)


admin.site.register(Category, CategoryAdmin)


class BookAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'slug', 'category', 'author', 'book_quantity')
    search_fields = ['name']

    def get_queryset(self, request):
        """
        Get the category and author, so we don't have hundreds of queries. i.e. DB hits
        """
        return super(
            BookAdmin, self
        ).get_queryset(
            request
        ).select_related(
            'category',
            'author',
        )


admin.site.register(Book, BookAdmin)


class RentedBookAdmin(SimpleHistoryAdmin):
    list_display = ('book', 'user',
                    'rent_date', 'return_date', 'days_rented',
                    'fine_charged', 'total_charge', 'has_charges_paid')

    search_fields = ['name']

    def get_queryset(self, request):
        """
        Get the book and user, so we don't have hundreds of queries. i.e. DB hits
        """
        return super(
            RentedBookAdmin, self
        ).get_queryset(
            request
        ).select_related(
            'book',
            'book__category',
            'user',
        )


admin.site.register(RentedBook, RentedBookAdmin)
