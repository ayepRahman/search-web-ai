"""
A search agent module that integrates with Ollama for AI-powered web search and content processing.

This module provides functionality to:
- Perform intelligent web searches based on user queries
- Scrape and validate web content
- Generate contextual responses using an AI model
- Handle logging with color formatting

Key components:
- ColoredFormatter: Custom logging formatter with color output
- Web search functions: query_generator(), search_duckduckgo(), scrape_page()
- AI processing: check_search_or_not(), best_search_results(), contain_data_needed()
- Interactive chat loop in main()

Dependencies:
- ollama: AI model integration
- requests: HTTP requests
- trafilatura: Web scraping
- beautifulsoup4: HTML parsing
- colorama: Terminal colors
"""

import logging
from typing import Dict, List, Optional

import ollama
import requests
import trafilatura
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

import sys_msgs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add color formatting to logging
class ColoredFormatter(logging.Formatter):
    """Custom logging formatter that adds color to log messages based on level."""
    
    format_str = '%(levelname)s: %(message)s'
    
    FORMATS = {
        logging.DEBUG: Fore.BLUE + format_str + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + format_str + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + format_str + Style.RESET_ALL
    }

    def format(self, record):
        """Format the log record with appropriate color based on log level."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.handlers = [handler]

init(autoreset=True)

assistant_convo = [
    sys_msgs.assistant_agent,  
]

def check_search_or_not() -> bool:
    """
    Determine if a search should be performed based on the last conversation message.
    
    Returns:
        bool: True if search should be performed, False otherwise
    """
    sys_msg = sys_msgs.should_search_decision_agent
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[sys_msg, {'role': 'user', 'content': assistant_convo[-1]['content']}]
        )
        content = response['message']['content']
        logger.info(f'Search decision: {content}')
        return 'true' in content.lower()
    except Exception as e:
        logger.error(f'Error in search decision: {e}')
        return False

def query_generator() -> str:
    """
    Generate a search query based on the last conversation message.
    
    Returns:
        str: Generated search query
    """
    sys_msg = sys_msgs.search_query_generator_agent
    query = f'CREATE A SEARCH QUERY FOR THE FOLLOWING QUESTION: \n{assistant_convo[-1]["content"]}'
    
# site://nextjs.org/latest

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[sys_msg, {'role': 'user', 'content': query}]
        )
        content = response['message']['content']
        print(f'CONTENT: {content}')
        return content
    except Exception as e:
        logger.error(f'Error generating query: {e}')
        return assistant_convo[-1]["content"]

def search_duckduckgo(search_query: str) -> List[Dict]:
    """
    Search DuckDuckGo with the given query and return results.
    
    Args:
        search_query (str): Query string to search for
        
    Returns:
        List[Dict]: List of search results, each containing id, link and description
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    try:
        url = f'https://duckduckgo.com/html/?q={search_query}'
        print(f'URL: {url}')
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for i, result in enumerate(soup.find_all('div', class_='result'), start=0):
            if i >= 10:
                break

            title_tag = result.find('a', class_='result__a')
            if not title_tag:
                continue
            
            link = title_tag['href']
            snippet_tag = result.find('a', class_='result__snippet')
            snippet = snippet_tag.text.strip() if snippet_tag else 'No description available'

            results.append({
                'id': i,
                'link': link,
                'search_description': snippet
            })

        logger.info(f'Found {len(results)} search results')
        return results
    except Exception as e:
        logger.error(f'Error in DuckDuckGo search: {e}')
        return []

def best_search_results(s_results: List[Dict], query: str) -> int:
    """
    Select the best search result from the list based on relevance.
    
    Args:
        s_results (List[Dict]): List of search results
        query (str): Original search query
        
    Returns:
        int: Index of the best search result
    """
    if not s_results:
        return 0
        
    sys_msg = sys_msgs.best_search_result_selector_agent
    best_msg = f'SEARCH_RESULTS: {s_results} \nUSER_PROMPT: {assistant_convo[-1]["content"]} \nSEARCH_QUERY: {query}'

    for attempt in range(3):
        try:
            response = ollama.chat(
                model="llama3.2",
                messages=[sys_msg, {'role': 'user', 'content': best_msg}]
            )
            index = int(response['message']['content'])
            return min(index, len(s_results) - 1)  # Ensure index is within bounds
        except Exception as e:
            logger.error(f'Error selecting best result (attempt {attempt + 1}): {e}')
    return 0

