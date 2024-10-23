import os
from convert_report_text_with_table import process_pdf

def convert_all_pdfs(input_dir, output_dir):
    """
    Convert all PDF files in the input directory to preprocessed text and table files in the output directory.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            
            # Generate output filename (replace .pdf with .txt)
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(output_dir, txt_filename)
            
            print(f"Converting {filename} to text with tables...")
            
            try:
                # Process PDF to extract text and tables
                combined_content = process_pdf(pdf_path)
                
                # Write processed content to text file
                with open(txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(f"# Processed Content for {os.path.splitext(filename)[0]}\n\n")
                    txt_file.write(combined_content)
                
                print(f"Successfully converted {filename} to {txt_filename}")
            except Exception as e:
                print(f"Error converting {filename}: {str(e)}")

if __name__ == "__main__":
    input_directory = "../ESG_reports"
    output_directory = "../txt_files"
    
    convert_all_pdfs(input_directory, output_directory)
    print("Conversion process completed.")
