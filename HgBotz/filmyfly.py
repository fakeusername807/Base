import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5'
}

def get_soup(url, max_redirects=5):
    """Fetch URL with redirect handling and return BeautifulSoup object"""
    current_url = url
    for _ in range(max_redirects):
        try:
            response = requests.get(
                current_url, 
                headers=HEADERS,
                allow_redirects=False,
                timeout=15
            )
            if 300 <= response.status_code < 400:
                current_url = response.headers['Location']
                continue
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser'), current_url
        except Exception as e:
            return None, None
    return None, None

def extract_linkmake_url(movie_url):
    """Extract LinkMake gateway URL from FilmyFly movie page"""
    soup, final_url = get_soup(movie_url)
    if not soup:
        return None
    
    # Find download button container
    dlbtn_div = soup.find('div', class_='dlbtn')
    if dlbtn_div:
        dl_link = dlbtn_div.find('a', class_='dl')
        if dl_link and dl_link.get('href'):
            return urljoin(final_url, dl_link['href'])
    
    # Alternative search if primary method fails
    for a_tag in soup.find_all('a', class_='dl'):
        if a_tag.get('href') and 'linkmake' in a_tag['href']:
            return urljoin(final_url, a_tag['href'])
    
    return None

def extract_cloud_urls(linkmake_url):
    """Extract quality-specific cloud URLs from LinkMake page"""
    soup, final_url = get_soup(linkmake_url)
    if not soup:
        return []
    
    cloud_urls = []
    for div in soup.find_all('div', class_='dlink'):
        if 'dl' in div.get('class', []):
            link = div.find('a', href=True)
            if link and link['href'].startswith('http'):
                # Clean URL parameters
                clean_url = urlparse(link['href'])._replace(query=None).geturl()
                cloud_urls.append(clean_url)
    
    return cloud_urls

def extract_final_urls(cloud_url):
    """Extract final download URLs from cloud storage page"""
    soup, final_url = get_soup(cloud_url)
    if not soup:
        return []
    
    # Find download options container
    container = soup.find('div', class_='container')
    if not container:
        return []

    # Extract all valid download links
    final_urls = []
    for a_tag in container.find_all('a', href=True):
        href = a_tag['href'].strip()
        if href.startswith(('http://', 'https://')):
            # Decode obfuscated URLs
            if 'Xzk5X0' in href or 'aHR0c' in href:
                try:
                    href = requests.utils.unquote(href)
                except:
                    pass
            final_urls.append(urljoin(final_url, href))
    
    return final_urls

# ----------------------------
# /b Command Implementation
# ----------------------------
def process_filmyfly_url(movie_url):
    """Complete link extraction pipeline for /b command"""
    # Step 1: Get LinkMake gateway URL
    linkmake_url = extract_linkmake_url(movie_url)
    if not linkmake_url:
        return "❌ Failed to extract gateway URL"
    
    # Step 2: Get quality-specific cloud URLs
    cloud_urls = extract_cloud_urls(linkmake_url)
    if not cloud_urls:
        return "❌ No quality links found"
    
    # Step 3: Get all download mirrors
    results = {}
    for url in cloud_urls:
        quality = url.split('/')[-1]  # Last part of URL as quality ID
        mirrors = extract_final_urls(url)
        if mirrors:
            results[quality] = mirrors
    
    if not results:
        return "❌ No download links found"
    
    # Format results
    output = []
    for quality, urls in results.items():
        output.append(f"🔹 {quality.upper()} QUALITY:")
        output.extend([f"     • {url}" for url in urls])
    
    return "\n".join(output)

# For Telegram bot (pseudo-code)
@Client.on_message(filters.command("b") & filters.private)
async def handle_b_command(message):
    movie_url = message.text.split()[1]
    result = process_filmyfly_url(movie_url)
    bot.reply_to(message, result)
