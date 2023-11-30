from django.http import JsonResponse
from django.shortcuts import render, redirect
from kalendarz.models import Events
from django.contrib.auth.decorators import login_required
from users.forms import EventForm  # Dodaj ten import
from django.views.decorators.csrf import csrf_exempt


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





@login_required
def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)

    # Pobierz zalogowanego użytkownika
    user_profile = request.user.profile

    event = Events.objects.get(id=id, user_profile=user_profile)
    event.start = start
    event.end = end
    event.name = title
    event.save()

    data = {}
    return JsonResponse(data)


@login_required
def remove(request):
    id = request.GET.get("id", None)

    # Pobierz zalogowanego użytkownika
    user_profile = request.user.profile

    event = Events.objects.get(id=id, user_profile=user_profile)
    event.delete()

    data = {}
    return JsonResponse(data)
