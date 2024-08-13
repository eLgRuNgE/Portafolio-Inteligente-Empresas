from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Limpiar el historial de chat antes de iniciar sesión
            if 'chat_history' in request.session:
                del request.session['chat_history']
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.first_name} {user.last_name}!')
                return redirect('chat_home')  # Redirige a la página principal del chat
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = AuthenticationForm()
    return render(request, 'security/login.html', {'form': form})

def logout_view(request):
    if 'chat_history' in request.session:
        del request.session['chat_history']
    logout(request)
    return redirect('login')
