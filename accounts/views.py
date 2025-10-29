from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm, SupabaseUser  # ✅ use custom forms
from wanderlist.utils import register_user, login_user  # ✅ import utility functions


def home(request):
    # Check if the Supabase tokens exist in the session
    if 'supabase_access_token' in request.session:
        # User is authenticated via Supabase session
        # Temporarily retrieve username from a new session key set at login
        username = request.session.get('logged_in_username', 'User') 
        
        # Creating the dummy user object
        user_obj = SupabaseUser(username=username, is_authenticated=True)
        
    else:
        # User is not authenticated
        user_obj = SupabaseUser(username='Guest', is_authenticated=False)

    # Pass the user object into the context
    context = {
        'user': user_obj, # This fulfills {% if user.is_authenticated %} and {{ user.username }} in templates
    }
    
    return render(request, 'home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                result = register_user(email, password, username)
            except Exception:
                # Avoid leaking internal errors
                messages.error(request, 'Registration service is temporarily unavailable. Please try again later.')
                return render(request, 'register.html', {'form': form})

            if result.get('success'):
                messages.success(request, 'Registration successful. Please check your email to confirm your account.')
                return redirect('login')
            else:
                # Show a generic error if backend gives no safe message
                safe_message = result.get('message') or 'Registration failed. Please verify your details and try again.'
                messages.error(request, safe_message)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            try:
                session_result = login_user(username, password)
            except Exception:
                messages.error(request, 'Login service is temporarily unavailable. Please try again later.')
                return render(request, 'login.html', {'form': form})
            
            if session_result.get('success'):
                # Store Supabase session and user IDs
                request.session['supabase_access_token'] = session_result['token']
                request.session['supabase_auth_id'] = session_result['supabase_auth_id']
                request.session['custom_user_id'] = session_result['custom_user_id'] 
                request.session['logged_in_username'] = session_result['username'] 
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, "Please enter a valid username and password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    from wanderlist.utils import supabase_sign_out
    
    # Sign out from Supabase (revokes the refresh token)
    supabase_sign_out() 
    
    # Clear the local Django session data
    if 'supabase_access_token' in request.session:
        del request.session['supabase_access_token']
    if 'supabase_auth_id' in request.session:
        del request.session['supabase_auth_id']
    if 'custom_user_id' in request.session:
        del request.session['custom_user_id']
    if 'logged_in_username' in request.session:
        del request.session['logged_in_username']
        

    messages.info(request, "You have been logged out.")
    return redirect('login')
