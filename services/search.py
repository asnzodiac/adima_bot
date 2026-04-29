import os
import requests
import wikipedia

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def wikipedia_search(query):
    return wikipedia.summary(query, sentences=3)

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    data = requests.get(url).json()
    articles = data.get("articles", [])[:5]
    return "\n".join([f"- {a['title']}" for a in articles])

def web_search(query):
    url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_KEY}"
    data = requests.get(url).json()
    return data.get("organic_results", [{}])[0].get("snippet", "No results found.")
