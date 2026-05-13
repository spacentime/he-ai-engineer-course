import requests     
import json

def save_json_to_file(data, filename):
    """
    Save JSON data to a file.
    
    Args:
        data: Dictionary or JSON string to save
        filename: Name of the file to save to
    """
    with open(filename, 'w') as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2)

def get_api_data(url):
    """
    Make an HTTP GET request to the specified URL.
    
    Args:
        url: The API endpoint URL
        
    Returns:
        Response object from the request
    """
    response = requests.get(url)
    print(response.status_code)  # Should print 200 if successful
    print(response.json())  # Print the JSON response from the API
    return response


# Get request from API
response = get_api_data("https://api.github.com/users/github")
save_json_to_file(response.json(), "github_user.json")  # Save the JSON response to a file

