"""
Document converter module for the General-Purpose RAG Bot.
This module handles the conversion of different document formats (PDF, XLSX, CSV)
to cleaned text that can be processed by the document processor.
"""
import os
import re
import PyPDF2
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from typing import List, Optional, Dict, Any

# Common domain-specific terms to keep even if they are stopwords
DOMAIN_TERMS = {
    'about', 'above', 'across', 'after', 'against', 'along', 'among', 
    'around', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 
    'between', 'beyond', 'but', 'by', 'despite', 'down', 'during', 
    'except', 'for', 'from', 'in', 'inside', 'into', 'like', 'near',
    'of', 'off', 'on', 'onto', 'out', 'outside', 'over', 'past',
    'since', 'through', 'throughout', 'to', 'toward', 'under', 'underneath',
    'until', 'up', 'upon', 'with', 'within', 'without'
}

# Load stopwords but keep important domain terms
STOPWORDS = set(stopwords.words('english')) - DOMAIN_TERMS

class DocumentCleaner:
    """Class for cleaning and filtering text to keep relevant content."""
    
    def __init__(self):
        """Initialize the document cleaner."""
        # Content quality patterns - looking for well-structured content
        self.content_patterns = [
            r'\b(section|chapter|part|introduction|conclusion)\b',
            r'\b(figure|table|chart|graph|diagram)\b',
            r'\b(example|definition|summary|overview)\b',
            r'\b(important|note|key|main|critical)\b',
            r'^\d+\.\s.*',  # Numbered lists
            r'^\*\s.*',     # Bullet points
            r'^-\s.*',      # Dash bullet points
            r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',  # Proper nouns
            r'\b\d+(\.\d+)?%\b',  # Percentages
            r'\$\d+(\.\d+)?\b',   # Dollar amounts
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.content_patterns]
    
    def is_relevant_content(self, text: str) -> bool:
        """
        Check if a piece of text contains meaningful content.
        
        Args:
            text: The text to check
            
        Returns:
            bool: True if the text contains meaningful content, False otherwise
        """
        # Very short texts are unlikely to be meaningful
        if len(text.strip()) < 15:
            return False
            
        # Text with multiple sentences is usually meaningful
        if text.count('.') >= 2:
            return True
            
        # Check for content quality patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
                
        # Default to keeping content unless very short
        return len(text.strip()) > 50
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace, special characters, and standardizing format.
        
        Args:
            text: The text to clean
            
        Returns:
            str: The cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep periods, commas, and other useful punctuation
        text = re.sub(r'[^\w\s.,;:?!-]', '', text)
        
        # Remove headers, page numbers, and footers (common patterns)
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)  # Standalone numbers like page numbers
        
        return text.strip()
    
    def filter_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """
        Filter paragraphs to keep only those containing meaningful content.
        
        Args:
            paragraphs: List of paragraphs to filter
            
        Returns:
            List[str]: Filtered list of paragraphs
        """
        return [p for p in paragraphs if p and self.is_relevant_content(p)]
    
    def process_text(self, text: str) -> str:
        """
        Process a text document to clean it and filter for relevant content.
        
        Args:
            text: The text to process
            
        Returns:
            str: The processed text with meaningful content
        """
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Split into paragraphs
        paragraphs = cleaned_text.split('\n\n')
        
        # Filter paragraphs for meaningful content
        relevant_paragraphs = self.filter_paragraphs(paragraphs)
        
        # Join the relevant paragraphs back together
        if relevant_paragraphs:
            return '\n\n'.join(relevant_paragraphs)
        else:
            # If no relevant paragraphs were found, check if the whole document might be relevant
            # This handles cases where the formatting doesn't have clear paragraph breaks
            if len(cleaned_text.strip()) > 100:  # Basic check for minimum meaningful content
                return cleaned_text
            return ""


