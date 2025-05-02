import httpx
import json
from types import TracebackType
from typing import Optional, Type, List, Dict, Any

# Define common headers as a constant
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Origin": "https://wiki.kurobbs.com",
    "Referer": "https://wiki.kurobbs.com/",
    "Source": "h5",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "wiki_type": "9"
    # Removed "Devcode" as it might be specific or dynamic, add back if necessary
}

class KuroWikiApiClient:
    """
    An asynchronous client for interacting with the Kuro BBS Wiki API.
    """
    BASE_URL = "https://api.kurobbs.com/wiki/core/catalogue/item"

    def __init__(self, headers: Optional[Dict[str, str]] = None):
        """
        Initializes the API client.
        Args:
            headers: Optional dictionary of headers to override/extend common headers.
        """
        self.headers = COMMON_HEADERS.copy()
        if headers:
            self.headers.update(headers)
        # Initialize client in __aenter__ to ensure it's managed correctly
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "KuroWikiApiClient":
        """Asynchronous context manager entry."""
        self._client = httpx.AsyncClient(headers=self.headers, timeout=30.0) # Increased timeout
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        """Asynchronous context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None # Ensure client is None after closing

    async def _post_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Internal helper to perform a POST request.
        Args:
            endpoint: The API endpoint path (e.g., "/getPage").
            data: The form data payload.
        Returns:
            The parsed JSON response dictionary, or None if an error occurred.
        """
        if not self._client:
             raise RuntimeError("Client not initialized. Use 'async with KuroWikiApiClient():'")

        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = await self._client.post(url, data=data)

            if response.status_code == 200:
                try:
                    json_data = response.json()
                    return json_data
                except json.JSONDecodeError:
                    print(f"Error: Failed to decode JSON response from {url}")
                    print(f"Response text: {response.text[:500]}...")
                    return None
            else:
                print(f"Request to {url} failed with status code: {response.status_code}")
                print(f"Response content: {response.text[:500]}...")
                return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {url}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during request to {url}: {e}")
            return None

    async def fetch_character_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches the list of characters.
        Returns:
            A list of character records, or None if an error occurred.
        """
        endpoint = "/getPage"
        form_data = {
            "catalogueId": "1105",
            "page": "1",
            "limit": "1000"
        }
        print("Requesting character list...")
        response_data = await self._post_request(endpoint, form_data)

        if response_data:
            if "data" in response_data and \
               "results" in response_data["data"] and \
               "records" in response_data["data"]["results"]:
                print("Character list request successful.")
                return response_data["data"]["results"]["records"]
            else:
                return None
        else:
            # Error already printed in _post_request
            return None

    async def fetch_artifacts_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches the list of artifacts (声骸).
        Returns:
            A list of artifact records, or None if an error occurred.
        """
        endpoint = "/getPage"
        form_data = {
            "catalogueId": "1219",
            "page": "1",
            "limit": "1000"
        }
        print("Requesting artifacts list...") # Updated print message
        response_data = await self._post_request(endpoint, form_data)

        if response_data:
            if "data" in response_data and \
               "results" in response_data["data"] and \
               "records" in response_data["data"]["results"]:
                print("Artifacts list request successful.") # Updated print message
                return response_data["data"]["results"]["records"]
            else:
                print(f"Error: Unexpected response structure for artifacts list: {response_data}")
                return None
        else:
            # Error already printed in _post_request
            return None

    async def fetch_entry_detail(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the detailed content for a specific entry ID.
        Args:
            entry_id: The ID of the entry to fetch.
        Returns:
            The raw response data dictionary for the entry, or None if an error occurred.
        """
        endpoint = "/getEntryDetail"
        form_data = {"id": entry_id}
        
        print(f"Requesting entry detail for ID: {entry_id}...")
        response_data = await self._post_request(endpoint, form_data)

        if response_data:
             # Assuming the raw response is needed, as per original function's docstring
             return response_data
        else:
            # Error already printed in _post_request
            return None
