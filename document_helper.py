#!/usr/bin/env python3
"""
Script to demonstrate how to use the document conversion functionality.
This script provides an easy way for users to convert PDF, XLSX, and CSV files
to cleaned text files that can be used by the General-Purpose RAG Bot.
"""
import os
import sys
import argparse
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

# Add the current directory to path if not already there
if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def show_welcome():
    """Display a welcome message with instructions."""
    welcome_text = """# Document Conversion Tool for General-Purpose RAG Bot

This tool helps you add PDF, Excel, and CSV files to your General-Purpose RAG Bot knowledge base.

## How It Works
1. Place your document files in any location
2. Run this tool with the path to your file
3. The tool will:
   - Extract text from your document
   - Clean the content to focus on relevant information
   - Save a processed text file to app/data
   - Update the vectorstore with the new content

## Supported File Types
- PDF Documents (.pdf)
- Excel Spreadsheets (.xlsx, .xls)
- CSV Files (.csv)
"""
    md = Markdown(welcome_text)
    console.print(md)
    console.print("\n")

def show_examples():
    """Display example commands."""
    console.print("Example commands:", style="bold cyan")
    examples = [
        "./document_helper.py convert path/to/your/document.pdf",
        "./document_helper.py convert path/to/your/rates.xlsx",
        "./document_helper.py convert path/to/your/customer_data.csv",
        "./document_helper.py list",
        "./document_helper.py initialize"
    ]
    for example in examples:
        console.print(f"  {example}")
    console.print("\n")

def list_documents():
    """List all documents in the app/data directory."""
    data_dir = "app/data"
    if not os.path.exists(data_dir):
        console.print("[red]Error: Data directory not found.[/red]")
        return False
    
    table = Table(title="Current Documents")
    table.add_column("Document Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Path", style="blue")
    
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".txt"):
                table.add_row(file, "Text", os.path.join(root, file))
    
    console.print(table)
    return True

def convert_document(file_path):
    """Convert a document to text and initialize the vectorstore."""
    from app.utils.document_converter import save_as_text_file
    from app.utils.vectorstore import create_vectorstore
    
    # Check if file exists
    if not os.path.isfile(file_path):
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        return False
        
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check supported formats
    supported_formats = ['.pdf', '.xlsx', '.xls', '.csv']
    if ext not in supported_formats:
        console.print(f"[red]Error: Unsupported file format: {ext}.[/red]")
        console.print(f"[red]Supported formats are: {', '.join(supported_formats)}[/red]")
        return False
    
    # Use data directory for output
    output_dir = "app/data"
    
    with console.status(f"[bold green]Converting {os.path.basename(file_path)}...[/bold green]"):
        # Convert document to text
        text_path = save_as_text_file(file_path, output_dir)
        
        if not text_path:
            console.print("[red]Error: Failed to convert document[/red]")
            return False
        
        console.print(f"[green]✓ Document converted successfully to:[/green] {text_path}")
    
    # Initialize the vectorstore
    with console.status("[bold green]Updating knowledge base...[/bold green]"):
        try:
            create_vectorstore()
            console.print("[green]✓ Knowledge base updated successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error updating knowledge base: {str(e)}[/red]")
            return False

def initialize_vectorstore():
    """Initialize or reinitialize the vectorstore."""
    from app.utils.vectorstore import create_vectorstore
    
    with console.status("[bold green]Initializing knowledge base...[/bold green]"):
        try:
            create_vectorstore()
            console.print("[green]✓ Knowledge base initialized successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error initializing knowledge base: {str(e)}[/red]")
            return False

def main():
    parser = argparse.ArgumentParser(description="General-Purpose RAG Bot Document Helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a document to text")
    convert_parser.add_argument("file_path", help="Path to the document file (PDF, XLSX, CSV)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all documents in the knowledge base")
    
    # Initialize command
    init_parser = subparsers.add_parser("initialize", help="Initialize the knowledge base")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show welcome message
    show_welcome()
    
    # If no command provided, show examples and exit
    if not args.command:
        show_examples()
        return 0
    
    # Execute the appropriate command
    if args.command == "convert":
        success = convert_document(args.file_path)
    elif args.command == "list":
        success = list_documents()
    elif args.command == "initialize":
        success = initialize_vectorstore()
    else:
        console.print("[red]Invalid command[/red]")
        show_examples()
        return 1
    
    # Show a summary
    if success:
        console.print(Panel("[bold green]Operation completed successfully![/bold green]"))
    else:
        console.print(Panel("[bold red]Operation failed. See errors above.[/bold red]"))
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
