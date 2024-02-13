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
        widgets = {
            'owner': forms.HiddenInput()  # Ukryj pole 'owner' przed użytkownikami
        }


class AddUserToGroupForm(forms.Form):
    user = forms.ModelChoiceField(queryset=None, label='Użytkownik')

    def __init__(self, *args, **kwargs):
        group_id = kwargs.pop('group_id')
        action = kwargs.pop('action')
        super(AddUserToGroupForm, self).__init__(*args, **kwargs)

        if action == 'add':
            self.fields['user'].queryset = User.objects.exclude(groups__id=group_id)
        elif action == 'remove':
            group = Group.objects.get(id=group_id)
            self.fields['user'].queryset = group.members.all()