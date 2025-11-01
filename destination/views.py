from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from dashboard.supabase_client import supabase
import uuid 


def destination_list(request):
	"""Display the list of destinations and the create/edit form."""
	try:
		resp = supabase.table('destination').select('*').execute()
		destinations = resp.data if resp.data else []
	except Exception as e:
		destinations = []
		messages.error(request, f"Could not fetch destinations: {e}")

	context = {
		'destinations': destinations,
	}
	return render(request, 'destination.html', context)

@csrf_protect
def add_destination(request):
    """Display the Add Destination form."""
    if request.method == 'POST':
        return create_destination(request)  # handle the form submission
    
    return render(request, 'add_destination.html')


@csrf_protect
@require_http_methods(["POST"])
def create_destination(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        
        # ✅ Get latitude and longitude from the form
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        image_file = request.FILES.get('image')
        image_url = None

        if not name or not city or not country or not category:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('destination:add_destination')
            
        # ✅ Convert coordinates to float or None
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            messages.error(request, 'Latitude and Longitude must be valid numbers.')
            return redirect('destination:add_destination')

        # ✅ Check for duplicates
        try:
            existing = supabase.table('destination') \
                .select('destinationID') \
                .eq('name', name) \
                .eq('city', city) \
                .eq('country', country) \
                .execute()
            
            if existing.data:
                messages.error(request, f'This destination ({name}, {city}) already exists.')
                return redirect('destination:add_destination')
        except Exception as e:
            messages.error(request, f'Error checking for duplicates: {e}')
            return redirect('destination:add_destination')

        if image_file:
            if image_file.size > 20 * 1024 * 1024: 
                messages.error(request, 'Image file is too large (max 20MB).') 
                return redirect('destination:add_destination')
            
            try:
                file_ext = image_file.name.split('.')[-1]
                file_path = f"public/{uuid.uuid4()}.{file_ext}"
                supabase.storage.from_("destination_images").upload(
                    file_path, image_file.read(), {"content-type": image_file.content_type}
                )
                image_url = supabase.storage.from_("destination_images").get_public_url(file_path)
            except Exception as e:
                messages.error(request, f'Error uploading image: {e}')
                return redirect('destination:add_destination')

        data = {
            'name': name,
            'city': city,
            'country': country,
            'description': description,
            'category': category,
            'image_url': image_url, 
            'latitude': latitude,   # ✅ Save latitude
            'longitude': longitude, # ✅ Save longitude
        }

        try:
            supabase.table('destination').insert(data).execute()
            messages.success(request, 'Destination added successfully!')
            return redirect('destination:list')
        except Exception as e:
            messages.error(request, f'Error adding destination: {e}')
            return redirect('destination:add_destination')

    return render(request, 'add_destination.html')


@csrf_protect
def edit_destination(request, destination_id):
    """Fetch and update a destination from Supabase."""
    try:
        result = supabase.table('destination').select('*').eq('destinationID', destination_id).execute()
        destination = result.data[0] if result.data else None

        if not destination:
            messages.error(request, 'Destination not found.')
            return redirect(reverse('destination:list'))
    except Exception as e:
        messages.error(request, f'Error loading destination: {e}')
        return redirect(reverse('destination:list'))

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        
        # ✅ Get latitude and longitude
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        image_file = request.FILES.get('image')
        image_url = destination.get('image_url') 

        if not name or not city or not country or not category:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'edit_destination.html', {'destination': destination})
            
        # ✅ Convert coordinates to float or None
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            messages.error(request, 'Latitude and Longitude must be valid numbers.')
            return render(request, 'edit_destination.html', {'destination': destination})

        if image_file:
            if image_file.size > 20 * 1024 * 1024: 
                messages.error(request, 'Image file is too large (max 20MB).') 
                return render(request, 'edit_destination.html', {'destination': destination})
            
            try:
                file_ext = image_file.name.split('.')[-1]
                file_path = f"public/{uuid.uuid4()}.{file_ext}"
                supabase.storage.from_("destination_images").upload(
                    file_path, image_file.read(), {"content-type": image_file.content_type}
                )
                image_url = supabase.storage.from_("destination_images").get_public_url(file_path)
            except Exception as e:
                messages.error(request, f'Error uploading image: {e}')
                return render(request, 'edit_destination.html', {'destination': destination})

        payload = {
            'name': name,
            'city': city,
            'country': country,
            'category': category,
            'description': description,
            'image_url': image_url, 
            'latitude': latitude,   # ✅ Update latitude
            'longitude': longitude, # ✅ Update longitude
        }

        try:
            supabase.table('destination').update(payload).eq('destinationID', destination_id).execute()
            messages.success(request, 'Destination updated successfully!')
            return redirect(reverse('destination:list'))
        except Exception as e:
            messages.error(request, 'Could not update destination. Please try again later.')

    return render(request, 'edit_destination.html', {'destination': destination})


@require_http_methods(["POST"])
def delete_destination(request, destination_id):
	"""Delete a destination."""
	try:
		supabase.table('destination').delete().eq('destinationID', destination_id).execute()
		messages.success(request, 'Destination deleted.')
	except Exception as e:
		messages.error(request, f'Could not delete destination: {e}')

	return redirect(reverse('dashboard'))


def redirect_to_dashboard(request):
	"""Redirect to the main dashboard page."""
	return redirect(reverse('dashboard'))