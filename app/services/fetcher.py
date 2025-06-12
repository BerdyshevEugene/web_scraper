import httpx
from curl_cffi.requests import AsyncSession


async def httpx_fetch_html(url: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_html(url: str):
    async with AsyncSession() as session:
        response = await session.get(url, impersonate='chrome110', timeout=10)
        response.raise_for_status()
        return response.text
