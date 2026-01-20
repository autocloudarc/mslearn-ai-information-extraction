from dotenv import load_dotenv
import os
# Import credentials module for authentication
from azure.core.credentials import AzureKeyCredential
# Import SearchClient to interact with Azure Cognitive Search
from azure.search.documents import SearchClient


def main():
    """
    Main function that runs the interactive search application.
    
    This function:
    - Loads environment variables
    - Creates a search client
    - Prompts the user for search queries
    - Executes searches against the search index
    - Displays results with extracted entities (locations, people, key phrases)
    """

    # Clear the console screen for a clean interface
    # Works on both Windows (cls) and Unix-like systems (clear)
    os.system('cls' if os.name=='nt' else 'clear')

    try:

        # Get config settings from the .env file
        # load_dotenv() reads environment variables from .env file
        load_dotenv()
        # Retrieve the Azure Cognitive Search endpoint URL
        search_endpoint = os.getenv('SEARCH_ENDPOINT')
        # Retrieve the query API key for authentication
        query_key = os.getenv('QUERY_KEY')
        # Retrieve the name of the search index to query
        index = os.getenv('INDEX_NAME')

        # Create a search client that will communicate with Azure Cognitive Search
        # Parameters:
        #   - search_endpoint: The URL of your search service
        #   - index: The name of the index to search
        #   - AzureKeyCredential(query_key): Authentication using the API key
        search_client = SearchClient(search_endpoint, index, AzureKeyCredential(query_key))

        # Loop until the user types 'quit'
        # This creates an interactive search experience where users can enter multiple queries
        while True:
            # Prompt the user to enter a search query
            # The query text will be used to search documents in the index
            query_text = input("Enter a query (or type 'quit' to exit): ")
            
            # Check if user wants to exit the application
            if query_text.lower() == "quit":
                break
            
            # Validate that the user entered something
            # Empty queries don't make sense and waste resources
            if len(query_text) == 0:
                print("Please enter a query.")
                continue

            # Clear the console screen before displaying results
            # This gives a cleaner appearance to the output
            os.system('cls' if os.name=='nt' else 'clear')
            
            # Execute the search query against the search index
            # Parameters:
            #   - search_text: The query text to search for (full-text search)
            #   - select: Specifies which fields to return in results
            #     * metadata_storage_name: Document name/filename
            #     * locations: Extracted location entities
            #     * people: Extracted person entities
            #     * keyphrases: Extracted key phrases from the document
            #   - order_by: Sort results by document name
            #   - include_total_count: Include total number of matching documents
            found_documents = search_client.search(
                search_text=query_text,
                select=["metadata_storage_name", "locations", "people", "keyphrases"],
                order_by=["metadata_storage_name"],
                include_total_count=True
            )

            # Parse and display the search results
            # Get the total count of documents that matched the query
            print(f"\nSearch returned {found_documents.get_count()} documents:")
            
            # Iterate through each document returned by the search
            for document in found_documents:
                # Display the document name/filename
                print(f"\nDocument: {document["metadata_storage_name"]}")
                
                # Display extracted locations (cities, countries, etc.)
                # These are entities recognized by Azure AI services
                print(" - Locations:")
                for location in document["locations"]:
                    print(f"   - {location}")
                
                # Display extracted people (person names recognized in the document)
                # This is useful for finding documents mentioning specific people
                print(" - People:")
                for person in document["people"]:
                    print(f"   - {person}")
                
                # Display extracted key phrases (important terms/phrases from the document)
                # These summarize the main topics of the document
                print(" - Key phrases:")
                for phrase in document["keyphrases"]:
                    print(f"   - {phrase}")

    except Exception as ex:
        # Catch and display any errors that occur
        # This helps with debugging connection, authentication, or query issues
        print(ex)



if __name__ == "__main__":
    # Entry point of the script
    # This ensures main() only runs when the script is executed directly,
    # not when it's imported as a module in another script
    main()        
