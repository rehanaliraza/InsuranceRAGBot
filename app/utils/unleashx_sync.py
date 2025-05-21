"""
Module to sync knowledge base from TryUnleashX API

This module provides functionality to:
1. Fetch agent scope information (knowledge files, links, pages) from TryUnleashX API
2. Download and process files (PDF, XLSX, CSV) from URLs
3. Scrape content from web links
4. Extract text from HTML pages
5. Save all content as text files in a dedicated directory
6. Clean up old files before syncing
"""
import os
import requests
import json
import tempfile
import logging
import shutil
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger("unleashx_sync")

# Directory for storing downloaded and processed files
DATA_DIR = "app/data"
UNLEASHX_DIR = os.path.join(DATA_DIR, "unleashx")
PROCESSED_TXT_DIR = os.path.join(DATA_DIR, "processed_txt")

def ensure_directories():
    """Ensure necessary directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UNLEASHX_DIR, exist_ok=True)
    os.makedirs(PROCESSED_TXT_DIR, exist_ok=True)
    
def clean_knowledge_base():
    """
    Clean up the UnleashX directory to remove old files
    
    Returns:
        Tuple[bool, int]: Success status and count of removed files
    """
    try:
        total_file_count = 0
        
        # Clean processed text files
        if os.path.exists(PROCESSED_TXT_DIR):
            file_count = 0
            for filename in os.listdir(PROCESSED_TXT_DIR):
                file_path = os.path.join(PROCESSED_TXT_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    file_count += 1
            logger.info(f"Cleaned {file_count} text files from {PROCESSED_TXT_DIR}")
            total_file_count += file_count
        else:
            logger.info(f"Directory {PROCESSED_TXT_DIR} does not exist, nothing to clean")
        
        # We'll keep the files in UNLEASHX_DIR as requested
        logger.info(f"Keeping original files in {UNLEASHX_DIR}")
            
        return True, total_file_count
    except Exception as e:
        logger.error(f"Error cleaning knowledge base directories: {str(e)}")
        return False, 0
    
def fetch_agent_scope(token: str, agent_id: int) -> Dict[str, Any]:
    """
    Fetch agent scope information from TryUnleashX API
    
    Args:
        token: API token for authentication
        agent_id: ID of the agent to fetch scope for
        
    Returns:
        Dict containing the agent scope information
    """
    logger.info(f"Fetching agent scope for agent ID: {agent_id}")
    
    url = "https://www.tryunleashx.com/api/agent-scope/summary"
    
    headers = {
        "token": token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "agent_id": agent_id
    }
    
    try:
        # Log request details for debugging
        logger.info(f"Making API request to: {url}")
        
        # Use retry pattern for better reliability
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(url, headers=headers, json=payload, timeout=30)
                
                # Log response details
                logger.info(f"Response status code: {response.status_code}")
                
                if response.status_code == 200:
                    break
                    
                # Handle rate limiting
                if response.status_code == 429:
                    retry_count += 1
                    wait_time = min(2 ** retry_count, 60)  # Exponential backoff
                    logger.warning(f"Rate limited, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                # Handle other error codes
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return {}
                
            except requests.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.warning(f"Retrying in {wait_time} seconds... ({retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached ({max_retries})")
                    return {}
        
        # Now handle the response contents
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response")
            return {}
            
        if data.get("error", True):
            logger.error(f"API returned error: {data.get('message', 'Unknown error')}")
            return {}
            
        # Validate response data
        agent_data = data.get("data", {})
        if not agent_data:
            logger.error("API response missing data field or data is empty")
            return {}
            
        # Log summary of fetched data
        knowledge_files = agent_data.get("knowledge_files", [])
        knowledge_links = agent_data.get("knowledge_links", [])
        knowledge_pages = agent_data.get("knowledge_pages", [])
        
        logger.info(f"Fetched agent data: {len(knowledge_files)} files, {len(knowledge_links)} links, {len(knowledge_pages)} pages")
            
        return agent_data
    except Exception as e:
        logger.error(f"Error fetching agent scope: {str(e)}")
        return {}

def download_file(url: str, output_path: str) -> bool:
    """
    Download a file from a URL to the specified path
    
    Args:
        url: URL of the file to download
        output_path: Path to save the downloaded file
        
    Returns:
        bool: Whether the download was successful
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Downloaded file from {url} to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading file from {url}: {str(e)}")
        return False

