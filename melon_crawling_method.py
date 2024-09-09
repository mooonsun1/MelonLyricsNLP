from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import os
import random


user_agent = 'User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'


song_name = "#downloadfrm > div > div > div.entry > div.info > div.song_name"
song_singer = "#downloadfrm > div > div > div.entry > div.info > div.artist > a > span:nth-child(1)"
lyrics_selector = "#d_video_summary" 




async def get_song_info(urls , session):
     async with session.get(urls) as res:
        #  res = requests.get(urls , headers={"user-agent":user_agent})
         if res.status == 200 : 
            html = await res.text() 
            soup = BeautifulSoup(html, "lxml") 

            name = soup.select(song_name)
            singer = soup.select(song_singer)
            lyrics = soup.select(lyrics_selector)
            song_info = []
            for a,b,c in zip(name , singer , lyrics):
                a = a.text.replace('\t','').replace('\n','').replace('곡명','')
                b = b.get_text().strip()
                c = c.get_text(separator=' ', strip=True)
                song_info.extend((a,b,c))
                # time.sleep( random.uniform(1,3) )

            return song_info
         else:
            raise Exception(f"요청 실패. 응답코드: {res.status}")



async def main(links):
    async with aiohttp.ClientSession(headers={"user-agent":user_agent}) as session: 
        result = await asyncio.gather(*[get_song_info(urls, session) for urls in links])
    return result


if __name__ == "__main__":

    years = int(input("년도를 입력하세요: "))
    if years % 10 != 0:
        years = years - years%10
    e = time.time()
    # Selenium 설정
    driver = driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    song_id = []
    for year in range(years , years+10):
        if year not in [1960, 1961, 1962, 1963 , 2024 ,2025, 2026, 2027, 2028, 2029]:
            year = str(year)
            url = 'https://www.melon.com/chart/age/index.htm?chartType=YE&chartGenre=KPOP&chartDate=' + year
            driver.get(url)

        # 페이지 로드 대기
        time.sleep(2)

        # 페이지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.3);")

        # 추가적인 페이지 로딩 시간 대기
        time.sleep(5)

        # BeautifulSoup 객체 생성
        html = driver.page_source
        dom = BeautifulSoup(html, 'html.parser')

        # 데이터 수집
        elements = dom.select('td:nth-child(5) > div > button')    ##lst50 > td:nth-child(5) > div > button  - 각 시대별 50개씩 추출
        

        for element in elements:
            id = element.get('data-song-no')
            song_id.append("https://www.melon.com/song/detail.htm?songId="+id)
    
    print(song_id)
    # print(len(song_id))

    
    song_data = asyncio.run(main(song_id))
    print(song_data)
    s = time.time()
    print(f"걸린시간:{s-e}")

    os.makedirs("data",exist_ok=True)
    df = pd.DataFrame(song_data , columns = ["곡명","가수","가사"])
    file_path = f"data/{years}s.csv"
    df.to_csv(file_path , index=False)



