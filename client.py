import requests
import os
import logging

# We don't need to configure logging here as it will be configured in the main script
# Just use the logger that's already configured

def get_token(url, username, password, client_id, grant_type='password'):
    """
    Get OAuth token using password grant type

    Args:
        url (str): The OAuth token endpoint URL
        username (str): The username for authentication
        password (str): The password for authentication
        client_id (str): The OAuth client ID
        grant_type (str, optional): The grant type. Defaults to 'password'

    Returns:
        dict or None: The token response as a dictionary, or None if the request failed
    """
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Form data
    data = {
        'username': username,
        'password': password,
        'client_id': client_id,
        'grant_type': grant_type
    }
    logging.info(f"Attempt to authenticate on URL: {url}")
    logging.info(f"User: {username}")

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=data)

        # Check if the request was successful
        if response.status_code == 200:
            logging.info("Authentication complete")
            return response.json()
        elif response.status_code in [401, 403]:
            error_message = f"Authentication failed with status code: {response.status_code}. Response: {response.text}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        else:
            error_message = f"Request failed with status code: {response.status_code}. Response: {response.text}"
            logging.error(error_message)
            raise RuntimeError(error_message)
    except requests.exceptions.RequestException as e:
        error_message = f"Request error during authentication: {str(e)}"
        logging.error(error_message)
        raise RuntimeError(error_message)


def send_project_data(url, token, project_name, branch, commit_hash, csv_file_path):
    """
    Send project data including text fields and a CSV file to the specified URL

    Args:
        url (str): The API endpoint URL
        token (str): OAuth access token
        project_name (str): Name of the project
        branch (str): Branch name
        commit_hash (str): Commit hash
        csv_file_path (str): Path to the CSV file to upload

    Returns:
        dict or None: The response as a dictionary, or None if the request failed
    """
    # Verify the file exists
    if not os.path.exists(csv_file_path):
        error_message = f"CSV file not found: {csv_file_path}"
        logging.error(error_message)
        raise FileNotFoundError(error_message)

    # Set up authorization header with the token
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Create multipart form data
    form_data = {
        'project': (None, project_name),
        'branch': (None, branch),
        'commit': (None, commit_hash),
        'hash': (None, commit_hash)
    }

    try:
        # Add the CSV file to the form data
        with open(csv_file_path, 'rb') as csv_file:
            form_data['file'] = (os.path.basename(csv_file_path), csv_file, 'text/csv')

            logging.info(f"Attempt to send data to URL: {url}")

            # Send the POST request with the form data and file
            response = requests.post(
                url,
                headers=headers,
                files=form_data,
                verify=False
            )

        # Check if the request was successful
        if response.status_code in [200, 201, 202]:
            logging.info(f"Successfully sent project data: {project_name}, branch: {branch}")
            try:
                return response.json()
            except:
                # If the response is not JSON
                return {"status": "success", "response_text": response.text}
        elif response.status_code in [401, 403]:
            error_message = f"Authentication failed with status code: {response.status_code}. Response: {response.text}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        elif response.status_code == 413:
            error_message = f"File too large. Status code: {response.status_code}. Response: {response.text}"
            logging.error(error_message)
            raise ValueError(error_message)
        else:
            error_message = f"Request failed with status code: {response.status_code}. Response: {response.text}"
            logging.error(error_message)
            raise RuntimeError(error_message)
    except requests.exceptions.RequestException as e:
        error_message = f"Request error during file upload: {str(e)}"
        logging.error(error_message)
        raise RuntimeError(error_message)
    except IOError as e:
        error_message = f"IO error while handling file {csv_file_path}: {str(e)}"
        logging.error(error_message)
        raise IOError(error_message)