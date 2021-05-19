import uuid
from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
	name = models.CharField(max_length=100)
	def __str__(self):
		return self.name

class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=100)
    publisher = models.ForeignKey('PublishingHouse', on_delete=models.SET_NULL, null=True, blank=True)
    GEN = (('n',''),('m','Male'),('f','Female'),('o','Other'))
    gender = models.CharField(max_length=15, choices=GEN, default='n', blank=True)
    bio = models.CharField(max_length=1000, default=' ')
    nationality= models.CharField(max_length=50, default=' ')

    def __str__(self):
        return self.name

class PublishingHouse(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    genre = models.ManyToManyField(Genre)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title', 'author']
    
    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all())

    def num_books(self):
        return BookIndividual.objects.filter(book=self, status='a').count()
    
    def __str__(self):
        return self.title

class BookIndividual(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    book = models.ForeignKey('Book', on_delete=models.CASCADE, null=True)
    edition = models.IntegerField(default=0)
    LOAN_STATUS = ( ('o', 'Not Available'), ('a', 'Available'))
    status = models.CharField( max_length=1, choices=LOAN_STATUS, blank=True, default='a', help_text='')
    
    class Meta:
        ordering = ['-edition']

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)


class IssueBook(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    borrowed_book = models.ForeignKey('BookIndividual', on_delete = models.SET_NULL , null=True, blank=True)
    issue_date = models.DateTimeField(null=True,blank=True)
    expected_return_date = models.DateTimeField(null=True,blank=True)
    is_returned = models.BooleanField(default=False)
    
    def __str__(self):
        return self.student.name+" has been issued "+self.borrowed_book.book.title+" on "+str(self.issue_date)

class ReturnBook(models.Model):
    borrowed_book = models.OneToOneField('IssueBook', on_delete = models.CASCADE , null=True, blank=True)
    actual_return_date = models.DateTimeField(null=True,blank=True)
    is_fined = models.BooleanField(default=False)
    
    def __str__(self):
        return self.borrowed_book.student.name+" has returned "+self.borrowed_book.borrowed_book.book.title+" on "+str(self.actual_return_date)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    branch = models.CharField(max_length=3)
    DEPT = ( ('1', 'CSE'), ('2', 'ECE'), ('3','EEE'),('4','ME'))
    department = models.CharField(max_length=1, choices=DEPT, blank=True, default='1')
    BAT = (('1','2017'),('2','2018'),('3','2019'),('4','2020'))
    batch = models.CharField(max_length=1, choices=BAT, blank=True, default='4')
    SEM = (('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'))
    semester = models.CharField(max_length=1, choices=SEM, blank=True, default='1')
    total_books_due=models.IntegerField(default=0)
    fine = models.IntegerField(default=0)
    email=models.EmailField()
    
    class Meta:
        ordering = ['roll_no']

    def __str__(self):
        return str(self.roll_no)

    def num_books(self):
        return IssueBook.objects.filter(student=self, is_returned=False).count()
"""
class Staff(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)

"""