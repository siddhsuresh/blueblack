from django.contrib import admin
from .models import Author, Genre, Book, BookIndividual, Language, IssueBook, Student, ReturnBook, PublishingHouse, Staff, RenewRequest

admin.site.site_header = "Library Admin"
admin.site.site_title = "Library Admin Portal"
admin.site.index_title = "CSE2004 Library Database Management Project"

class BookIndividualInline(admin.TabularInline):
    model = BookIndividual

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookIndividualInline]

class IssueBookInline(admin.TabularInline):
    model = IssueBook

@admin.register(BookIndividual)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'edition')
    inlines = [IssueBookInline]

class BookInline(admin.TabularInline):
	model = Author

@admin.register(PublishingHouse)
class BookAdmin(admin.ModelAdmin):
	inlines = [BookInline]

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(IssueBook)
admin.site.register(ReturnBook)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(RenewRequest)
