from .models import Author, Genre, Book, BookIndividual, Language, IssueBook, Student, ReturnBook, Staff, PublishingHouse, RenewRequest
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv

"""
	View this view.py with respect to the models.py and url.py to understand what's going one
	
	request.user gives uses the presently logged in used you have issued the request

	Model.object.all() will give a queryset having all the objects stored using that model
	Model.object.filter() will give a query set with respect to what condition is given inside
	
	Q objects are provided by Django in order to perfrom AND and OR complex operations together. It has been used in 
	View_Dashboard and in the Search_View

	Whenever __ is used in filter needs to be understood that we are using the relationships between the models using the 
	names given in the models.py in order to get and display the correct quesry set.

	The . operator is also used to access the objects of another model whcih is releated to it as per models.py

	Using model_name.save() to save the changes made to the model

	Using modle_name.object.filter().count() will provide the number of object present in the modles with the particular condition
	
	While return render(request,template_name,locals()) 
	So what locals() actually does it that it returns everything in the function as a dictionary so that the template
	can render it by just writing the name in {{}} brackets
	
	So in the template rendering there will be many {% if %} or {% for %} statemnts which run just like any other if or for 
	statements run normally in python, but in this case we will be iterating over HTML code
	
	For every if and for every for we need to end them with {% endif %} or {% endfor %}

	There also places where {% include template_name %} is used. This is mainly for stopping the repetition and the easly change of HTML code
	for repettitive things likt the imports/includes and the navbar. 
"""

"""

	All Student Views are written here

"""
def View_Dashboard(request):
	if request.user.is_staff:
		return redirect('/staff')
	if request.user.is_authenticated:
		# Creating 3 flag in order to show either hour, minute, second or exceded time limit in Dashboard.html
		flag1=flag2=flag3=False
		student=Student.objects.get(user=request.user)
		c_i=IssueBook.objects.all().count()
		if IssueBook.objects.filter(student=student).exists():
		    exists=True
		    # The following counts are for the display bar below the navbar in the Dashboard.html
		    ci=IssueBook.objects.filter(student=student)
		    cic=ci.count()
		    cr=ReturnBook.objects.filter(borrowed_book__student=student).count()
		    crf=ReturnBook.objects.filter(borrowed_book__student=student,is_fined=True).count()
		    # The following command is for finding the favorite genre by ordering the issued books with respect
		    # to the genre of the book
		    # Using Count function to find out the number of issued book for each genre
		    res = ci.values('borrowed_book__book__genre__name').annotate(count=Count('borrowed_book'))
		    re = res.order_by('-count').first()
		    genrename = re['borrowed_book__book__genre__name']
		    # The following command is for finding the favourite author by ordering the issued book with respect to the author of the book
		    # Using Count function to find out the number of issued book for each author
		    author = ci.values('borrowed_book__book__author__name').annotate(count=Count('borrowed_book')).order_by('-count').first()
		    a=author['borrowed_book__book__author__name']
		else:
		    exists=False
		if c_i:
			# The following command is used to find the MOST POPULAR BOOK to show in the Dahsboard.html
			result = IssueBook.objects.values('borrowed_book__book__title').annotate(count=Count('borrowed_book'))
			r=result.order_by('-count').first()
			name=r['borrowed_book__book__title']
			number_of_time_issued = r['count']
			book = Book.objects.get(title=name)
		# This command is used to find whether a student has an issued book that is not returned yet.. 
		c=IssueBook.objects.filter(student=student, is_returned=False).count()
		# This is used to find the LAST BOOK ISSUED for showing in Dashboard.html
		i2=IssueBook.objects.filter(student=student).order_by('-issue_date').first()
		if c:
			# This command is used to show or recommend to the student the upcomming expected return date
			i1=IssueBook.objects.filter(student=student, is_returned=False).order_by('expected_return_date').first()
			# Timezone.now() provides the time with respect to the timezone in the settings.py
			time1 = i1.expected_return_date
			time=timezone.now()
			time1-=time
			# using the command total_second in order to compare
			if time1.total_seconds()<0:
				flag3=True
			else:
				time_left = time1.total_seconds()//3600
				if time_left==0:
					flag1=True
					time_left = time1.total_seconds()//60
				if time_left==0:
					flag2=True
					time_left = time1.total_seconds()
		# This rr stand for renewrequest and is used for the if statemnts in the Dashboard.html to show a recomended book 
		# if there are no renewrequest currently pending
		rr=False
		if RenewRequest.objects.filter(book__student=student,book__is_returned=False).exists():
			rr=True
			# This command is for checking whether there is a current pending renew request as that is of more priotirty than
			# showind accepted or denied 
			if RenewRequest.objects.filter(book__student=student,request='p',book__is_returned=False).exists():
				renew = RenewRequest.objects.get(book__student=student,request='p',book__is_returned=False)
			else:
				# If not using Q objects provided by Django check for a renewrequest object of the particular student
				# It must not be returned and It must be either an accepted or denied request
				# If both are present it will show the latest one
				renew = RenewRequest.objects.filter(Q(book__student=student)&Q(book__is_returned=False)&(Q(request='a')|Q(request='d'))).order_by('-date').first()
	return render(request, "Dashboard.html", locals())

