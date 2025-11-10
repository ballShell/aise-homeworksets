import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

# Create a Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

def check_trips():
    """Fetches all trips from the 'trips' table and prints them."""
    try:
        response = supabase.table("trips").select("*").execute()
        print("Trips found in the database:")
        print(response.data)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_trips()