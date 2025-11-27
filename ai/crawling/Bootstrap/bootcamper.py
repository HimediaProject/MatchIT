from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 병렬화
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Dict, Any, List, Set, Tuple, Union
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import lxml
import pandas as pd
import random
import requests
import os
import time
import logging
import re
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class Crawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    @staticmethod
    def create_driver(headless: bool = True):
        # 래퍼: Crawler.set_selenium이 드라이버를 반환하지 않더라도 Crawler.driver에서 꺼냄
        try:
            driver = Crawler.set_selenium(headless=False)
            if driver is None:
                driver = getattr(Crawler, "driver", None)

            if driver is None:
                logging.error('[DRIVER] Crawler.set_selenium() 또는 Crawler.driver에서 드라이버를 얻지 못함')
                return None

            logging.info('[DRIVER] 드라이버 생성 완료')
            return driver
        
        except Exception as e:
            logging.error(f'[DRIVER] 드라이버 생성 중 예외 발생: {e}')

    
    def set_selenium(self, headless: bool = True):
        try:
            opts = Options()
            if headless:
                opts.add_argument("--headless=new")
                opts.add_argument("--no-sandbox")
                opts.add_argument("--disable-gpu")
                opts.add_argument("--window-size=1920,1080")
                opts.add_argument("--start-maximized")
                opts.add_argument("--disable-dev-shm-usage")
                opts.add_argument("--lang=ko-KR")
                opts.add_argument("--log-level=3")
                opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

            # 드라이버 서비스 설정
            service = Service(ChromeDriverManager().install())

            # 드라이버 생성
            driver = webdriver.Chrome(service = service, options = opts)
            logging.info("[DRIVER] Selenium 드라이버 생성 완료")
            return driver
        
        except Exception as e:
            logging.error(f'[DRIVER] Seleinum 드라이버 생성 실패: {e}')
            return None
        
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            logging.info("[DRIVER] 드라이버 종료 완료")

    
    def scroll_and_get_links(self, pattern: str):
        '''
        React 무한 scrolling 구현 페이지에 적용
        1. 전체 a tag 수집
        2. a.href에 '/end point/'가 포함 된 공고 링크만
            - pattern에 endpoint 기재
        3. 공고 URL만 추출
            - Set: {}로 중복제거
            - [...]로 배열(list)화
        '''
        last_count = 0
        retry = 0
        
        while retry < 3:
            # 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 링크 수집
            links = self.driver.execute_script("""
                const target = arguments[0];    // target: python의 pattern
                const allLinks = Array.from(document.querySelectorAll('a'));
                return [...new Set(allLinks
                    .filter(a => a.href.includes(target))
                    .map(a => a.href))];
            """, pattern)
            
            logging.info(f"[INFO] 현재 링크 개수: {len(links)}개")
            
            if len(links) == last_count:
                retry += 1
            else:
                retry = 0
                last_count = len(links)
        
        return links
    
    def save_intermediate(self,
                          data: Union[List, Dict],
                          name: str = "results_partial"):
        df = pd.DataFrame(data)
        df.to_csv(f"{name}.csv", index=False, encoding="utf-8-sig")
        with open(f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"[SAVE] 중간 저장 완료: {name}.csv / {name}.json")

    def save_final_data(self,
                        data: List[Dict],
                        filename: str = "results.json"):
        
        # def deduplicate(records: List[Dict]) -> List[Dict]:
        #     seen = set()
        #     unique = []
        #     for rec in records:
        #         isbn = rec.get("isbn", "").strip()
        #         if not isbn or isbn in seen:
        #             continue
        #         seen.add(isbn)
        #         unique.append(rec)
        #     return unique

        # clean_data = deduplicate(book_data)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"[SAVE] 저장 {len(data)} unique records to {filename}")


