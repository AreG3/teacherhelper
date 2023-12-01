from django.http import JsonResponse
from django.shortcuts import render, redirect
from kalendarz.models import Events
from django.contrib.auth.decorators import login_required
from users.forms import EventForm  # Dodaj ten import
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.http import HttpResponseNotAllowed



@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_profile = request.user
            event.save()
            return redirect('all_events')  # Przykładowa nazwa widoku listy zdarzeń
    else:
        form = EventForm()

    return render(request, 'create_event.html', {'form': form})



@login_required
def event_list(request):
    user_events = Events.objects.filter(user_profile=request.user)
    return render(request, 'event_list.html', {'user_events': user_events})


def index(request):
    user_events = Events.objects.filter(user_profile=request.user)
    context = {
        "user_events": user_events,
    }
    return render(request, 'index.html', context)


def all_events(request):
    all_events = Events.objects.filter(user_profile=request.user)
    out = []
    for event in all_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)




@csrf_protect
@require_http_methods(["POST", "GET"])
@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_profile = request.user
            event.save()
            data = {}
            return JsonResponse(data)
        else:
            data = {'error': 'Invalid form data'}
            return JsonResponse(data, status=400)
    else:
        start = request.GET.get("start", None)
        end = request.GET.get("end", None)
        title = request.GET.get("title", None)

        # Pobierz zalogowanego użytkownika
        user = request.user

        # Przypisz użytkownika do nowego zdarzenia
        event = Events(user_profile=user, name=str(title), start=start, end=end)
        event.save()

        data = {}
        return JsonResponse(data)


@login_required
@require_GET
def remove(request, id):
    # Pobierz zalogowanego użytkownika
    user = request.user

    if request.method == 'POST':
        event = get_object_or_404(Events, id=id, user_profile=user)
        event.delete()

        response_data = {}
        return JsonResponse(response_data)
    else:
        data = {'error': 'Invalid request method'}
        return JsonResponse(data, status=400)



@login_required
@require_GET
def update(request, id):
    # Pobierz zalogowanego użytkownika
    user = request.user

    event = get_object_or_404(Events, id=id, user_profile=user)

    # Odczytaj dane z parametrów zapytania zamiast z ciała
    event.start = request.GET.get("start", None)
    event.end = request.GET.get("end", None)
    event.name = request.GET.get("title", None)
    event.save()

    response_data = {}
    return JsonResponse(response_data)
