from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from .models import Group

from blog.models import Post
from .models import Profile
from kalendarz.models import Events
from tinymce.widgets import TinyMCE


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label='Grupa nauczycielska')
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), label='Treść: ')

    class Meta:
        model = Post
        fields = ['title', 'content', 'uploaded_file', 'visibility', 'group']


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
        fields = ['name', 'start', 'end', 'groups']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['groups'].queryset = Group.objects.filter(models.Q(members=user) | models.Q(owner=user)).distinct()


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        labels = {
            'name': 'Nazwa grupy',
            'description': 'Opis grupy'
        }
        widgets = {
            'owner': forms.HiddenInput()  # Ukryj pole 'owner' przed użytkownikami
        }


class AddUserToGroupForm(forms.Form):
    user = forms.ModelChoiceField(queryset=None, label='Użytkownik')

    def __init__(self, *args, **kwargs):
        group_id = kwargs.pop('group_id')
        action = kwargs.pop('action')
        super(AddUserToGroupForm, self).__init__(*args, **kwargs)

        group = Group.objects.get(id=group_id)
        existing_members = group.members.all()

        if action == 'add':
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_members.values_list('id', flat=True))
        elif action == 'remove':
            self.fields['user'].queryset = existing_members