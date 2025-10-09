from django.shortcuts import render, redirect

# Import SupabaseUser to present a user-like object to templates
from accounts.forms import SupabaseUser


def dashboard_view(request):
	"""Render the dashboard.html and provide a `user` object compatible with templates.

	If the Supabase session token is missing, redirect to the login page.
	"""
	# If there's no Supabase token in session, require login
	if 'supabase_access_token' not in request.session:
		return redirect('login')

	username = request.session.get('logged_in_username', 'User')
	user_obj = SupabaseUser(username=username, is_authenticated=True)

	context = {
		'user': user_obj,
	}
	return render(request, 'dashboard.html', context)
