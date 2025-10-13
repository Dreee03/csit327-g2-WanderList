from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
from .models import UserProfile
from .forms import ProfileForm

def dashboard_view(request):
    """Render the dashboard.html and provide a `user` object compatible with templates."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)

    # Retrieve or create profile record so the navbar can display the profile picture
    profile, _ = UserProfile.objects.get_or_create(username=username)

    context = {
        'user': user_obj,
        'profile': profile,  # include profile in context
    }
    return render(request, 'dashboard.html', context)


def profile_view(request):
    """Render an editable user profile page with image upload."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)

    # Retrieve or create profile record
    profile, _ = UserProfile.objects.get_or_create(username=username)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user_obj,
        'form': form,
        'profile': profile,
    }
    return render(request, 'profile.html', context)
