from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
from .models import UserProfile
from .forms import ProfileForm
from .supabase_client import supabase
from django.contrib import messages
import json


def dashboard_view(request):
    # This view is unchanged
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)

    profile, _ = UserProfile.objects.get_or_create(username=username)

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    response = supabase.table("destination").select("*").execute()
    destination = response.data if response.data else []

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
    }
    return render(request, 'dashboard.html', context)


def my_lists_view(request):
    # This view is unchanged
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)

    profile, _ = UserProfile.objects.get_or_create(username=username)

    try:
        response = supabase.table("destination").select("*").execute()
        destinations = response.data if response.data else []
    except Exception as e:
        destinations = []
        messages.error(request, f"Could not fetch destinations: {e}")

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations_json': json.dumps(destinations),
    }
    return render(request, 'my_lists.html', context)


def profile_view(request):
    """Render an editable user profile page with image upload."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)

    # This will now find the profile created during registration
    profile, created = UserProfile.objects.get_or_create(username=username)
    
    # ✅ --- START: Get Destination Stats & Lists ---
    stats = {'Planned': 0, 'Visited': 0, 'Dreaming': 0, 'Total': 0}
    
    # Create lists to hold the actual destinations for the modal
    planned_destinations = []
    visited_destinations = []
    dreaming_destinations = []
    
    try:
        # Fetch the data needed for the lists
        # Note: This fetches destinations for *all* users.
        response = supabase.table("destination").select("category, name, image_url").execute()
        
        if response.data:
            all_destinations = response.data
            stats['Total'] = len(all_destinations)
            
            for dest in all_destinations:
                category = dest.get('category')
                if category == 'Planned':
                    stats['Planned'] += 1
                    planned_destinations.append(dest)
                elif category == 'Visited':
                    stats['Visited'] += 1
                    visited_destinations.append(dest)
                elif category == 'Dreaming':
                    stats['Dreaming'] += 1
                    dreaming_destinations.append(dest)
    except Exception as e:
        messages.error(request, f"Could not load destination stats: {e}")
    # ✅ --- END: Get Destination Stats & Lists ---


    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user_obj,
        'form': form,
        'profile': profile,
        'stats': stats, # Pass stats (counts)
        'planned_destinations': planned_destinations, # ✅ Pass lists
        'visited_destinations': visited_destinations,
        'dreaming_destinations': dreaming_destinations,
    }
    return render(request, 'profile.html', context)


# These functions are unchanged from your file
def add_destination(request):
    """Add a new destination to Supabase."""
    if request.method == "POST":
        name = request.POST.get("name")
        city = request.POST.get("city")
        country = request.POST.get("country")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        description = request.POST.get("description")
        category = request.POST.get("category", "")

        data = {
            "name": name,
            "city": city,
            "country": country,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "description": description,
            "category": category,
        }

        try:
            supabase.table("destination").insert(data).execute()
            messages.success(request, "✅ Destination added successfully!")
        except Exception as e:
            messages.error(request, f"❌ Could not add destination: {e}")

        return redirect("dashboard")

    return render(request, "add_destination.html")


def edit_destination(request, destination_id):
    """Edit an existing destination."""
    if request.method == "POST":
        name = request.POST.get("name")
        city = request.POST.get("city")
        country = request.POST.get("country")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        description = request.POST.get("description")
        category = request.POST.get("category", "")

        try:
            supabase.table("destination").update({
                "name": name,
                "city": city,
                "country": country,
                "latitude": float(latitude) if latitude else None,
                "longitude": float(longitude) if longitude else None,
                "description": description,
                "category": category,
            }).eq("destinationID", destination_id).execute()
            messages.success(request, "✏️ Destination updated successfully!")
        except Exception as e:
            messages.error(request, f"❌ Could not update destination: {e}")

        return redirect("dashboard")

    # Fetch destination details to prefill form
    destination = supabase.table("destination").select("*").eq("destinationID", destination_id).execute().data[0]
    return render(request, "edit_destination.html", {"destination": destination})


def delete_destination(request, destination_id):
    """Delete a destination with confirmation."""
    if request.method == "POST":
        try:
            supabase.table("destination").delete().eq("destinationID", destination_id).execute()
            messages.success(request, "🗑️ Destination deleted successfully!")
        except Exception as e:
            messages.error(request, f"❌ Could not delete destination: {e}")
    
    return redirect("dashboard")