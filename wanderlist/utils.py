from .supabase_client import supabase

def register_user(email, password, username):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }  # <-- Custom metadata
        })
        print(f"Supabase Sign-up Response: {response}") # Debugging line
        if response.user:
            return {"success": True, "message": "Check your email for a confirmation link."}
        else:
            error_message = response.error.message if hasattr(response, 'error') and response.error else "Registration failed."
            return {"success": False, "message": error_message}
            
    except Exception as e:
        print(f"*** CRITICAL SUPABASE ERROR: {type(e).__name__} - {e}")
        return {"success": False, "message": f"Could not connect to the authentication server. Please try again."}
    
def login_user(username, password):
    try:
        lookup_response = supabase.table('user').select('email, auth_id, userID, username').eq('username', username).execute()

        if not lookup_response.data:
            return {"success": False, "message": "Invalid username or password."}
        print(f"Supabase Login Response: {lookup_response}") # Debugging line
        user_data = lookup_response.data[0]
        user_email = user_data['email']

        response = supabase.auth.sign_in_with_password({
            "email": user_email,
            "password": password
        })
        print(f"Supabase Login Response: {response}") # Debugging line
        if response.session:
            print("Login successful.")# Debugging line
            return {
                "success": True, 
                "message": "Login successful.", 
                "user": response.user, 
                "token": response.session.access_token,
                "custom_user_id": user_data['userID'],      # The bigint ID
                "supabase_auth_id": user_data['auth_id'], # The UUID auth ID
                "username": user_data['username']
            }
        else:
            print("Invalid credentials or unconfirmed account.")# Debugging line
            return {"success": False, "message": "Invalid credentials or unconfirmed account."}

    except Exception as e:
        print(f"*** CRITICAL SUPABASE ERROR: {type(e).__name__} - {e}")
        return {"success": False, "message": f"An error occurred: {e}"}
    
def supabase_sign_out():
    from .supabase_client import supabase
    try:
        # This revokes the refresh token associated with the session.
        # It relies on the current Supabase client instance having an active session/token.
        supabase.auth.sign_out()
    except Exception:
        # Ignore exceptions if, for instance, the token is already expired or missing.
        pass