###################################################################################
# Crawling site 별 수정 필요
# data parsing용
###################################################################################
    def extract_job_detail(self, url):
        """공고 상세 정보 추출"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            data = {'url': url}
            
            # JavaScript로 데이터 추출
            job_data = self.driver.execute_script("""
                const result = {};
                
                // 제목
                const title = document.querySelector('h1');
                result.title = title ? title.textContent.trim() : null;
                
                // 모든 div 찾아서 라벨-값 매칭
                const allDivs = Array.from(document.querySelectorAll('div'));
                
                ['연봉', '근무지', '경력', '학력', '마감일'].forEach(label => {
                    const labelDiv = allDivs.find(d => d.textContent.trim() === label);
                    if (labelDiv && labelDiv.nextElementSibling) {
                        result[label] = labelDiv.nextElementSibling.textContent.trim();
                    }
                });
                
                // 섹션 제목으로 내용 찾기
                ['회사소개', '주요업무', '자격 요건', '우대사항', '채용절차', '기타안내'].forEach(section => {
                    const heading = Array.from(document.querySelectorAll('h2, h3, strong')).find(h => h.textContent.includes(section));
                    if (heading) {
                        const content = heading.closest('section') || heading.parentElement;
                        result[section] = content ? content.textContent.trim() : null;
                    }
                });
                
                // 섹션 제목으로 stack tags 찾기 
                const f_stack = '이 포지션에 필요한 전문분야/기술';
                
                // 해당 클래스 span 모두 선택
                const stackSpans = document.querySelectorAll('span.sc-9ab07b31-1, span.hLGjbI');

                if (stackSpans.length > 0) {
                    result[f_stack] = Array.from(stackSpans).map((el, idx) => ({
                        index: idx + 1,
                        text: el.textContent.trim()
                    }));
                }

                // 기업 상세 링크
                const companyLink = Array.from(document.querySelectorAll('a')).find(a => a.href.includes('/company/'));
                result.companyUrl = companyLink ? companyLink.href : null;
                
                return result;
            """)
            
            data.update(job_data)
            
            # 기업 상세 정보
            if data.get('companyUrl'):
                company_data = self.extract_company_detail(data['companyUrl'])
                data.update(company_data)
            
            return data
            
        except Exception as e:
            logging.error(f"오류 ({url}): {e}")
            return {'url': url, 'error': str(e)}
    
    def extract_company_detail(self, company_url):
        """기업 상세 정보 추출"""
        try:
            self.driver.get(company_url)
            time.sleep(2)
            
            company_data = self.driver.execute_script("""
                const result = {};
                const allDivs = Array.from(document.querySelectorAll('div'));
                
                ['대표자', '설립일', '업종', '기업유형', '위치'].forEach(label => {
                    const labelDiv = allDivs.find(d => d.textContent.trim() === label);
                    if (labelDiv && labelDiv.nextElementSibling) {
                        result[label] = labelDiv.nextElementSibling.textContent.trim();
                    }
                });
                
                // 홈페이지
                const homepage = Array.from(document.querySelectorAll('a')).find(a => a.href.includes('http') && !a.href.includes('rememberapp'));
                result['홈페이지'] = homepage ? homepage.href : null;
                
                // 평균 연봉
                const salary = document.querySelector('b');
                result['평균연봉'] = salary ? salary.textContent.trim() : null;
                
                return result;
            """)
            
            return company_data
            
        except Exception as e:
            logging.error(f"[ERROR] 기업 정보 오류: {e}")
            return {}
    
    def crawl_all(self,
                  url: str,
                  pattern: str = "/job/posting/") -> pd.DataFrame:
        '''
        전체 크롤링
        '''
        try:
            self.driver.get(url)
            job_links = self.scroll_and_get_links(pattern)
            logging.info(f"[INFO] 총 {len(job_links)}개 공고 발견")

            all_data = []
            for i, link in enumerate(job_links, 1):
                logging.info(f"[INFO] [{i}/{len(job_links)}] {link}")
                data = self.extract_job_detail(link)
                all_data.append(data)

                if i % 100 == 0:
                    self.save_intermediate(all_data,
                                           name = f"results_batch_{i//100}")

                time.sleep(2)

            return pd.DataFrame(all_data)

        finally:
            self.close_driver()


###################################################################################
# BeautifulSoup, requests
# 간단하고 가벼운 DOM parsing
###################################################################################
def parse_page(driver, url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    data = {
        "url": url,
        "title": soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else None,
        "images": [img["src"] for img in soup.select("img") if img.get("src")]
    }
    return data

def download_image(url, folder: str = "images"):
    try:
        os.makedirs(folder, exist_ok = True)
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            fname = os.path.join(folder, os.path.basename(url))
            with open(fname, "wb") as f:
                f.write(resp.content)
            logging.info(f"[IMG] 저장 완료: {fname}")
    except Exception as e:
        logging.error(f"[IMG] 다운로드 실패 {url}: {e}")


###################################################################################
# ProcessPoolExecutor, ThreadPoolExecutor
# 병렬처리
###################################################################################
def chunkify(lst, size):
    '''
    리스트를 size 단위로 잘라서 반환
    '''
    for i in range(0, len(lst), size):
        yield lst[i: i + size]

def parse_links(links_chunk):
    '''
    링크 청크 단위로 상세 페이지 파싱
    '''
    results = []
    crawler = Crawler(headless = True)
    driver = crawler.driver
    for link in links_chunk:
        try:
            driver.get(link)
            soup = BeautifulSoup(driver.page_source, "lxml")
            data = {
                "url": link,
                "title": soup.select_one("h1").get_text(strip = True) if soup.select_one("h1") else None
            }
            results.append(data)
            logging.info(f"[PARSE] {link} 처리 완료")
        except Exception as e:
            logging.error(f"[ERROR] {link} 처리 실패: {e}")
    crawler.close_driver()
    return results

def crawl_site(pattern, name = "result"):
    '''
    BeautifulSoup
    한가지 사이트의 상세 내용까지 전체 수집
    '''
    crawler = Crawler(headless=True)
    driver = crawler.driver
    links = crawler.scroll_and_get_links(pattern)
    crawler.close_driver()

    # 링크를 10개씩 청크로 나눔
    chunks = list(chunkify(links, 10))

    # 청크 단위 병렬 처리
    all_results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = list(executor.map(parse_links, chunks))
        for res in futures:
            all_results.extend(res)

    # 저장
    with open(f"{name}_parsed.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    return all_results

def parse_link(link):
    '''
    BeautifulSoup
    link를 가져와, 
    '''
    crawler = Crawler(headless=True)
    driver = crawler.driver
    try:
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, "lxml")
        data = {
            "url": link,
            "title": soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else None,
            "images": [img["src"] for img in soup.select("img") if img.get("src")]
        }
        return data
    except Exception as e:
        logging.error(f"[ERROR] {link} 처리 실패: {e}")
        return None
    finally:
        crawler.close_driver()

def crawl_and_parse(pattern, name = "result"):
    crawler = Crawler(headless = True)
    links = crawler.scroll_and_get_links(pattern)
    crawler.close_driver()

    logging.info(f"[INFO] 총 {len(links)}개 링크 발견")

    results = []
    # 링크 병렬 처리
    with ThreadPoolExecutor(max_workers = 10) as executor:
        futures = list(executor.map(parse_link, links))
        results = [res for res in futures if res]

    # 저장
    with open(f"{name}_parsed.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


def main(mode = "site"):
    if mode == "site":
        patterns = ["/job/posting/", "/product/", "/news/"]
        with ProcessPoolExecutor(max_workers = 4) as executor:
            results = list(executor.map(crawl_site, patterns))

        merged = []
        for r in results:
            merged.extend(r)

        crawler = Crawler(headless = True)
        crawler.save_final_data(merged, filename = "results.json")
        crawler.close_driver()

    elif mode == "url":
        crawler = Crawler(headless = False)
        url = 'https://career.rememberapp.co.kr/job/postings?search=%7B%22jobCategoryNames%22%3A%5B%7B%22level1%22%3A%22SW%EA%B0%9C%EB%B0%9C%22%7D%2C%7B%22level1%22%3A%22AI%C2%B7%EB%8D%B0%EC%9D%B4%ED%84%B0%22%7D%5D%7D'
        df = crawler.crawl_all(url)
        if df is not None:
            crawler.save_final_data(df.to_dict(orient = "records"), filename = "results.json")

if __name__ == "__main__":
    # 원하는 모드 선택
    # mode = 'site': 각 사이트별 함수를 이용해, 상세 데이터까지 가져옴
    # mode = 'url': 병렬 처리로 빠르게 link만 가져옴
    main(mode = 'site')   # 또는 main(mode = 'url')