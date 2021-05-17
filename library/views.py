from .forms import NewBookForm, NewStudentForm
from django.contrib.auth.forms import UserCreationForm
from .models import Author, Genre, Book, BookIndividual, Language, IssueBook, Student, ReturnBook
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def View_Dashboard(request):
	if request.user.is_authenticated:
		student=Student.objects.get(user=request.user)
		c_i=IssueBook.objects.all().count()
		if c_i:
			result = IssueBook.objects.values('borrowed_book__book__title').annotate(count=Count('borrowed_book'))
			r=result.order_by('-count').first()
			most_popular_book=r['borrowed_book__book__title']
			number_of_time_issued = r['count']
			print(most_popular_book,number_of_time_issued)
		c=IssueBook.objects.filter(student=student, is_returned=False).count()
		if c:
			i1=IssueBook.objects.filter(student=student, is_returned=False).first()
			i2=IssueBook.objects.filter(student=student).last()
			time1 = i1.expected_return_date
			time=timezone.now()
			time1-=time
			time_left = time1.total_seconds()//3600
	return render(request, "Dashboard.html", locals())
@login_required(redirect_field_name='dashboard')
def add_book_view(request):
	context ={}
	form = NewBookForm(request.POST or None, request.FILES or None)

	if form.is_valid():
		form.save()

	context['form']= form
	return render(request, "addbook.html", context)

def all_books_view(request):
    dataset=Book.objects.all()
    return render(request, "allbooks.html", locals())

@login_required(redirect_field_name='dashboard')
def Author_view(request,pk):
    author=Author.objects.get(id=pk)
    books=Book.objects.filter(author=author)
    return render(request, "author.html", locals())

@login_required(redirect_field_name='dashboard')
def Search_View(request):
	flag=False
	if request.method=='POST':
		flag=True
		search = request.POST.get('search')
		book_count=Book.objects.filter(title__contains=search).count()
		author_count=Author.objects.filter(name__contains=search).count()
		if book_count>0:
			books=Book.objects.filter(title__contains=search)
		if author_count>0:
			authors=Author.objects.filter(name__contains=search)	

	return render(request, "search.html", locals())

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
		return_date=issue_date+timedelta(days = 1)
		iss=IssueBook(student=student, borrowed_book=book, issue_date=issue_date, expected_return_date=return_date)
		iss.save()
		messages.success(request, 'Your Book Has Been Successfully Issued')
		student.total_books_due+=1
		student.save()
		book.status = 'o'
		book.save()
	else:
		messages.error(request, 'Book already taken try again!!')
	return redirect('/', locals())

@login_required(redirect_field_name='dashboard')
def Book_Return_View(request,pk):
	student=Student.objects.get(user=request.user)
	iss=IssueBook.objects.get(id=pk)
	iss.is_returned=True
	iss.save()
	iss.borrowed_book.status='a'
	iss.borrowed_book.save()
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
	student.total_books_due-=1
	student.save()
	return redirect('/', locals())

@login_required(redirect_field_name='dashboard')
def student_render_pdf_view(request):
    template_path = 'history.html'
    student=Student.objects.get(user=request.user)
    ret= ReturnBook.objects.filter(borrowed_book__student=student)
    #ret=ReturnBook.objects.filter(borrowed_book=iss).first()
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(locals())

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
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
