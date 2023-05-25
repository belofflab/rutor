from fastapi import FastAPI
from pydantic import BaseModel

from .utils.scraper import start_scrape_rutor

app = FastAPI()

class Scrape(BaseModel):
    url: str


@app.post('/scrape')
async def scrape(scrape: Scrape) -> dict:
    return await start_scrape_rutor(url=scrape.url)
