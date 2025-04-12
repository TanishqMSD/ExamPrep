import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from urllib.parse import urlparse
from typing import Dict, List, Optional

class ContentScraper:
    SUPPORTED_DOMAINS = [
        'geeksforgeeks.org',
        'javatpoint.com',
        'tutorialspoint.com'
    ]

    @classmethod
    def is_supported_domain(cls, url: str) -> bool:
        domain = urlparse(url).netloc.lower()
        return any(supported in domain for supported in cls.SUPPORTED_DOMAINS)

    @staticmethod
    def scrape_webpage(url: str) -> Dict[str, str]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract main content based on common article containers
            main_content = soup.find('article') or soup.find(class_=['article', 'post-content', 'entry-content'])
            if not main_content:
                main_content = soup.find('main') or soup.find('div', class_=['content', 'main-content'])
            
            title = soup.title.string if soup.title else ''
            content = main_content.get_text(separator='\n', strip=True) if main_content else soup.get_text()
            
            return {
                'title': title if title else '',
                'content': content,
                'source_type': 'webpage'
            }
        except Exception as e:
            raise ValueError(f"Failed to scrape webpage: {str(e)}")

    @staticmethod
    def extract_pdf_content(pdf_file) -> Dict[str, str]:
        try:
            text = extract_text(pdf_file)
            # Extract title from first line or filename
            title = pdf_file.name.rsplit('.', 1)[0] if hasattr(pdf_file, 'name') else 'Uploaded PDF'
            
            return {
                'title': title,
                'content': text,
                'source_type': 'pdf'
            }
        except Exception as e:
            raise ValueError(f"Failed to extract PDF content: {str(e)}")

    @staticmethod
    def clean_content(content: str) -> str:
        # Remove excessive whitespace and normalize line breaks
        cleaned = ' '.join(content.split())
        # Remove any remaining special characters or unwanted symbols
        cleaned = ''.join(char for char in cleaned if char.isprintable())
        return cleaned

    @classmethod
    def process_content(cls, source, is_pdf: bool = False) -> Dict[str, str]:
        if is_pdf:
            raw_content = cls.extract_pdf_content(source)
        else:
            if not cls.is_supported_domain(source):
                raise ValueError(f"Unsupported domain. Please use one of: {', '.join(cls.SUPPORTED_DOMAINS)}")
            raw_content = cls.scrape_webpage(source)
        
        raw_content['content'] = cls.clean_content(raw_content['content'])
        return raw_content