from fastapi import FastAPI, Query, HTTPException

from .services.scraper import scrape_url, scrape_book_links


app = FastAPI(title='Scraper API')


@app.get('/book_list')
async def book_list(url: str):
    try:
        book_links = await scrape_book_links(url)
        return book_links
    except Exception as e:
        raise HTTPException(status_code=400, details=str(e))



@app.get('/scrape')
async def scrape(url: str):
    try:
        result = await scrape_url(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/scrape_all_books')
async def scrape_all_books(url: str):
    try:
        book_links = await scrape_book_links(url)
        
        book_details = []
        for link in book_links:
            details = await scrape_url(link)
            if details:  # Добавляем только успешно распарсенные книги
                book_details.append(details)
        
        if not book_details:
            raise HTTPException(
                status_code=404,
                detail="Не удалось получить данные ни об одной книге. Возможно, изменилась структура сайта."
            )
            
        return book_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )