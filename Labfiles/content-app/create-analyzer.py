from dotenv import load_dotenv
import os
import sys
import time
import requests
import json


def main():

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:

        # Get the business card schema
        with open("biz-card.json", "r") as file:
            schema_json = json.load(file)
        
        card_schema = json.dumps(schema_json)

        # Get config settings
        load_dotenv()
        ai_svc_endpoint = os.getenv('ENDPOINT')
        ai_svc_key = os.getenv('KEY')
        analyzer = os.getenv('ANALYZER_NAME')

        # Create the analyzer
        create_analyzer(card_schema, analyzer, ai_svc_endpoint, ai_svc_key)

        print("\n")

    except Exception as ex:
        print(ex)



def create_analyzer(schema, analyzer, endpoint, key):
    """
    Creates a Content Understanding analyzer using the REST API.
    
    This function:
    - Prints the analyzer creation status
    - Deletes any existing analyzer with the same name
    - Submits a PUT request to create a new analyzer with the provided schema
    - Polls the operation status until completion
    - Reports success or failure
    
    Args:
        schema (str): JSON string defining the analyzer schema (field definitions)
        analyzer (str): Name of the analyzer to create
        endpoint (str): Azure AI Services endpoint URL
        key (str): Azure AI Services API key for authentication
    """
    
    # Display status to user
    print (f"Creating {analyzer}")

    # Set the API version for Content Understanding
    # This ensures compatibility with the Azure service
    CU_VERSION = "2025-05-01-preview"

    # Prepare HTTP headers for the API requests
    # Ocp-Apim-Subscription-Key: Authentication header with API key
    # Content-Type: Specifies that we're sending JSON data
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"}

    # Construct the REST API URL for the analyzer endpoint
    # For Azure AI Foundry, the Content Understanding API uses the /projects/<project-id>/... path
    # The endpoint already includes the project path
    # Format: {endpoint}/contentunderstanding/analyzers/{analyzer}?api-version={version}
    url = f"{endpoint}/contentunderstanding/analyzers/{analyzer}?api-version={CU_VERSION}"
    print(f"DEBUG: URL = {url}")

    # Delete the analyzer if it already exists
    # This is important because we cannot create an analyzer with a duplicate name
    # The DELETE request silently succeeds whether or not the analyzer exists
    response = requests.delete(url, headers=headers)
    print(response.status_code)  # Print HTTP status code (204 = No Content, 404 = Not Found)
    time.sleep(1)  # Small delay to avoid rate limiting

    # Now create the analyzer with the provided schema
    # The schema parameter contains the field definitions in JSON format
    # HTTP PUT is used for creating/updating resources
    response = requests.put(url, headers=headers, data=(schema))
    print(response.status_code)  # Print HTTP status code (202 = Accepted for async operation)
    
    # If the request failed, print the error response
    if response.status_code >= 400:
        print(f"ERROR: PUT request failed")
        print(f"Response: {response.text}")
        return

    # Extract the callback URL from the response headers
    # The Operation-Location header contains the URL to check the operation status
    # This is how we'll poll the service to see when the analyzer is ready
    callback_url = response.headers["Operation-Location"]

    # Check the status of the asynchronous operation
    # Azure uses asynchronous operations for long-running tasks
    time.sleep(1)  # Small delay to allow the operation to process
    result_response = requests.get(callback_url, headers=headers)

    # Keep polling until the operation is no longer running
    # The status will be "Running", "Succeeded", or "Failed"
    # We loop until status changes to one of the terminal states
    status = result_response.json().get("status")
    while status == "Running":
        time.sleep(1)  # Wait before polling again
        result_response = requests.get(callback_url, headers=headers)
        status = result_response.json().get("status")

    # Extract the final status from the response
    result = result_response.json().get("status")
    print(result)  # Display the final status
    
    # Report the outcome to the user
    if result == "Succeeded":
        print(f"Analyzer '{analyzer}' created successfully.")
    else:
        print("Analyzer creation failed.")
        print(result_response.json())  # Print error details from the response




if __name__ == "__main__":
    main()        
