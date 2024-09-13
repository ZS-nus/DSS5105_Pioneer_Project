from fetch_storage import initialize_firebase, fetch_file_from_storage, list_all_files
from OCR_test import extract_text_from_pdf, save_as_markdown

if __name__ == "__main__":
    # Initialize Firebase
    initialize_firebase()
    
    # List all files in the bucket and print them
    file_names = list_all_files()
    print("Files in bucket:")
    for file_name in file_names:
        print(file_name)
    
    # Prompt the user to enter a file name
    user_input = input("Enter the file name you want to download: ")
    
    # Check if the entered file name exists in the list
    if user_input in file_names:
        # Fetch the file from storage
        local_file_name = user_input.split('/')[-1]  # Extract the file name from the path
        download_dir = '../ESG_reports'  # Directory to save the file
        fetch_file_from_storage(user_input, local_file_name, download_dir)
        
        # # Extract text from the downloaded PDF
        # local_file_path = f"{download_dir}/{local_file_name}"
        # text = extract_text_from_pdf(local_file_path)
        
        # # Save the extracted text as a markdown file
        # output_md = "output.md"
        # save_as_markdown(text, output_md)
    else:
        print(f"Error: The file '{user_input}' does not exist in the bucket.")