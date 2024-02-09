from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .forms import GroupForm


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


#def create_group(request):
#    if request.method == 'POST':
#        form = GroupForm(request.POST)
#        if form.is_valid():
#            group = form.save()
#            return redirect('group_detail', pk=group.pk)
#    else:
#        form = GroupForm()
#    return render(request, 'users/create_group.html', {'form': form})


def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupa została pomyślnie utworzona!')
            return redirect('blog-home')  # Przykładowy URL do przekierowania po utworzeniu grupy
    else:
        form = GroupForm()
    return render(request, 'users/group_form.html', {'form': form})