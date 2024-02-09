from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Group

from blog.models import Post
from .models import Profile
from kalendarz.models import Events


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class FileForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['uploaded_file']


class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['name', 'start', 'end']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        labels = {
            'name': 'Nazwa grupy',
            'description': 'Opis grupy'
        }