def scrape_page(page_link: str) -> Optional[str]:
    """
    Scrape content from the given webpage.
    
    Args:
        page_link (str): URL of the page to scrape
        
    Returns:
        Optional[str]: Scraped content if successful, None otherwise
    """
    try:
        downloaded = trafilatura.fetch_url(page_link)
        if not downloaded:
            return None
        result = trafilatura.extract(downloaded, include_formatting=True)
        return result
    except Exception as e:
        logger.error(f'Failed to scrape page {page_link}: {e}')
        return None

def ai_search() -> Optional[str]:
    """
    Perform an AI-powered web search based on the conversation context.
    
    Returns:
        Optional[str]: Relevant content if found, None otherwise
    """
    try:
        logger.info('Starting search process')
        search_query = query_generator().replace('"', '')

        print(f'SEARCH_QUERY: {search_query}')
        
        search_results = search_duckduckgo(search_query)
        if not search_results:
            logger.warning('No search results found')
            return None

        max_attempts = 5
        for attempt in range(max_attempts):
            best_result_index = best_search_results(s_results=search_results, query=search_query)
            
            if best_result_index >= len(search_results):
                logger.warning(f'Invalid result index: {best_result_index}')
                continue
                
            page_link = search_results[best_result_index]['link']
            page_text = scrape_page(page_link)

            
            if page_text and contain_data_needed(search_content=page_text, query=search_query):
                logger.info('Found relevant content')
                return page_text
                
            search_results.pop(best_result_index)
            
        logger.warning(f'Could not find relevant content after {max_attempts} attempts')
        return None
        
    except Exception as e:
        logger.error(f'Error in search process: {e}')
        return None

def contain_data_needed(search_content: str, query: str) -> bool:
    """
    Check if the scraped content contains the information needed.
    
    Args:
        search_content (str): Scraped webpage content
        query (str): Original search query
        
    Returns:
        bool: True if content is relevant, False otherwise
    """
    sys_msg = sys_msgs.page_content_validator_agent
    page_content_msg = f'PAGE_TEXT: {search_content} \nUSER_PROMPT: {assistant_convo[-1]["content"]} \nSEARCH_QUERY: {query}'

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[sys_msg, {'role': 'user', 'content': page_content_msg}]
        )
        return 'true' in response['message']['content'].lower()
    except Exception as e:
        logger.error(f'Error validating content: {e}')
        return False

def stream_assistant_response() -> None:
    """
    Stream the AI assistant's response to the console and update conversation history.
    """
    global assistant_convo
    try:
        response_stream = ollama.chat(model="llama3.2", messages=assistant_convo, stream=True)
        complete_response = ""
        print(f"{Fore.GREEN}Assistant:{Style.RESET_ALL}")

        for chunk in response_stream:
            chunk_content = chunk['message']['content']
            print(chunk_content, end="", flush=True)
            complete_response += chunk_content

        assistant_convo.append({'role': 'assistant', 'content': complete_response})
        print('\n\n')
    except Exception as e:
        logger.error(f'Error streaming response: {e}')
        print(f"{Fore.RED}Error: Could not generate response{Style.RESET_ALL}\n")

def main() -> None:
    """
    Main function that runs the interactive chat loop with AI-powered search capabilities.
    """
    global assistant_convo
    logger.info('Starting chat application')

    while True:
        try:
            prompt = input(f'{Fore.YELLOW}You: \n{Style.RESET_ALL}')
            if not prompt.strip():
                continue
                
            assistant_convo.append({'role': 'user', 'content': prompt})

            if check_search_or_not():
                context = ai_search()
                assistant_convo.pop()  # Remove the original prompt

                if context:
                    prompt = f'SEARCH_RESULT: {context} \nUSER_PROMPT: {prompt}'
                else:
                    prompt = sys_msgs.SEARCH_FAILURE_PROMPT_TEMPLATE.format(prompt=prompt)
                    
                assistant_convo.append({'role': 'user', 'content': prompt})

            stream_assistant_response()
            
        except KeyboardInterrupt:
            logger.info('Shutting down chat application')
            break
        except Exception as e:
            logger.error(f'Error in main loop: {e}')
            print(f"{Fore.RED}An error occurred. Please try again.{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()