class PDFConverter:
    """Class for converting PDF files to cleaned text."""
    
    def __init__(self, cleaner: DocumentCleaner):
        """
        Initialize the PDF converter.
        
        Args:
            cleaner: An instance of DocumentCleaner for text cleaning
        """
        self.cleaner = cleaner
    
    def convert_to_text(self, pdf_path: str) -> str:
        """
        Convert a PDF file to text.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: The extracted and cleaned text
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
        
        # Process the extracted text to clean and filter it
        processed_text = self.cleaner.process_text(text)
        return processed_text


class ExcelConverter:
    """Class for converting Excel files to cleaned text."""
    
    def __init__(self, cleaner: DocumentCleaner):
        """
        Initialize the Excel converter.
        
        Args:
            cleaner: An instance of DocumentCleaner for text cleaning
        """
        self.cleaner = cleaner
    
    def convert_to_text(self, excel_path: str) -> str:
        """
        Convert an Excel file to text.
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            str: The extracted and cleaned text
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(excel_path)
            all_text = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Convert column names to text
                headers = " | ".join(str(col) for col in df.columns)
                all_text.append(f"Sheet: {sheet_name}")
                all_text.append(f"Headers: {headers}")
                
                # Convert each row to text
                for _, row in df.iterrows():
                    row_text = " | ".join(str(val) for val in row.values)
                    # Check if this row has meaningful content
                    if self.cleaner.is_relevant_content(row_text):
                        all_text.append(row_text)
            
            # Join all text
            text = "\n".join(all_text)
            
            # Process the extracted text to clean and filter it
            processed_text = self.cleaner.process_text(text)
            return processed_text
        except Exception as e:
            print(f"Error extracting text from Excel file {excel_path}: {e}")
            return ""


class CSVConverter:
    """Class for converting CSV files to cleaned text."""
    
    def __init__(self, cleaner: DocumentCleaner):
        """
        Initialize the CSV converter.
        
        Args:
            cleaner: An instance of DocumentCleaner for text cleaning
        """
        self.cleaner = cleaner
    
    def convert_to_text(self, csv_path: str) -> str:
        """
        Convert a CSV file to text.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            str: The extracted and cleaned text
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            all_text = []
            
            # Convert column names to text
            headers = " | ".join(str(col) for col in df.columns)
            all_text.append(f"Headers: {headers}")
            
            # Convert each row to text
            for _, row in df.iterrows():
                row_text = " | ".join(str(val) for val in row.values)
                # Check if this row has meaningful content
                if self.cleaner.is_relevant_content(row_text):
                    all_text.append(row_text)
            
            # Join all text
            text = "\n".join(all_text)
            
            # Process the extracted text to clean and filter it
            processed_text = self.cleaner.process_text(text)
            return processed_text
        except Exception as e:
            print(f"Error extracting text from CSV file {csv_path}: {e}")
            return ""


def convert_document(file_path: str) -> Optional[str]:
    """
    Convert a document to cleaned text based on its file extension.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Optional[str]: The cleaned text from the document or None if conversion failed
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    # Initialize the document cleaner
    cleaner = DocumentCleaner()
    
    # Get the file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Convert based on file extension
    if ext == '.pdf':
        converter = PDFConverter(cleaner)
        return converter.convert_to_text(file_path)
    elif ext == '.xlsx' or ext == '.xls':
        converter = ExcelConverter(cleaner)
        return converter.convert_to_text(file_path)
    elif ext == '.csv':
        converter = CSVConverter(cleaner)
        return converter.convert_to_text(file_path)
    else:
        print(f"Unsupported file format: {ext}")
        return None


def save_as_text_file(file_path: str, output_dir: str = None) -> Optional[str]:
    """
    Convert a document and save it as a text file.
    
    Args:
        file_path: Path to the document file
        output_dir: Directory to save the text file (default is same as input file)
        
    Returns:
        Optional[str]: Path to the created text file or None if conversion failed
    """
    # Convert the document to text
    text_content = convert_document(file_path)
    if text_content is None:
        return None
    
    # If no output directory is specified, use the same directory as the input file
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the output file path
    file_name = os.path.basename(file_path)
    name_without_ext, _ = os.path.splitext(file_name)
    output_path = os.path.join(output_dir, f"{name_without_ext}.txt")
    
    # Write the text to the file
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text_content)
        print(f"Converted document saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving text file: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        save_as_text_file(file_path, output_dir)
    else:
        print("Please provide a file path as an argument.")
