import os
from report_convert import extract_and_preprocess_esg_data

def convert_all_pdfs(input_dir, output_dir):
    """
    Convert all PDF files in the input directory to preprocessed markdown files in the output directory.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            
            # Generate output filename (replace .pdf with .md)
            md_filename = os.path.splitext(filename)[0] + '.txt'
            md_path = os.path.join(output_dir, md_filename)
            
            print(f"Converting {filename} to markdown...")
            
            try:
                # Extract and preprocess ESG data
                preprocessed_text = extract_and_preprocess_esg_data(pdf_path)
                
                # Write preprocessed text to markdown file
                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(f"# Preprocessed ESG Data for {os.path.splitext(filename)[0]}\n\n")
                    md_file.write(preprocessed_text)
                
                print(f"Successfully converted {filename} to {md_filename}")
            except Exception as e:
                print(f"Error converting {filename}: {str(e)}")

if __name__ == "__main__":
    input_directory = "../ESG_reports"
    output_directory = "../txt_files"
    
    convert_all_pdfs(input_directory, output_directory)
    print("Conversion process completed.")