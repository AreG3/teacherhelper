from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from .models import Group
from django.forms import ModelForm, DateTimeInput

from blog.models import Post
from .models import Profile
from blog.models import PostEditProposal
from kalendarz.models import Events
from tinymce.widgets import TinyMCE


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), label='Treść: ')

    co_creation_enabled = forms.BooleanField(required=False, label="Włącz współtworzenie")
    co_creation_mode = forms.ChoiceField(
        choices=[('open', 'Otwarta'), ('closed', 'Zamknięta')],
        label='Tryb współtworzenia',
        required=False
    )
    co_creation_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Grupa współtworząca'
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'co_creation_enabled', 'co_creation_mode', 'co_creation_group', 'visibility',
                  'group', 'uploaded_file']


class PostEditProposalForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), label='Treść: ')

    class Meta:
        model = PostEditProposal
        fields = ['title', 'content']


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
    start = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Początek'
    )
    end = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Koniec*'
    )
    all_day = forms.BooleanField(
        required=False,
        label='Całodniowe'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Udostępnij grupom:'
    )

    class Meta:
        model = Events
        fields = ['name', 'start', 'end', 'all_day', 'groups']
        labels = {
            'name': 'Tytuł wydarzenia*',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['groups'].queryset = Group.objects.filter(members=user) | Group.objects.filter(owner=user)


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


