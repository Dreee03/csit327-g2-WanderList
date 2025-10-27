from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from dashboard.supabase_client import supabase


def destination_list(request):
	"""Display the list of destinations and the create/edit form."""
	# Fetch all destinations from Supabase
    # current_user_id = request.session.get('supabase_auth_id') 
	try:
		resp = supabase.table('destination').select('*').execute()
		destinations = resp.data if resp.data else []
	except Exception as e:
		destinations = []
		messages.error(request, f"Could not fetch destinations: {e}")

	# Render template with an empty form by default
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
        # Basic server-side validation and normalization
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()  # now stores text directly

        if not name or not city or not country or not category:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('destination:add_destination')

        if len(description) > 500:
            messages.error(request, 'Description must be 500 characters or fewer.')
            return redirect('destination:add_destination')

        data = {
            'name': name,
            'city': city,
            'country': country,
            'description': description,
            'category': category,  # directly insert text like "Visited"
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
        # Fetch the existing destination
        result = supabase.table('destination').select('*').eq('destinationID', destination_id).execute()
        destination = result.data[0] if result.data else None

        if not destination:
            messages.error(request, 'Destination not found.')
            return redirect(reverse('destination:list'))
    except Exception as e:
        messages.error(request, f'Error loading destination: {e}')
        return redirect(reverse('destination:list'))

    # ✅ Handle POST (update data)
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        
        if not name or not city or not country or not category:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'edit_destination.html', {'destination': destination})

        if len(description) > 500:
            messages.error(request, 'Description must be 500 characters or fewer.')
            return render(request, 'edit_destination.html', {'destination': destination})

        payload = {
            'name': name,
            'city': city,
            'country': country,
            'category': category,
            'description': description,
        }

        try:
            supabase.table('destination').update(payload).eq('destinationID', destination_id).execute()
            messages.success(request, 'Destination updated successfully!')
            return redirect(reverse('destination:list'))
        except Exception as e:
            messages.error(request, 'Could not update destination. Please try again later.')

    # ✅ Handle GET (load page)
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

