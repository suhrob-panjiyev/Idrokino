from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')
def about_view(request):
    return render(request, "core/about.html")