def all_books_view(request):
	if request.user.is_staff:
		return redirect('/staff')
	# Returns all books present in the library
	books=Book.objects.all()
	bc = books.count()
	return render(request, "allbooks.html", locals())

@login_required(redirect_field_name='dashboard')
def Author_view(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	# Using the primary key author_id to ge tthe particular author and then filetering the book model
	# to give a fitered query set of all book authored by the particular author
	author=Author.objects.get(id=pk)
	books=Book.objects.filter(author=author)
	return render(request, "author.html", locals())

@login_required(redirect_field_name='dashboard')
def Search_View(request):
	if request.user.is_staff:
		staff=Staff.objects.get(user=request.user)
	books=None
	# Using AJAX Javascirpt to provide asynchronous response without reloading the web page
	# Getting the search item written the search.html input bar and relays it here
	url_parameter = request.GET.get("q", None)
	if url_parameter:
		# Filtering the Book model to get the filtered query set if the url_parameter is the time,author,..... of the book
		books = Book.objects.filter(Q(title__icontains=url_parameter)|Q(author__name__icontains=url_parameter)|Q(genre__name__icontains=url_parameter)|Q(author__publisher__name__icontains=url_parameter)).distinct()
		# If not it also spits the words with trepsect to a space and then searchs if anything matches
		if books.count()==0:
			words = url_parameter.split()
			for w in words:
				b = Book.objects.filter(Q(title__icontains=w)|Q(author__name__icontains=w)|Q(genre__name__icontains=w)|Q(author__publisher__name__icontains=w))
				books=books.union(b)
		book_count=books.count()
	if request.is_ajax():
		html = render_to_string(
			template_name="books-results-partial.html",
			context={"books": books,"book_count":book_count}
		)
		data_dict = {"html_from_view": html}
		# Send a JSONResponce to the javascript in the search.html to display it
		return JsonResponse(data=data_dict, safe=False)
	return render(request, "search.html", locals())

@login_required(redirect_field_name='dashboard')
def get_issued_view(request):
	if request.user.is_staff:
		return redirect('/staff')
	# Getting student using the user currently logged in
	student=Student.objects.get(user=request.user)
	# Getting all the issued books that are issued by the student and are not retuened yet
	book_list=IssueBook.objects.filter(student=student, is_returned=False)
	return render(request, 'viewissued.html', locals())

@login_required(redirect_field_name='dashboard')
def View_Renew_Issued(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	# Using this view in order to issue a renew request
	iss=IssueBook.objects.get(id=pk)
	r=RenewRequest(book=iss, request='p')
	r.save()
	# Messages will go to the Bootstrap in the Dashboard.html to show it as a message
	messages.info(request,'Renew Request is Sent!!')
	return redirect('/',locals())

@login_required(redirect_field_name='dashboard')
def Individual_books_view(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	Already_Taken=False
	# We are allowing only copy to be taken at a time for a particular view
	# If the book is already taken the HTML will not allow an issue request 
	book=Book.objects.get(id=pk)
	student=Student.objects.get(user=request.user)
	if IssueBook.objects.filter(borrowed_book__book=book, student=student, is_returned=False).count():
		Already_Taken=True
	dataset=BookIndividual.objects.filter(book=book, status='a')
	return render(request, "books.html", locals())

@login_required(redirect_field_name='dashboard')
def Profile_view(request):
	if request.user.is_staff:
		return redirect('/staff')
	student=Student.objects.get(user=request.user)
	return render(request, "profile.html", locals())

@login_required(redirect_field_name='dashboard')
def Book_Issue_View(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	student=Student.objects.get(user=request.user)
	book=BookIndividual.objects.get(id=pk)
	# Only 3 Books at a particular time
	if IssueBook.objects.filter(student=student, is_returned=False).count()>=3:
		messages.info(request,'Sorry!! You Can Not Issue More Than 3 Books At A Time')
	elif book.status=='a':
		issue_date=timezone.now()
		# timedelta creates a timezone object that is used to add a second, minute, hour, day,.....and so on
		return_date=issue_date+timedelta(days = 1)
		# Creating an object in Issuebook with the requeired information
		iss=IssueBook(student=student, borrowed_book=book, issue_date=issue_date, expected_return_date=return_date)
		iss.save()
		messages.success(request, 'Your Book Has Been Successfully Issued')
		book.status = 'o'
		book.save()
	else:
		messages.error(request, 'Book already taken try again!!')
	return redirect('/', locals())

@login_required(redirect_field_name='dashboard')
def Book_Return_View(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	student=Student.objects.get(user=request.user)
	iss=IssueBook.objects.get(id=pk)
	iss.is_returned=True
	iss.save()
	iss.borrowed_book.status='a'
	iss.borrowed_book.save()
	r = ReturnBook(borrowed_book=iss,actual_return_date=timezone.now())
	r.save()
	# We are setting tzinfo to None in order to escape the problems that arrised due to have an active 
	# and an inactive timezone
	time1 = r.borrowed_book.expected_return_date.replace(tzinfo=None)
	time2 = r.actual_return_date.replace(tzinfo=None)
	if time1<time2:
		r.borrowed_book.student.fine+=100
		r.borrowed_book.student.save()
		r.is_fined=True
		r.save()
		messages.error(request,'You have been fined!!')
	# Solves problem that renew request is pending and the user just returns the book
	# So if such a renewrequest is present it would get deleted
	if RenewRequest.objects.filter(book=iss).exists():
	    renw = RenewRequest.objects.get(book=iss)
	    if renw.request=='p':
	        renw.delete()
	messages.success(request,  'Your Book Has Been Successfully Returned')
	return redirect('/', locals())

@login_required(redirect_field_name='dashboard')
def ReturnListView(request):
	# Using Pagnator provided by Django in order to show 10 return book objects at a time
	student=Student.objects.get(user=request.user)
	returnbooks = ReturnBook.objects.filter(borrowed_book__student=student)
	page = request.GET.get('page', 1)
	paginator = Paginator(returnbooks, 10)
	try:
		books = paginator.page(page)
	except PageNotAnInteger:
		books = paginator.page(1)
	except EmptyPage:
		books = paginator.page(paginator.num_pages)

	return render(request, 'returnbooks.html', locals())

@login_required(redirect_field_name='dashboard')
def History_view(request):
	# Using csv module given by python to create a csv of the return book so that we can download the history as csv
    student=Student.objects.get(user=request.user)
    response=HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    l=[]
    l.append('Book History:')
    l.append(student.name)
    l.append(student.roll_no)
    l.append(timezone.now())
    writer.writerow(l)
    writer.writerow(['Book','Author','Publisher','Language','Issue Date','Expected Return Date','Actual Return Date'])
    for r in ReturnBook.objects.filter(borrowed_book__student=student, borrowed_book__is_returned=True).values_list('borrowed_book__borrowed_book__book__title','borrowed_book__borrowed_book__book__author__name','borrowed_book__borrowed_book__book__author__publisher__name','borrowed_book__borrowed_book__book__language__name','borrowed_book__issue_date','borrowed_book__expected_return_date','actual_return_date'):
        writer.writerow(r)
    response['Content-Disposition'] = 'attachment; filename="Return History.csv"'
    return response

"""

 All Staff Website Views written here

"""

@login_required(redirect_field_name='dashboard')
def View_Staff_Dashboard(request):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	# The below command are for the creation of the graph using ChartJS
	labels = []
	data = []
	result = IssueBook.objects.values('borrowed_book__book__title').annotate(count=Count('borrowed_book'))
	ordered_result=result.order_by('-count')[:5]
	for r in ordered_result:
		labels.append(r['borrowed_book__book__title'])
		data.append(r['count'])
	return render(request, 'staff_dashboard.html', locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_AllStudents(request):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	students=Student.objects.all()
	return render(request,'staff_allusers.html',locals())

@login_required(redirect_field_name='dashboard')
def View_Student(request,pk):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	student=Student.objects.get(id=pk)
	book_list=IssueBook.objects.filter(student=student, is_returned=False)
	return render(request, 'staff_student.html', locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_AllBooks(request):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	books=Book.objects.all()
	num_books=Book.objects.all().count()
	num_book_individuals=BookIndividual.objects.all().count()
	return render(request, "staff_allbooks.html", locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_Author(request,pk):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	author=Author.objects.get(id=pk)
	books=Book.objects.filter(author=author)
	return render(request, "staff_author.html",locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_Book(request,pk):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	book=Book.objects.get(id=pk)
	dataset=BookIndividual.objects.filter(book=book)
	return render(request, "staff_books.html",locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_AllAuthors(request):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
	authors=Author.objects.all()
	return render(request, "staff_allauthors.html", locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_Renew(request):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
	# This is meant for showing all the renw requests present which are currently pending
	flag=False
	if RenewRequest.objects.all().count():
		flag=True
		renew = RenewRequest.objects.filter(request='p')
	return render(request, "staff_renewbooks.html",locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_Approve_Renew(request,pk):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
	# This is meant for approving a renew request that is changing the request from p -> a and savind with the date
	# As it is approved we need to add another day to the expected_return_date and save it
	r = RenewRequest.objects.get(id=pk)
	r.request = 'a'
	r.staff = Staff.objects.get(user=request.user)
	r.date = timezone.now()
	r.save()
	r.book.expected_return_date+=timedelta(days=1)
	r.book.save()
	return redirect('/staff', locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_Deny_Renew(request,pk):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
	# This is emant for rejecting a renew request that is changing the request from p->d and saved with date
	r = RenewRequest.objects.get(id=pk)
	r.staff = Staff.objects.get(user=request.user)
	r.request = 'd'
	r.date = timezone.now()
	r.save()
	return redirect('/staff', locals())