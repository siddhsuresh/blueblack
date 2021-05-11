from django import forms
from .models import Book, User, Student
  
class NewBookForm(forms.ModelForm):
    
    class Meta:
        model = Book
        fields = "__all__"

class NewStudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields = "__all__"