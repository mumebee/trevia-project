from django.shortcuts import render

def index_view(request):
    return render(request, 'core/index.html')

def about_view(request):
    return render(request, 'core/about.html')

def contacts_view(request):
    return render(request, 'core/contacts.html')