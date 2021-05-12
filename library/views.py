from .forms import NewBookForm, NewStudentForm
from django.contrib.auth.forms import UserCreationForm
from .models import Author, Genre, Book, BookIndividual, Language, IssueBook, Student, ReturnBook
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

@login_required(redirect_field_name='dashboard')
def add_book_view(request):
	context ={}
	form = NewBookForm(request.POST or None, request.FILES or None)

	if form.is_valid():
		form.save()

	context['form']= form
	return render(request, "addbook.html", context)

@login_required(redirect_field_name='dashboard')
def all_books_view(request):
    dataset=Book.objects.all()
    return render(request, "allbooks.html", locals())

@login_required(redirect_field_name='dashboard')
def Author_view(request,pk):
    author=Author.objects.get(id=pk)
    books=Book.objects.filter(author=author)
    return render(request, "author.html", locals())

@login_required(redirect_field_name='dashboard')
def get_issued_view(request):
	student=Student.objects.get(user=request.user)
	iss=IssueBook.objects.filter(student=student, is_returned=False)
	book_list=[]
	for i in iss:
		book_list.append(i)
	return render(request, 'viewissued.html', locals())

@login_required(redirect_field_name='dashboard')
def Individual_books_view(request,pk):
	book=Book.objects.get(id=pk)
	dataset=BookIndividual.objects.filter(book=book, status='a')
	return render(request, "books.html", locals())

@login_required(redirect_field_name='dashboard')
def Profile_view(request):
	student=Student.objects.get(user=request.user)
	return render(request, "profile.html", locals())

@login_required(redirect_field_name='dashboard')
def Book_Issue_View(request,pk):
	student=Student.objects.get(user=request.user)
	book=BookIndividual.objects.get(id=pk)
	if book.status=='a':
		issue_date=datetime.now()
		return_date=issue_date+timedelta(minutes = 1)
		if IssueBook.objects.filter(borrowed_book=book, student=student).exists():
			iss=IssueBook.objects.get(borrowed_book=book, student=student)
			iss.issue_date=issue_date
			iss.expected_return_date=return_date
			iss.is_returned=False
			iss.save()
		else:
			iss=IssueBook(student=student, borrowed_book=book, issue_date=issue_date, expected_return_date=return_date)
			iss.save()
		messages.success(request,  'Your Book Has Been Successfully Issued')
		book.status = 'o'
		book.save()
	else:
		messages.error(request, 'Book already taken try again!!')
	return render(request, 'Dashboard.html', locals())

@login_required(redirect_field_name='dashboard')
def Book_Return_View(request,pk):
	iss=IssueBook.objects.get(id=pk)
	iss.is_returned=True
	iss.save()
	iss.borrowed_book.status='a'
	iss.borrowed_book.save()
	if ReturnBook.objects.filter(borrowed_book=iss).exists():
		r=ReturnBook.objects.get(borrowed_book=iss)
		r.actual_return_date=datetime.now()
		r.save()
	else:
		r = ReturnBook(borrowed_book=iss,actual_return_date=datetime.now())
		r.save()
	time1 = r.borrowed_book.expected_return_date.replace(tzinfo=None)
	time2 = r.actual_return_date.replace(tzinfo=None)
	if time1<time2:
		r.borrowed_book.student.fine+=100
		r.borrowed_book.student.save()
		r.is_fined=True
		r.save()
		messages.error(request,'You have been fined!!')
	messages.success(request,  'Your Book Has Been Successfully Returned')
	return render(request, 'Dashboard.html', locals())
"""
def registerPage(request):
	context={}
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		student_form = NewStudentForm(request.POST)

		if form.is_valid() and student_form.is_valid():
			user = form.save()


			student.save()

			messages.success(request,  'Your account has been successfully created')

			return redirect('login')

	context = {'form': form, 'student_form': student_form}
	return render(request, 'registeruser.html', context)
"""
