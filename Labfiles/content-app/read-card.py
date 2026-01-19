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

        # Get the business card
        image_file = 'biz-card-1.png'
        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        # Get config settings
        load_dotenv()
        ai_svc_endpoint = os.getenv('ENDPOINT')
        ai_svc_key = os.getenv('KEY')
        analyzer = os.getenv('ANALYZER_NAME')

        # Analyze the business card
        analyze_card(image_file, analyzer, ai_svc_endpoint, ai_svc_key)

        print("\n")

    except Exception as ex:
        print(ex)



def analyze_card(image_file, analyzer, endpoint, key):
    """
    Analyzes a business card image using the Content Understanding REST API.
    
    This function:
    - Reads the image file from disk
    - Submits it to the analyzer via REST API
    - Polls the operation status until completion
    - Extracts and displays the recognized field values
    - Saves the full JSON response to a file
    
    Args:
        image_file (str): Path to the business card image file
        analyzer (str): Name of the analyzer to use
        endpoint (str): Azure AI Services endpoint URL
        key (str): Azure AI Services API key for authentication
    """
    
    # Display which image is being analyzed
    print (f"Analyzing {image_file}")

    # Set the API version for Content Understanding
    # This ensures compatibility with the Azure service
    CU_VERSION = "2025-05-01-preview"

    # Read the image file from disk into memory as binary data
    # Binary mode ('rb') is necessary because images are binary files
    # This data will be sent to the analyzer
    with open(image_file, "rb") as file:
        image_data = file.read()
    
    # Use a POST request to submit the image data to the analyzer
    # POST is used for submitting data for analysis/processing
    print("Submitting request...")
    
    # Prepare HTTP headers for the API request
    # Ocp-Apim-Subscription-Key: Authentication header with API key
    # Content-Type: application/octet-stream indicates binary image data
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"}
    
    # Construct the REST API URL for the analyze operation
    # The :analyze action tells the API to process the image
    # Format: {endpoint}/contentunderstanding/analyzers/{analyzer}:analyze?api-version={version}
    url = f'{endpoint}/contentunderstanding/analyzers/{analyzer}:analyze?api-version={CU_VERSION}'
    
    # Submit the image to the analyzer
    # The analyzer will extract structured data from the business card
    response = requests.post(url, headers=headers, data=image_data)

    # Print the HTTP response status code
    # 202 = Accepted, indicating the analysis has started asynchronously
    print(response.status_code)
    
    # Check if the POST request was successful
    # Status codes 400 or higher indicate an error
    if response.status_code >= 400:
        print(f"ERROR: Failed to submit image for analysis")
        print(f"Response: {response.text}")
        return
    
    # Extract the response JSON and get the operation ID
    # The API returns an ID that can be used to track the analysis progress
    # This ID is essential for polling the status of the analysis
    response_json = response.json()
    id_value = response_json.get("id")
    
    # Verify that we got a valid operation ID
    if not id_value:
        print("ERROR: No operation ID returned from the API")
        return

    # Use a GET request to check the status of the analysis operation
    # This is where we'll poll to see when the analysis completes
    print ('Getting results...')
    time.sleep(1)  # Small delay before first poll
    
    # Construct the URL to retrieve the analysis results
    # Format: {endpoint}/contentunderstanding/analyzerResults/{id}?api-version={version}
    result_url = f'{endpoint}/contentunderstanding/analyzerResults/{id_value}?api-version={CU_VERSION}'
    
    # Submit the GET request to retrieve the current status
    result_response = requests.get(result_url, headers=headers)
    print(result_response.status_code)  # Print HTTP status code
    
    # Check if the GET request was successful
    if result_response.status_code >= 400:
        print(f"ERROR: Failed to retrieve analysis results")
        print(f"Response: {result_response.text}")
        return

    # Keep polling until the analysis is complete
    # The status will be "Running" until analysis is done, then "Succeeded" or "Failed"
    status = result_response.json().get("status")
    while status == "Running":
        time.sleep(1)  # Wait before polling again to avoid overwhelming the service
        result_response = requests.get(result_url, headers=headers)
        status = result_response.json().get("status")

    # Process the analysis results once the operation completes
    if status == "Succeeded":
        print("Analysis succeeded:\n")
        
        # Extract the complete JSON response from the API
        result_json = result_response.json()
        
        # Save the full JSON response to a file for reference
        # This is useful for debugging and understanding the response structure
        output_file = "results.json"
        with open(output_file, "w") as json_file:
            json.dump(result_json, json_file, indent=4)  # indent=4 makes the JSON readable
            print(f"Response saved in {output_file}\n")

        # Extract the content from the results
        # The API response structure contains a 'result' object with 'contents' array
        # contents is a list of analyzed items (typically just one for a single image)
        contents = result_json["result"]["contents"]
        
        # Iterate through each content item (in this case, the business card)
        for content in contents:
            # Check if the content has 'fields' (extracted data)
            # Not all content types may have fields, so we check first
            if "fields" in content:
                fields = content["fields"]
                
                # Iterate through each field and display its value
                # The field_name is the key (e.g., "name", "email", "phone")
                # The field_data contains type and value information
                # This loop extracts and displays all recognized information from the card
                for field_name, field_data in fields.items():
                    # Extract the value based on the field's data type
                    # Different types require accessing different value properties
                    # This is important because the API returns type-specific value fields
                    if field_data['type'] == "string":
                        print(f"{field_name}: {field_data['valueString']}")
                    elif field_data['type'] == "number":
                        print(f"{field_name}: {field_data['valueNumber']}")
                    elif field_data['type'] == "integer":
                        print(f"{field_name}: {field_data['valueInteger']}")
                    elif field_data['type'] == "date":
                        print(f"{field_name}: {field_data['valueDate']}")
                    elif field_data['type'] == "time":
                        print(f"{field_name}: {field_data['valueTime']}")
                    elif field_data['type'] == "array":
                        # Arrays can contain multiple values separated by commas
                        print(f"{field_name}: {field_data['valueArray']}")
    else:
        # Handle analysis failure
        print(f"Analysis failed with status: {status}\n")
        result_json = result_response.json()
        print("Error details:")
        print(result_json)  # Print the full error response for debugging





if __name__ == "__main__":
    main()        
