from dotenv import load_dotenv
import os

# Add references
# Import Azure credentials for API authentication
from azure.core.credentials import AzureKeyCredential

# Import the Document Analysis client from Azure AI Form Recognizer SDK
# This client is used to communicate with the Azure Document Intelligence service
from azure.ai.formrecognizer import DocumentAnalysisClient



def main():

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:
        # Get config settings
        load_dotenv()
        endpoint = os.getenv('ENDPOINT')
        key = os.getenv('KEY')


        # Set analysis settings
        fileUri = "https://github.com/MicrosoftLearning/mslearn-ai-information-extraction/blob/main/Labfiles/prebuilt-doc-intelligence/sample-invoice/sample-invoice.pdf?raw=true"
        fileLocale = "en-US"
        fileModelId = "prebuilt-invoice"

        print(f"\nConnecting to Forms Recognizer at: {endpoint}")
        print(f"Analyzing invoice at: {fileUri}")


        # Create the client
        # Initialize the DocumentAnalysisClient with the endpoint and API key
        # This client object is our interface to the Azure Document Intelligence service
        # AzureKeyCredential handles the authentication using the API key
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )



        # Analyse the invoice
        # begin_analyze_document_from_url submits the document for analysis
        # This is an asynchronous operation that returns a poller object
        # Parameters:
        #   - fileModelId: The prebuilt model to use ("prebuilt-invoice" extracts invoice-specific fields)
        #   - fileUri: The URL of the document to analyze
        #   - locale: The language/region of the document ("en-US" for English)
        # The poller allows us to track the status of the analysis operation
        poller = document_analysis_client.begin_analyze_document_from_url(
            fileModelId, fileUri, locale=fileLocale
        )



        # Display invoice information to the user
        # poller.result() waits for the analysis to complete and returns the results
        # The results object contains a list of analyzed documents
        # For each document, we can extract specific fields that the prebuilt-invoice model recognizes
        receipts = poller.result()
        
        # Iterate through each analyzed document (typically just one in this case)
        for idx, receipt in enumerate(receipts.documents):
            
            # Extract the Vendor Name field from the invoice
            # The get() method safely retrieves the field, returning None if not found
            # Each field has a 'value' property containing the extracted data
            # and a 'confidence' score (0-1) indicating how confident the model is
            vendor_name = receipt.fields.get("VendorName")
            if vendor_name:
                print(f"\nVendor Name: {vendor_name.value}, with confidence {vendor_name.confidence}.")

            # Extract the Customer Name field
            # This represents who the invoice is being sent to
            customer_name = receipt.fields.get("CustomerName")
            if customer_name:
                print(f"Customer Name: '{customer_name.value}', with confidence {customer_name.confidence}.")

            # Extract the Invoice Total field
            # This field contains a currency value with both symbol and amount
            # The prebuilt model automatically recognizes the currency and converts to a structured format
            invoice_total = receipt.fields.get("InvoiceTotal")
            if invoice_total:
                # invoice_total.value is a CurrencyValue object with 'symbol' and 'amount' properties
                print(f"Invoice Total: '{invoice_total.value.symbol}{invoice_total.value.amount}', with confidence {invoice_total.confidence}.")


            


    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")

if __name__ == "__main__":
    main()        