def scrape_website(url: str, timeout: int = 30) -> str:
    """
    Scrape content from a website
    
    Args:
        url: URL of the website to scrape
        timeout: Timeout in seconds for the request
        
    Returns:
        str: Extracted text content
    """
    try:
        # Ensure URL has proper scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        logger.info(f"Scraping content from: {url}")
        
        # Set user agent to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request with retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.warning(f"Request failed, retrying in {wait_time} seconds... ({retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached ({max_retries})")
                    return f"Error scraping website after {max_retries} attempts: {str(e)}"
        
        # Check if we got non-text content
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type and 'text/plain' not in content_type:
            logger.warning(f"Non-text content detected: {content_type}")
            return f"Unsupported content type: {content_type}"
        
        # Use BeautifulSoup for better HTML parsing
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'iframe', 'noscript']):
            element.extract()
            
        # Try to find main content container
        main_content = None
        for container in ['main', 'article', 'section', 'div[role="main"]', '#content', '.content', '#main', '.main']:
            content = soup.select(container)
            if content:
                main_content = content[0]
                break
                
        # Use the targeted content or the whole body if no main content found
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
            
        # Clean up text: break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Check if we got any meaningful content
        if len(text.strip()) < 100:  # arbitrary minimum
            logger.warning(f"Very little content extracted from {url}")
            
        return text
    except Exception as e:
        logger.error(f"Error scraping website {url}: {str(e)}")
        return f"Error scraping website: {str(e)}"

def process_html_content(html_content: str) -> str:
    """
    Process HTML content to extract text
    
    Args:
        html_content: HTML content to process
        
    Returns:
        str: Extracted text content
    """
    try:
        if not html_content:
            logger.warning("Empty HTML content provided")
            return ""
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove non-content elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'iframe', 'noscript']):
            element.extract()
            
        # Look for quality content markers (paragraphs with substance)
        quality_paragraphs = []
        for p in soup.find_all(['p', 'div', 'section', 'article']):
            text = p.get_text().strip()
            # Keep paragraphs with meaningful content (non-empty, more than just a few words)
            if text and len(text) > 40:
                quality_paragraphs.append(text)
                
        if quality_paragraphs:
            # If we found quality paragraphs, use those
            text = "\n\n".join(quality_paragraphs)
        else:
            # Otherwise, use all text
            text = soup.get_text()
            
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace and normalize newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    except Exception as e:
        logger.error(f"Error processing HTML content: {str(e)}")
        return f"Error processing HTML content: {str(e)}"

def process_knowledge_files(knowledge_files: List[Dict[str, Any]], token: str) -> List[str]:
    """
    Process knowledge files from TryUnleashX
    
    Args:
        knowledge_files: List of knowledge file information
        token: API token for authentication
        
    Returns:
        List[str]: List of paths to processed text files
    """
    logger.info(f"Processing {len(knowledge_files)} knowledge files")
    
    processed_files = []
    
    for file_info in knowledge_files:
        try:
            file_id = file_info.get("id")
            file_name = file_info.get("name", f"unknown_{file_id}")
            file_url = file_info.get("url")
            
            if not file_url:
                logger.warning(f"No URL provided for file {file_name}, skipping")
                continue
                
            # Create a clean filename
            clean_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in file_name)
            
            # Get the file extension from URL
            parsed_url = urlparse(file_url)
            path = parsed_url.path
            _, extension = os.path.splitext(path)
            
            # Define output paths
            original_file_path = os.path.join(UNLEASHX_DIR, f"{clean_name}{extension}")
            
            # Download the file directly to the unleashx directory (keeping original)
            success = download_file(file_url, original_file_path)
            
            if not success:
                logger.error(f"Failed to download file: {file_url}")
                continue
                
            logger.info(f"Successfully downloaded file: {file_name} -> {original_file_path}")
            
            # Convert the original file to text
            from app.utils.document_converter import save_as_text_file
            text_path = save_as_text_file(original_file_path, PROCESSED_TXT_DIR)
            
            if text_path:
                logger.info(f"Successfully processed file: {file_name} -> {text_path}")
                processed_files.append(text_path)
            else:
                logger.error(f"Failed to convert file: {file_name}")
                
        except Exception as e:
            logger.error(f"Error processing knowledge file: {str(e)}")
            
    return processed_files

def process_knowledge_links(knowledge_links: List[Dict[str, Any]]) -> List[str]:
    """
    Process knowledge links from TryUnleashX
    
    Args:
        knowledge_links: List of knowledge link information
        
    Returns:
        List[str]: List of paths to processed text files
    """
    logger.info(f"Processing {len(knowledge_links)} knowledge links")
    
    processed_files = []
    
    for link_info in knowledge_links:
        try:
            link_id = link_info.get("id")
            link_name = link_info.get("name", f"link_{link_id}")
            link_url = link_info.get("url")
            
            if not link_url:
                logger.warning(f"No URL provided for link {link_name}, skipping")
                continue
                
            # Prepend http:// if the URL doesn't have a scheme
            if not link_url.startswith(('http://', 'https://')):
                link_url = 'https://' + link_url
                
            # Create a clean filename
            clean_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in link_name)
            output_path = os.path.join(PROCESSED_TXT_DIR, f"{clean_name}.txt")
            
            # Scrape the website
            content = scrape_website(link_url)
            
            if not content:
                logger.warning(f"No content extracted from {link_url}")
                continue
                
            # Write content to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Source: {link_url}\n\n")
                f.write(content)
                
            logger.info(f"Successfully processed link: {link_name} -> {output_path}")
            processed_files.append(output_path)
                
        except Exception as e:
            logger.error(f"Error processing knowledge link: {str(e)}")
            
    return processed_files

