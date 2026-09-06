from django.shortcuts import render, get_object_or_404, redirect
from .models import Chore, Member


def today(request):
    members = Member.objects.all()
    chores = Chore.objects.filter(archived=False).order_by('due_date')
    context = {'members': members, 'chores': chores}
    return render(request, 'chores/today.html', context)


def chore_list(request):
    chores = Chore.objects.all().order_by('title')
    return render(request, 'chores/chore_list.html', {'chores': chores})
