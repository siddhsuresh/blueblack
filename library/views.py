from .models import Author, Genre, Book, BookIndividual, Language, IssueBook, Student, ReturnBook, Staff, PublishingHouse, RenewRequest
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import ListView
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

def View_Dashboard(request):
	if request.user.is_staff:
		return redirect('/staff')
	if request.user.is_authenticated:
		flag1=flag2=flag3=False
		student=Student.objects.get(user=request.user)
		c_i=IssueBook.objects.all().count()
		if IssueBook.objects.filter(student=student).exists():
		    exists=True
		    ci=IssueBook.objects.filter(student=student)
		    cic=ci.count()
		    cr=ReturnBook.objects.filter(borrowed_book__student=student).count()
		    crf=ReturnBook.objects.filter(borrowed_book__student=student,is_fined=True).count()
		    res = ci.values('borrowed_book__book__genre__name').annotate(count=Count('borrowed_book'))
		    re = res.order_by('-count').first()
		    genrename = re['borrowed_book__book__genre__name']
		    author = ci.values('borrowed_book__book__author__name').annotate(count=Count('borrowed_book')).order_by('-count').first()
		    a=author['borrowed_book__book__author__name']
		else:
		    exists=False
		if c_i:
			result = IssueBook.objects.values('borrowed_book__book__title').annotate(count=Count('borrowed_book'))
			r=result.order_by('-count').first()
			name=r['borrowed_book__book__title']
			number_of_time_issued = r['count']
			book = Book.objects.get(title=name)
		c=IssueBook.objects.filter(student=student, is_returned=False).count()
		i2=IssueBook.objects.filter(student=student).order_by('-issue_date').first()
		if c:
			i1=IssueBook.objects.filter(student=student, is_returned=False).order_by('expected_return_date').first()
			time1 = i1.expected_return_date
			time=timezone.now()
			time1-=time
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
		rr=False
		if RenewRequest.objects.filter(book__student=student,book__is_returned=False).exists():
			rr=True
			if RenewRequest.objects.filter(book__student=student,request='p',book__is_returned=False).exists():
				renew = RenewRequest.objects.get(book__student=student,request='p',book__is_returned=False)
			else:
				renew = RenewRequest.objects.filter(Q(book__student=student)&Q(book__is_returned=False)&(Q(request='a')|Q(request='d'))).order_by('-date').first()
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
	if request.user.is_staff:
		return redirect('/staff')
	books=Book.objects.all()
	bc = books.count()
	return render(request, "allbooks.html", locals())

@login_required(redirect_field_name='dashboard')
def Author_view(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	author=Author.objects.get(id=pk)
	books=Book.objects.filter(author=author)
	return render(request, "author.html", locals())

@login_required(redirect_field_name='dashboard')
def Search_View(request):
	if request.user.is_staff:
		staff=Staff.objects.get(user=request.user)
	books=None
	url_parameter = request.GET.get("q", None)
	if url_parameter:
		books = Book.objects.filter(Q(title__icontains=url_parameter)|Q(author__name__icontains=url_parameter)|Q(genre__name__icontains=url_parameter)|Q(author__publisher__name__icontains=url_parameter)).distinct()
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
		return JsonResponse(data=data_dict, safe=False)
	return render(request, "search.html", locals())

@login_required(redirect_field_name='dashboard')
def get_issued_view(request):
	if request.user.is_staff:
		return redirect('/staff')
	student=Student.objects.get(user=request.user)
	book_list=IssueBook.objects.filter(student=student, is_returned=False)
	return render(request, 'viewissued.html', locals())

@login_required(redirect_field_name='dashboard')
def View_Renew_Issued(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	iss=IssueBook.objects.get(id=pk)
	r=RenewRequest(book=iss, request='p')
	r.save()
	messages.info(request,'Renew Request is Sent!!')
	return redirect('/',locals())

@login_required(redirect_field_name='dashboard')
def Individual_books_view(request,pk):
	if request.user.is_staff:
		return redirect('/staff')
	Already_Taken=False
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
	if IssueBook.objects.filter(student=student, is_returned=False).count()>=3:
		messages.info(request,'Sorry!! You Can Not Issue More Than 3 Books At A Time')
	elif book.status=='a':
		issue_date=timezone.now()
		return_date=issue_date+timedelta(days = 1)
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
	time1 = r.borrowed_book.expected_return_date.replace(tzinfo=None)
	time2 = r.actual_return_date.replace(tzinfo=None)
	if time1<time2:
		r.borrowed_book.student.fine+=100
		r.borrowed_book.student.save()
		r.is_fined=True
		r.save()
		messages.error(request,'You have been fined!!')
	if RenewRequest.objects.filter(book=iss).exists():
	    renw = RenewRequest.objects.get(book=iss)
	    if renw.request=='p':
	        renw.delete()
	messages.success(request,  'Your Book Has Been Successfully Returned')
	return redirect('/', locals())

@login_required(redirect_field_name='dashboard')
def ReturnListView(request):
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

#All Staff Website Views written here
@login_required(redirect_field_name='dashboard')
def View_Staff_Dashboard(request):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
		return redirect('/', locals())
	staff=Staff.objects.get(user=request.user)
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
	flag=False
	if RenewRequest.objects.all().count():
		flag=True
		renew = RenewRequest.objects.filter(request='p')
	return render(request, "staff_renewbooks.html",locals())

@login_required(redirect_field_name='dashboard')
def View_Staff_Approve_Renew(request,pk):
	if not request.user.is_staff:
		messages.error(request,'You are Unauthorised to visit the Staff Page!!')
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
	r = RenewRequest.objects.get(id=pk)
	r.staff = Staff.objects.get(user=request.user)
	r.request = 'd'
	r.date = timezone.now()
	r.save()
	return redirect('/staff', locals())
