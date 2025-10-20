from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
from .models import UserProfile
from .forms import ProfileForm
from .supabase_client import supabase
from django.contrib import messages


def dashboard_view(request):
<<<<<<< HEAD
    """Render the dashboard.html with destinations from Supabase."""
=======
    """Render the dashboard.html with destinations from Supabase + search & filter."""
>>>>>>> d516e5f (Initial project commit with dashboard search and filter feature)
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)

    # Retrieve or create profile record so the navbar can display the profile picture
    profile, _ = UserProfile.objects.get_or_create(username=username)

<<<<<<< HEAD
    # Fetch destinations from Supabase
    response = supabase.table("destination").select("*").execute()
    destination = response.data if response.data else []

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations': destination,  # 👈 pass this to your template
=======
    # --- NEW: Get search and filter parameters from GET request ---
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    # Fetch all destinations from Supabase
    response = supabase.table("destination").select("*").execute()
    destination = response.data if response.data else []

    # --- NEW: Apply local filtering ---
    if query:
        destination = [
            d for d in destination
            if query.lower() in d.get('name', '').lower()
            or query.lower() in d.get('city', '').lower()
            or query.lower() in d.get('country', '').lower()
            or query.lower() in d.get('description', '').lower()
        ]

    if category:
        destination = [
            d for d in destination
            if d.get('category', '').lower() == category.lower()
        ]

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations': destination,
        'query': query,
        'category': category,
>>>>>>> d516e5f (Initial project commit with dashboard search and filter feature)
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



def add_destination(request):
<<<<<<< HEAD
=======
    """Add a new destination to Supabase."""
>>>>>>> d516e5f (Initial project commit with dashboard search and filter feature)
    if request.method == "POST":
        name = request.POST.get("name")
        city = request.POST.get("city")
        country = request.POST.get("country")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        description = request.POST.get("description")
<<<<<<< HEAD
=======
        category = request.POST.get("category", "")  # ✅ optional filter field
>>>>>>> d516e5f (Initial project commit with dashboard search and filter feature)

        data = {
            "name": name,
            "city": city,
            "country": country,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "description": description,
<<<<<<< HEAD
=======
            "category": category,
>>>>>>> d516e5f (Initial project commit with dashboard search and filter feature)
        }

        try:
            supabase.table("destination").insert(data).execute()
            messages.success(request, "Destination added successfully!")
        except Exception as e:
            messages.error(request, f"Could not add destination: {e}")

<<<<<<< HEAD
        return redirect("dashboard")  # ✅ always return

    # If GET request, render the form
    return render(request, "add_destination.html")  # ✅ also returns an HttpResponse
=======
        return redirect("dashboard")

    # If GET request, render the form
    return render(request, "add_destination.html")
>>>>>>> d516e5f (Initial project commit with dashboard search and filter feature)
