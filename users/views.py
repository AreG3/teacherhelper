from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .forms import GroupForm
from django.shortcuts import get_object_or_404
from .models import Group
from .forms import AddUserToGroupForm
from django.db.models import Q


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Utworzono konto dla {username}! Możesz się teraz zalogować!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f' Twój Profil został zaktualizowany!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'users/profile.html', context)


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user  # Ustaw właściciela grupy na bieżącego użytkownika
            group.save()
            messages.success(request, 'Grupa została pomyślnie utworzona!')
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'users/group_form.html', {'form': form})


@login_required
def group_list(request):
    if request.user.is_authenticated:
        user_groups = Group.objects.filter(owner=request.user)
        if not user_groups.exists():
            user_groups = Group.objects.filter(members=request.user)
        return render(request, 'users/group_list.html', {'user_groups': user_groups})
    else:
        return render(request, 'users/group_list.html', {})


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    is_owner = group.owner == request.user
    if not is_owner and not group.members.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You are not a member of this group.")

    form = None
    if is_owner:  # Jeśli użytkownik jest właścicielem grupy, inicjujemy formularz z instancją grupy
        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                return redirect('group_list')
        else:
            form = GroupForm(instance=group)

    return render(request, 'users/group_detail.html', {'group': group, 'is_owner': is_owner, 'form': form})


@login_required
def add_user_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)
    if request.method == 'POST':
        form = AddUserToGroupForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            group.members.add(user)
            messages.success(request, f'Dodano użytkownika {user.username} do grupy {group.name}.')
            return redirect('group_detail', group_id=group.id)
    else:
        form = AddUserToGroupForm()
    return render(request, 'users/add_user_to_group.html', {'form': form})


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'users/delete_group_confirm.html', {'group': group})