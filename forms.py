
from .models import Profile,Comment
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput

class DateInput(forms.DateInput):
    input_type = "date"

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class ProfileUpdateForm(forms.ModelForm):

    image = forms.ImageField()
    cover_photos = forms.ImageField()

    class Meta:
        model = Profile
        fields = ['image', 'cover_photos']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    uname = forms.CharField()
    phone = forms.CharField()

    class Meta:
        model = User
        fields = ['uname', 'email', 'phone']


