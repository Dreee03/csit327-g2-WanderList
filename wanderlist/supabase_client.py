# supabase_client.py
import os
from django.conf import settings
from supabase import create_client, Client

# Ensure SUPABASE_URL and SUPABASE_KEY are loaded from environment variables
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY

# Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)