from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from wanderlist.supabase_client import supabase


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


@require_http_methods(["POST"])
def create_destination(request):
	"""Handle creation of a new destination."""
	name = request.POST.get('name')
	city = request.POST.get('city')
	country = request.POST.get('country')
	latitude = request.POST.get('latitude')
	longitude = request.POST.get('longitude')
	description = request.POST.get('description')

	payload = {
		'name': name,
		'city': city,
		'country': country,
		'latitude': float(latitude) if latitude else None,
		'longitude': float(longitude) if longitude else None,
		'description': description,
	}

	try:
		supabase.table('destination').insert(payload).execute()
		messages.success(request, 'Destination added.')
	except Exception as e:
		messages.error(request, f'Could not add destination: {e}')

	return redirect(reverse('destination:list'))


@require_http_methods(["POST"])
def edit_destination(request, destination_id):
	"""Update an existing destination."""
	name = request.POST.get('name')
	city = request.POST.get('city')
	country = request.POST.get('country')
	latitude = request.POST.get('latitude')
	longitude = request.POST.get('longitude')
	description = request.POST.get('description')

	payload = {
		'name': name,
		'city': city,
		'country': country,
		'latitude': float(latitude) if latitude else None,
		'longitude': float(longitude) if longitude else None,
		'description': description,
	}

	try:
		supabase.table('destination').update(payload).eq('destinationID', destination_id).execute()
		messages.success(request, 'Destination updated.')
	except Exception as e:
		messages.error(request, f'Could not update destination: {e}')

	return redirect(reverse('destination:list'))


@require_http_methods(["POST"])
def delete_destination(request, destination_id):
	"""Delete a destination."""
	try:
		supabase.table('destination').delete().eq('destinationID', destination_id).execute()
		messages.success(request, 'Destination deleted.')
	except Exception as e:
		messages.error(request, f'Could not delete destination: {e}')

	return redirect(reverse('destination:list'))


def redirect_to_dashboard(request):
	"""Redirect to the main dashboard page."""
	return redirect(reverse('dashboard'))

