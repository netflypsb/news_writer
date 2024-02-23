from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

class NewsSearchTools:

    @tool("Search and Scrape News Articles")
    def search_and_scrape_news(topic: str, api_key: str) -> dict:
        """
        Searches for news articles on a given topic and scrapes content if necessary.
        
        Parameters:
        - topic (str): The topic to search for.
        - api_key (str): The API key for SerpApi.

        Returns:
        - dict: A dictionary containing the news articles' titles, links, and snippets or scraped content.
        """
        try:
            params = {
                "engine": "google_news",
                "q": topic,
                "tbm": "nws",
                "api_key": api_key,  # Use the provided API key
                "hl": "en",
                "num": 5
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            news_results = results.get("news_results", [])
            
            output = {"articles": []}

            for news in news_results:
                article = {
                    "title": news.get('title'),
                    "link": news.get('link'),
                    "content": news.get('snippet') or NewsSearchTools.scrape_article_content(news.get('link'))
                }
                output["articles"].append(article)

            return output

        except Exception as e:
            return {"error": "Failed to search for news articles."}

    @staticmethod
    def scrape_article_content(url: str) -> str:
        """
        Scrapes the content of a news article.

        Parameters:
        - url (str): The URL of the article to scrape.

        Returns:
        - str: The scraped article content or an error message.
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            article_text = ' '.join(p.text for p in soup.find_all('p'))
            return article_text[:500] + '...'  # Return the first 500 characters for brevity
        except Exception as e:
            return "Failed to scrape the article content."
