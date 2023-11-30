from django.http import JsonResponse
from django.shortcuts import render, redirect
from kalendarz.models import Events
from django.contrib.auth.decorators import login_required
from users.forms import EventForm  # Dodaj ten import
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_profile = request.user.profile
            event.save()
            return redirect('lista_zdarzen')  # Przykładowa nazwa widoku listy zdarzeń
    else:
        form = EventForm()

    return render(request, 'create_event.html', {'form': form})



@login_required
def event_list(request):
    user_events = Events.objects.filter(user_profile=request.user.profile)
    return render(request, 'event_list.html', {'user_events': user_events})


def index(request):
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }
    return render(request, 'index.html', context)


def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)



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
    elif request.method == 'GET':
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
    else:
        data = {'error': 'Invalid request method'}
        return JsonResponse(data, status=400)


@csrf_protect
@require_http_methods(["DELETE", "GET"])
@login_required
def remove(request):
    if request.method == 'DELETE':
        data = json.loads(request.body)
        event_id = data.get("id", None)

        # Pobierz zalogowanego użytkownika
        user = request.user

        try:
            event = Events.objects.get(id=event_id, user_profile=user)
            event.delete()

            response_data = {}
            return JsonResponse(response_data)
        except Events.DoesNotExist:
            response_data = {'error': 'Event not found'}
            return JsonResponse(response_data, status=404)
    elif request.method == 'GET':
        data = request.GET.dict()
        event_id = data.get("id", None)

        # Pobierz zalogowanego użytkownika
        user = request.user

        try:
            event = Events.objects.get(id=event_id, user_profile=user)
            event.delete()

            response_data = {}
            return JsonResponse(response_data)
        except Events.DoesNotExist:
            response_data = {'error': 'Event not found'}
            return JsonResponse(response_data, status=404)
    else:
        response_data = {'error': 'Invalid request method'}
        return JsonResponse(response_data, status=400)

@csrf_protect
@require_http_methods(["PUT", "GET"])
@login_required
def update(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        start = data.get("start", None)
        end = data.get("end", None)
        title = data.get("title", None)
        event_id = data.get("id", None)

        # Pobierz zalogowanego użytkownika
        user = request.user

        try:
            event = Events.objects.get(id=event_id, user_profile=user)
            event.start = start
            event.end = end
            event.name = title
            event.save()

            response_data = {}
            return JsonResponse(response_data)
        except Events.DoesNotExist:
            response_data = {'error': 'Event not found'}
            return JsonResponse(response_data, status=404)
    elif request.method == 'GET':
        data = request.GET.dict()
        start = data.get("start", None)
        end = data.get("end", None)
        title = data.get("title", None)
        event_id = data.get("id", None)

        # Pobierz zalogowanego użytkownika
        user = request.user

        try:
            event = Events.objects.get(id=event_id, user_profile=user)
            event.start = start
            event.end = end
            event.name = title
            event.save()

            response_data = {}
            return JsonResponse(response_data)
        except Events.DoesNotExist:
            response_data = {'error': 'Event not found'}
            return JsonResponse(response_data, status=404)
    else:
        response_data = {'error': 'Invalid request method'}
        return JsonResponse(response_data, status=400)