import asyncio
import re
import logging

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from app.services.fetcher import httpx_fetch_html


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


async def extract_book_links(html: str):
    current_url = html
    book_links = []
    page_number = 1

    logger.info(f"Starting book links extraction from: {current_url}")

    while current_url:
        logger.info(f"Processing page {page_number}: {current_url}")
        
        try:
            soup = BeautifulSoup(html, 'lxml')

            logger.debug(f"Successfully fetched and parsed HTML for page {page_number}")
            logger.debug(f"HTML size: {len(html)} bytes")

            try:
                link_tags = soup.find('div', class_='products-list').find_all('a')
                found_on_page = 0
                for link in link_tags:
                    href = link.get('href')
                    if href and href.startswith('/collection/all/product/'):
                        full_url = urljoin('https://www.piter.com/', href)
                        # if full_url not in book_links:
                        book_links.append(full_url)
                        found_on_page += 1

                logger.info(f"Links found on page {page_number}: {found_on_page} (Total: {len(book_links)})")
                if found_on_page == 0:
                    logger.warning("No books found on page. Ending extraction.")
                    break

            except AttributeError as e:
                logger.error(f"Failed to find products list: {e}")
                logger.debug(f"Page HTML: {html[:500]}...")
                break

            next_button = soup.find('a', string='Следующая')
            if next_button and next_button.get('href'):
                href = next_button['href']
                full_url = urljoin('https://www.piter.com/', href)
                match = re.search(r'page=(\d+)', href)
                if match:
                    page = int(match.group(1))
                    current_url = full_url
                    page_number = page
                    await asyncio.sleep(1)
                    response = await httpx_fetch_html(current_url)
                    html = response
                else:
                    logger.info("No valid page number in next link. Ending extraction.")
                    break
            else:
                logger.info("No next page button found. Ending extraction.")
                break

        except Exception as e:
            logger.error(f"Error during extraction on page {page_number}: {e}", exc_info=True)
            break

    logger.info(f"Finished extraction. Total book links found: {len(book_links)}")
    if book_links:
        logger.debug(f"First 5 links: {book_links[:5]}")
    return book_links



def extract_titles(html: str):
    soup = BeautifulSoup(html, 'lxml')
    # scrap_title = soup.find('div', _class='product-info').find('h1').get_text(strip=True)
    scrap_title = soup.select_one('div.product-info > h1').get_text(strip=True)
    # titles.append(scrap_title)
    # titles = [a.get('title').strip() for a in soup.select('h3 a')]
    return scrap_title


def extract_author(html: str):
    soup = BeautifulSoup(html, 'lxml')
    author_info = []
    scrap_author = soup.select_one('p.author a').get_text(strip=True)
    scrap_link = soup.select_one('p.author a')['href']
    author_info.extend([scrap_author, scrap_link])
    return author_info


def extract_price(html: str):
    soup = BeautifulSoup(html, 'lxml')
    price_info = []
    scrap_price = soup.select('div.price.color')
    price, electronic_price = [p.text.strip() for p in scrap_price[:2]]
    price_info.extend([f'{price}, {electronic_price}'])
    return price_info


def extract_details(html: str):
    soup = BeautifulSoup(html, 'lxml')
    author_info = []
    scrap_info = soup.select('ul.clear-list li.clearfix')
    scrap_info = {
        li.find('span', class_='grid-5').text.strip().rstrip(':'): li.find('span', class_='grid-7').text.strip()
        for li in scrap_info
    }
    author_info.extend([f'{scrap_info}'])
    return author_info

