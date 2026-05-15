import requests
from bs4 import BeautifulSoup

def test_hespress():
    url = "https://www.hespress.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Common selector for Hespress
        articles = soup.select('.card-title')
        print(f"Hespress found: {len(articles)} articles")
        for a in articles[:5]:
            print(f"- {a.get_text().strip()}")
    except Exception as e:
        print(f"Hespress error: {e}")

def test_akhbarona():
    url = "https://www.akhbarona.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Common selector for Akhbarona
        articles = soup.select('.title a')
        if not articles:
            articles = soup.select('h2 a')
        print(f"Akhbarona found: {len(articles)} articles")
        for a in articles[:5]:
            print(f"- {a.get_text().strip()}")
    except Exception as e:
        print(f"Akhbarona error: {e}")

if __name__ == "__main__":
    test_hespress()
    test_akhbarona()
