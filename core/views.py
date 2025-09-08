from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegistrationForm
# Create your views here.
def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
         form = UserRegistrationForm(request.POST)
         if form.is_valid():
             user = form.save(commit=False)
             user.email = form.cleaned_data.get('email', '')
             user.save()
             login(request, user)
             return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



def home_page(request):
    return render(request, 'home.html')