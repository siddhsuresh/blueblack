from django.contrib import admin
from .models import Author, Genre, Book, BookIndividual, Language, IssueBook, Student, ReturnBook

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

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(IssueBook)
admin.site.register(ReturnBook)
admin.site.register(Student)