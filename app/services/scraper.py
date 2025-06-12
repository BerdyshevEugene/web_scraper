from app.parsers.piter import extract_titles, extract_author, extract_price, extract_details, extract_book_links
from .fetcher import fetch_html, httpx_fetch_html


async def scrape_url(url: str):
    html = await fetch_html(url)
    titles = extract_titles(html)
    author = extract_author(html)
    price = extract_price(html)
    details = extract_details(html)
    return(
        {'url': url,
         'titles': titles,
         'author': author,
         'price': price,
         'details': details}
    )


async def scrape_book_links(url: str):
    html = await httpx_fetch_html(url)
    book_links = await extract_book_links(html)
    return book_links
