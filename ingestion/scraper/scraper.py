import requests
from bs4 import BeautifulSoup
import json
import datetime
import random

class NewsScraper:
    def __init__(self):
        self.sources = {
            "Hespress": "https://www.hespress.com",
            "Akhbarona": "https://www.akhbarona.com"
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_hespress(self):
        """Scrape real news titles and links from Hespress"""
        articles = []
        try:
            response = requests.get(self.sources["Hespress"], headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Hespress structure: articles are in div.card
                cards = soup.select('.card')[:20] # Get top 20
                for card in cards:
                    title_elem = card.select_one('.card-title')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text().strip()
                    link_elem = card.select_one('a')
                    link = link_elem['href'] if link_elem else self.sources["Hespress"]
                    
                    # Category extraction if possible
                    cat_elem = card.select_one('.card-category')
                    category = cat_elem.get_text().strip() if cat_elem else "Général"
                    
                    articles.append({
                        "source": "Hespress",
                        "title": title,
                        "content": f"Article récent sur Hespress : {title}. Consultez le lien pour l'intégralité.",
                        "url": link,
                        "category": category,
                        "published_date": datetime.datetime.now().isoformat()
                    })
            else:
                print(f"Error Hespress: {response.status_code}")
        except Exception as e:
            print(f"Scraping error Hespress: {e}")
            
        return articles

    def scrape_akhbarona(self):
        """Scrape real news from Akhbarona"""
        articles = []
        try:
            # Using the last news page for better results
            url = f"{self.sources['Akhbarona']}/last"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Akhbarona structure: often has articles in a list with titles in h2 or specific classes
                items = soup.select('.article_last, .title')[:15]
                for item in items:
                    link_elem = item.select_one('a')
                    if not link_elem:
                        continue
                        
                    title = link_elem.get_text().strip()
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = self.sources["Akhbarona"] + link
                        
                    articles.append({
                        "source": "Akhbarona",
                        "title": title,
                        "content": f"Actualité Akhbarona : {title}. Détails disponibles via le lien.",
                        "url": link,
                        "category": "Maroc",
                        "published_date": datetime.datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"Scraping error Akhbarona: {e}")
            
        return articles

    def get_all_news(self):
        all_news = self.scrape_hespress() + self.scrape_akhbarona()
        
        # Security fallback if both failed
        if not all_news:
            all_news.append({
                "source": "System",
                "title": "Maintenance en cours ou erreur de connexion",
                "content": "Le scraper n'a pas pu récupérer de données en direct.",
                "url": "http://internal.system",
                "category": "System",
                "published_date": datetime.datetime.now().isoformat()
            })
            
        return all_news

if __name__ == "__main__":
    scraper = NewsScraper()
    results = scraper.get_all_news()
    print(f"Scraped total: {len(results)} articles")
    print(json.dumps(results[:2], indent=2, ensure_ascii=False))