def process_knowledge_pages(knowledge_pages: List[Dict[str, Any]]) -> List[str]:
    """
    Process knowledge pages from TryUnleashX
    
    Args:
        knowledge_pages: List of knowledge page information
        
    Returns:
        List[str]: List of paths to processed text files
    """
    logger.info(f"Processing {len(knowledge_pages)} knowledge pages")
    
    processed_files = []
    
    for page_info in knowledge_pages:
        try:
            page_id = page_info.get("id")
            page_name = page_info.get("name", f"page_{page_id}")
            html_content = page_info.get("html")
            
            if not html_content:
                logger.warning(f"No HTML content provided for page {page_name}, skipping")
                continue
                
            # Create a clean filename
            clean_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in page_name)
            
            # Save original HTML content
            html_file_path = os.path.join(UNLEASHX_DIR, f"{clean_name}.html")
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"Saved original HTML content: {page_name} -> {html_file_path}")
            
            # Process HTML content and save as text
            output_path = os.path.join(PROCESSED_TXT_DIR, f"{clean_name}.txt")
            content = process_html_content(html_content)
            
            if not content:
                logger.warning(f"No content extracted from HTML for page {page_name}")
                continue
                
            # Write content to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Source: Knowledge Page - {page_name}\n\n")
                f.write(content)
                
            logger.info(f"Successfully processed page: {page_name} -> {output_path}")
            processed_files.append(output_path)
                
        except Exception as e:
            logger.error(f"Error processing knowledge page: {str(e)}")
            
    return processed_files

def sync_knowledge_base(token: str, agent_id: int) -> Dict[str, Any]:
    """
    Sync knowledge base from TryUnleashX API
    
    Args:
        token: API token for authentication
        agent_id: ID of the agent to sync knowledge for
        
    Returns:
        Dict with status and summary information
    """
    logger.info(f"Starting knowledge base sync for agent ID: {agent_id}")
    
    # Ensure directories exist
    ensure_directories()
    
    # Clean up old files before syncing
    clean_success, cleaned_files = clean_knowledge_base()
    if not clean_success:
        logger.warning("Failed to clean knowledge base directory, but continuing with sync")
    
    # Fetch agent scope from API
    agent_data = fetch_agent_scope(token, agent_id)
    
    if not agent_data:
        return {
            "status": "error",
            "message": "Failed to fetch agent data from TryUnleashX API"
        }
        
    # Extract knowledge sources
    knowledge_files = agent_data.get("knowledge_files", [])
    knowledge_links = agent_data.get("knowledge_links", [])
    knowledge_pages = agent_data.get("knowledge_pages", [])
    
    start_time = time.time()
    all_processed_files = []
    processed_counts = {
        "files": 0,
        "links": 0,
        "pages": 0,
        "errors": 0
    }
    
    # Process knowledge files
    logger.info(f"Processing {len(knowledge_files)} knowledge files")
    file_paths = process_knowledge_files(knowledge_files, token)
    all_processed_files.extend(file_paths)
    processed_counts["files"] = len(file_paths)
    
    # Process knowledge links
    logger.info(f"Processing {len(knowledge_links)} knowledge links")
    link_paths = process_knowledge_links(knowledge_links)
    all_processed_files.extend(link_paths)
    processed_counts["links"] = len(link_paths)
    
    # Process knowledge pages
    logger.info(f"Processing {len(knowledge_pages)} knowledge pages")
    page_paths = process_knowledge_pages(knowledge_pages)
    all_processed_files.extend(page_paths)
    processed_counts["pages"] = len(page_paths)
    
    # Calculate errors
    processed_counts["errors"] = (
        len(knowledge_files) - processed_counts["files"] +
        len(knowledge_links) - processed_counts["links"] +
        len(knowledge_pages) - processed_counts["pages"]
    )
    
    # Calculate total processing time
    processing_time = time.time() - start_time
    
    logger.info(f"Processed a total of {len(all_processed_files)} knowledge files in {processing_time:.2f} seconds")
    
    # Return summary
    return {
        "status": "success",
        "message": f"Successfully synced knowledge base for agent ID: {agent_id}",
        "agent_name": agent_data.get("agent_name", "Unknown"),
        "processed_files": len(all_processed_files),
        "files": all_processed_files,
        "cleaned_files": cleaned_files,
        "processing_time_seconds": round(processing_time, 2),
        "counts": processed_counts
    }
