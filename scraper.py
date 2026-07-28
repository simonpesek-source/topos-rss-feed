import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Seznam všech rubrik, které chceme spojit
urls = [
    'https://toposmagazine.com/cities/',
    'https://toposmagazine.com/mobility/',
    'https://toposmagazine.com/projects/',
    'https://toposmagazine.com/sustainability/',
    'https://toposmagazine.com/digitisation/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

seen_links = set()
rss_items = ""
total_count = 0

session = requests.Session()

for url in urls:
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hledáme všechny karty článků na stránce podle poslaného HTML
        articles = soup.find_all('div', class_='tcl-list-articles__item-post')
        
        for article in articles:
            # Získání nadpisu
            heading_tag = article.find('h3', class_='tcl-list-articles__item-heading')
            if not heading_tag:
                continue
            title = heading_tag.get_text(strip=True)
            
            # Získání odkazu
            link_tag = article.find('a', href=True)
            if not link_tag:
                continue
            link = link_tag['href']
            
            # Získání nálepky rubriky (Cities, Mobility, ...)
            cat_tag = article.find('a', class_='tcl-list-articles__item-category')
            category = cat_tag.get_text(strip=True) if cat_tag else ""
            
            # Ochrana proti duplicitám (kdyby byl článek ve více rubrikách)
            if link and link not in seen_links:
                seen_links.add(link)
                total_count += 1
                
                clean_title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # Do nadpisu přidáme název rubriky v hranatých závorkách [Cities], [Mobility] atd.
                display_title = f"[{category}] {clean_title}" if category else clean_title
                
                rss_items += f"""
        <item>
            <title>{display_title}</title>
            <link>{link}</link>
            <guid>{link}</guid>
        </item>"""
                
    except Exception as e:
        print(f"Chyba při stahování {url}: {e}")

# Sestavení jednoho společného XML
rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Topos Magazine (Combined)</title>
  <link>https://toposmagazine.com/</link>
  <description>Sloučený feed z rubrik Cities, Mobility, Projects, Sustainability a Digitisation</description>
  <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
  {rss_items}
</channel>
</rss>"""

with open('feed.xml', 'w', encoding='utf-8') as f:
    f.write(rss_feed)

print(f"Úspěšně vygenerováno {total_count} článků ze všech rubrik.")
