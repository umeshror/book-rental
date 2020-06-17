from django.contrib import admin

from apps.book_rental.models import Category, Book, RentedBook


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ['name']
    fields = ('name', 'slug', 'created_by')


admin.site.register(Category, CategoryAdmin)


class BookAdmin(admin.ModelAdmin):
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


class RentedBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rent_date', 'return_date',
                    'per_day_charge', 'has_charges_paid', 'fine_applied')
    search_fields = ['name']

    def get_queryset(self, request):
        """
        Get the category and author, so we don't have hundreds of queries. i.e. DB hits
        """
        return super(
            RentedBookAdmin, self
        ).get_queryset(
            request
        ).select_related(
            'book',
            'user',
        )


admin.site.register(RentedBook, RentedBookAdmin)
