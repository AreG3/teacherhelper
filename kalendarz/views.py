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


@login_required
def event_list(request):
    personal_events = Events.objects.filter(user_profile=request.user)
    group_events = Events.objects.filter(groups__members=request.user).distinct()
    user_events = personal_events | group_events  # Łączymy obie listy i eliminujemy duplikaty
    return render(request, 'event_list.html', {'user_events': user_events})


def index(request):
    user_events = Events.objects.filter(user_profile=request.user)
    context = {
        "user_events": user_events,
    }
    return render(request, 'index.html', context)


def all_events(request):
    personal_events = Events.objects.filter(user_profile=request.user).values_list('id', flat=True)
    group_events = Events.objects.filter(groups__members=request.user).distinct().values_list('id', flat=True)
    all_user_events_ids = set(list(personal_events) + list(group_events))
    all_user_events = Events.objects.filter(id__in=all_user_events_ids)

    out = []
    for event in all_user_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S") if event.end else None,
        })

    return JsonResponse(out, safe=False)


@require_http_methods(["POST", "GET"])
@login_required
def add_event(request):
    if request.method == 'POST':
        # Używamy formularza z użytkownikiem, aby filtrować grupy
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_profile = request.user
            event.save()
            form.save_m2m()  # Zapisujemy relacje ManyToMany dla grup
            data = {'success': 'Wydarzenie zostało pomyślnie dodane/edytowane.'}
            return JsonResponse(data)
        else:
            data = {'error': 'Invalid form data'}
            return JsonResponse(data, status=400)
    else:
        # Logika dla żądań GET jest taka sama jak wcześniej
        start = request.GET.get("start", None)
        end = request.GET.get("end", None)
        title = request.GET.get("title", None)
        all_day_param = request.GET.get("all_day", None)

        user = request.user
        all_day = all_day_param.lower() == 'true' if all_day_param is not None else False

        event = Events(user_profile=user, name=title, start=start, end=end, all_day=all_day)
        event.save()

        data = {}
        return JsonResponse(data)


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
