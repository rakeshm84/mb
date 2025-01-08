import requests
from django.conf import settings

class PloiAPI:
    base_url = "https://ploi.io/api"
    
    def __init__(self, api_token=None):
        self.api_token = api_token or settings.PLOI_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_servers(self):
        """Fetch all servers."""
        url = f"{self.base_url}/servers"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    def get_server(self, server_id):
        """Fetch a specific server by ID."""
        url = f"{self.base_url}/servers/{server_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_server(self, provider, name, region, plan):
        """Create a new server."""
        url = f"{self.base_url}/servers"
        payload = {
            "provider": provider,
            "name": name,
            "region": region,
            "plan": plan,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def delete_server(self, server_id):
        """Delete a server by ID."""
        url = f"{self.base_url}/servers/{server_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_databases(self, server_id):
        """ List all the databases available in the server """
        url = f"{self.base_url}/servers/{server_id}/databases"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
