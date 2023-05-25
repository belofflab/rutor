import asyncio
from typing import Optional

from arsenic import get_session
from arsenic.browsers import Chrome
from arsenic.constants import SelectorType
from arsenic.errors import NoSuchElement
from arsenic.services import Chromedriver, Remote
from arsenic.session import Session
from bs4 import BeautifulSoup


async def parse_files(session: Session) -> Optional[str]:
    WATCH_TORRENT_FILES_FILELIST = 'tbody#filelist > tr > td'
    try:
        await session.execute_script("""if(filelist_already_loaded==0){filelist_already_loaded=1;$('#filelist').load('/descriptions/925948.files');}toggle_visibility('displayfiles');""")
        files = await session.get_element(
            selector=WATCH_TORRENT_FILES_FILELIST,
            selector_type=SelectorType.css_selector
        )
        files = await files.get_text()
    except NoSuchElement:   
        files = None
    return files 

async def parse_information(session: Session) -> dict:
    MOVIE_DETAILS_SELECTOR = 'table#details > tbody > tr > td > span'
    accessing_information = {
        'название': 'name', 
        'оригинальное название': 'init_name',
        'год выхода': 'release_dat',
        'жанр': 'genre',
        'режиссер': 'producer',
        'в ролях': 'cast',
        'о фильме:': 'about',
        'страна': 'country',
        'студия': 'studio',
        'формат': 'format',
        'качество': 'quality',
    }
    collected_data = {}
    page_source = await session.get_page_source()
    soup = BeautifulSoup(page_source, 'lxml')
    download_file = soup.select_one('div#download > a:nth-child(2)').attrs.get('href') if soup.select_one('div#download > a:nth-child(2)') is not None else '-'
    movie_details = soup.select_one(selector=MOVIE_DETAILS_SELECTOR)
    movie_data = movie_details.get_text().splitlines()
    for data in movie_data:
        splited_data = data.split(': ')
        try:
            collected_data[
                accessing_information[splited_data[0].lower()]
            ] = splited_data[-1]
        except KeyError:
            continue
        except IndexError:
            continue
    collected_data['description'] = movie_details.select_one('font').text if movie_details.select_one('font') is not None else '-'
    image = [image.attrs.get('src') for image in movie_details.select('img') if 'fastpic' in image.attrs.get('src')][0]
    print(image)
    collected_data['image'] = image
    collected_data['download_file'] = download_file
    return collected_data

async def scrape_rutor(session: Session, url: str) -> Optional[dict]:
    await session.get(url)
    # file = await parse_files(session)
    collected_data = await parse_information(session)
    # collected_data['file'] = file  if file is not None else ''
    return collected_data

async def start_scrape_rutor(url: str) -> dict:
    async with get_session(
        Remote(
            url='http://selenium:4444/wd/hub'
        ), Chrome()) as session:
        return await scrape_rutor(session, url=url)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(
            start_scrape_rutor(
                    url = """
http://rutor.info/torrent/894269/formula-1-sezon-2022-jetap-20-gran-pri-meksiki-gonka-30.10-2022-iptvrip-720r                    
"""
                )
            )
        )
