import datetime

from django.shortcuts import render
from django.utils import timezone
from kalendarz.models import Events
from django.contrib.auth.decorators import login_required
from users.forms import EventForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.contrib import messages
from datetime import timedelta


@login_required
def event_list(request):
    personal_events = Events.objects.filter(user_profile=request.user)
    group_events = Events.objects.filter(groups__members=request.user).distinct()
    user_events = personal_events | group_events  # Łączymy obie listy i eliminujemy duplikaty
    return render(request, 'event_list.html', {'user_events': user_events})


@login_required
def check_permissions(request, event_id):
    event = get_object_or_404(Events, id=event_id)

    # Only the event owner can edit or delete the event
    can_edit = event.user_profile == request.user

    return JsonResponse({'can_edit': can_edit})


def index(request):
    user_events = Events.objects.filter(user_profile=request.user)
    context = {
        "user_events": user_events,
    }
    return render(request, 'index.html', context)


@login_required
def all_events(request):
    # Fetch personal events created by the user
    personal_events = Events.objects.filter(user_profile=request.user)

    # Fetch events for groups the user is a member of
    group_events_as_member = Events.objects.filter(groups__members=request.user)

    # Fetch events for groups the user owns
    group_events_as_owner = Events.objects.filter(groups__owner=request.user)

    # Combine all events and remove duplicates using a set
    all_user_events = personal_events | group_events_as_member | group_events_as_owner

    # Prepare the event data for FullCalendar
    out = []
    for event in all_user_events.distinct():
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%Y-%m-%dT%H:%M:%S"),
            'end': event.end.strftime("%Y-%m-%dT%H:%M:%S") if event.end else None,
            'allDay': event.all_day,
        })

    return JsonResponse(out, safe=False)


@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)

            # Adjusting the start and end times by adding 2 hours to compensate for timezone issues
            event.start = event.start + timedelta(hours=2)
            event.end = event.end + timedelta(hours=2)

            event.user_profile = request.user
            event.save()
            form.save_m2m()  # Save the many-to-many data for the form
            return redirect('index')
    else:
        form = EventForm(user=request.user)

    return render(request, 'add_event.html', {'form': form})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Events, id=event_id, user_profile=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Wydarzenie zostało zaktualizowane.')
            return redirect('index')
    else:
        form = EventForm(instance=event, user=request.user)

    return render(request, 'edit_event.html', {'form': form})


@csrf_protect
@require_http_methods(["POST", "GET"])
@login_required
def remove(request, id):
    # Pobierz zalogowanego użytkownika
    user = request.user

    if request.method == 'POST' or request.method == 'GET':
        event = get_object_or_404(Events, id=id, user_profile=user)
        event.delete()

        response_data = {}
        return JsonResponse(response_data)
    else:
        data = {'error': 'Invalid request method'}
        return JsonResponse(data, status=400)


@csrf_protect
@require_GET
@login_required
def update(request, id):
    # Pobierz zalogowanego użytkownika
    user = request.user

    event = get_object_or_404(Events, id=id, user_profile=user)

    # Odczytaj dane z parametrów zapytania zamiast z ciała
    start_param = request.GET.get("start", None)
    end_param = request.GET.get("end", None)
    title = request.GET.get("title", None)
    all_day = request.GET.get("all_day", None)  # Dodaj nowy parametr 'all_day'

    # Przekształć ciągi znaków na daty
    if all_day:
        # Zdarzenie całodniowe
        start = timezone.make_aware(datetime.datetime.strptime(start_param, "%Y-%m-%dT%H:%M:%S"), timezone=timezone.utc)
        end = timezone.make_aware(datetime.datetime.strptime(end_param, "%Y-%m-%d")) if end_param else None
    else:
        # Zdarzenie z godzinami
        start = timezone.make_aware(datetime.datetime.strptime(start_param, "%Y-%m-%dT%H:%M:%S"), timezone=timezone.utc)
        end = timezone.make_aware(datetime.datetime.strptime(end_param, "%Y-%m-%dT%H:%M:%S"), timezone=timezone.utc) if end_param else None

    # Przypisz wartości do modelu
    event.start = start
    event.end = end
    event.name = title

    event.save()

    response_data = {}
    return JsonResponse(response_data)
