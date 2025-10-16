from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from dashboard.supabase_client import supabase


def destination_list(request):
	"""Display the list of destinations and the create/edit form."""
	# Fetch all destinations from Supabase
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

def add_destination(request):
    """Display the Add Destination form."""
    if request.method == 'POST':
        return create_destination(request)  # handle the form submission
    
    return render(request, 'add_destination.html')


@require_http_methods(["POST"])
def create_destination(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        country = request.POST.get('country')
        description = request.POST.get('description')
        category = request.POST.get('category')  # now stores text directly

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
        name = request.POST.get('name')
        city = request.POST.get('city')
        country = request.POST.get('country')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        if not name or not city or not country:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'destination/edit_destination.html', {'destination': destination})

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
            messages.error(request, f'Could not update destination: {e}')

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

