from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Generator
from contextlib import contextmanager
import pandas as pd
import json
import time
import logging
import os
import re


class CrawlerConfig:
    """크롤러 설정 - 모든 설정 값을 한 곳에서 관리

    사용법:
        1. 여기서 원하는 설정 값 변경
        2. python crawler_moduler.py 실행

    예시:
        # Bootcamper 크롤링으로 변경하려면:
        DEFAULT_PARSER = 'bootcamper'

        # 브라우저 창 보이게 하려면:
        HEADLESS = False

        # 더 빠르게 크롤링하려면:
        MAX_WORKERS = 20
        PAGE_LOAD_WAIT = 1
    """

    # 기본 설정
    HEADLESS = True
    DEFAULT_PARSER = 'hrd_net'  # 'bootcamper', 'hrd_net', 'remember', 'saramin'

    # 시간 설정 (초)
    PAGE_LOAD_WAIT = 3
    SCROLL_WAIT = 2
    ELEMENT_WAIT = 2

    # 재시도 설정
    MAX_SCROLL_RETRY = 3

    # 페이징 설정
    MAX_PAGES = 2500  # HRD-net은 많은 페이지가 있으므로 크게 설정

    # 병렬 처리 설정
    MAX_WORKERS = 10  # 동시 처리 수 (높을수록 빠르지만 서버 부하 주의)
    BATCH_SIZE = 100  # 중간 저장 단위

    # 출력 설정
    LOG_LEVEL = logging.INFO


logging.basicConfig(
    level=CrawlerConfig.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class Crawler:
    def __init__(self,
                 parser_name: str = 'bootcamper',
                 headless: bool = True):
        self.parser_name = parser_name
        self.headless = headless

        # 파서 매핑
        self.parsers = {
            'bootcamper': SiteParser.parse_bootcamper,
            'remember': SiteParser.parse_remember,
            'saramin': SiteParser.parse_saramin,
            'hrd_net': SiteParser.parse_hrd_net,
        }
        
    @staticmethod
    def create_driver(headless: bool = True) -> Optional[webdriver.Chrome]:
        """드라이버 생성 (정적 메서드)"""
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
                opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service = service, options = opts)
            logging.info("[DRIVER] 드라이버 생성 완료")
            return driver
        except Exception as e:
            logging.error(f'[DRIVER] 드라이버 생성 실패: {e}')
            return None
    
    @contextmanager
    def get_driver(self) -> Generator[webdriver.Chrome, None, None]:
        """컨텍스트 매니저로 드라이버 관리"""
        driver = None
        try:
            driver = self.create_driver(self.headless)
            yield driver
        finally:
            if driver:
                driver.quit()
                logging.info("[DRIVER] 드라이버 종료")
    
    def scroll_and_get_links(self,
                             url: str,
                             pattern: str) -> List[str]:
        """무한 스크롤 페이지에서 링크 수집"""
        with self.get_driver() as driver:
            driver.get(url)
            time.sleep(CrawlerConfig.PAGE_LOAD_WAIT)

            last_count = 0
            retry = 0

            while retry < CrawlerConfig.MAX_SCROLL_RETRY:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(CrawlerConfig.SCROLL_WAIT)

                # Bootcamper 전용: 특정 div 안의 링크만 수집
                links = driver.execute_script("""
                    const pattern = arguments[0];
                    const allLinks = Array.from(document.querySelectorAll('a'));
                    return [...new Set(allLinks
                        .filter(a => a.href.includes(pattern))
                        .map(a => a.href))];
                """, pattern)
                
                logging.info(f"[INFO] 현재 링크 개수: {len(links)}개")
                
                if len(links) == last_count:
                    retry += 1
                else:
                    retry = 0
                    last_count = len(links)
            
            return links

    def collect_hrd_links(self,
                          base_url: str,
                          max_pages: int = 10) -> List[str]:
        """HRD-net 페이지 순회하며 공고 링크 수집

        Args:
            base_url: 첫 페이지 URL (pageIndex=1 포함)
            max_pages: 최대 수집할 페이지 수

        Returns:
            수집된 공고 상세 페이지 URL 리스트
        """
        all_links = []

        with self.get_driver() as driver:
            # 첫 페이지 로드
            driver.get(base_url)
            time.sleep(CrawlerConfig.PAGE_LOAD_WAIT)

            current_page = 1

            while current_page <= max_pages:
                logging.info(f"[INFO] {current_page}페이지 수집 중...")

                # 공고 목록에서 onclick 속성 추출
                jobs_data = driver.execute_script("""
                    const links = document.querySelectorAll('div.company_title h3 a');
                    if (links.length === 0) return [];

                    return Array.from(links).map(a => {
                        const onclick = a.getAttribute('onclick');
                        // onclick에서 tracseId 추출
                        // 예: fn_viewTracseInfo('AIG20253001077153', ...)
                        const match = onclick ? onclick.match(/fn_viewTracseInfo\\('([^']+)'/) : null;
                        return match ? match[1] : null;
                    }).filter(id => id !== null);
                """)

                if not jobs_data:
                    logging.info(f"[INFO] {current_page}페이지에서 공고를 찾을 수 없음. 종료")
                    break

                logging.info(f"[INFO] {current_page}페이지: {len(jobs_data)}개 공고 발견")

                # tracseId로 개별 공고 URL 구성
                for tracse_id in jobs_data:
                    # 개별 공고 상세 페이지 URL
                    detail_url = 'https://m.work24.go.kr/hr/a/a/3100/selectTracseDetl.do?'
                    params = {
                        'tracseId': tracse_id,
                        'tracseTme': '1',
                        'cstmConsTme': '',
                        'crseTracseSe': 'C0061',
                        'trainstCstmrId': '',
                        'tracseReqstsCd': '',
                        'focusId': ''
                    }
                    detail_url += '&'.join([f'{k}={v}' for k, v in params.items()])
                    all_links.append(detail_url)

                logging.info(f"[INFO] 현재까지 총 {len(all_links)}개 링크 수집")

                # 다음 페이지로 이동
                if current_page % 10 == 0:
                    # 10, 20, 30... 페이지: "다음" 버튼 클릭 (다음 10페이지 그룹으로 이동)
                    logging.info(f"[INFO] {current_page}페이지 완료. '다음' 버튼 클릭 시도...")

                    has_next = driver.execute_script("""
                        const nextBtn = document.querySelector('button.btn_page.next');
                        if (nextBtn && !nextBtn.disabled) {
                            nextBtn.click();
                            return true;
                        }
                        return false;
                    """)

                    if not has_next:
                        logging.info(f"[INFO] '다음' 버튼 없음. 마지막 페이지 도달. 종료")
                        break

                    time.sleep(CrawlerConfig.PAGE_LOAD_WAIT)
                else:
                    # 1-9, 11-19, 21-29... 페이지: 개별 페이지 번호 버튼 클릭
                    next_page_num = current_page + 1

                    # onclick="fn_search(N)" 형태로 찾기
                    clicked = driver.execute_script(f"""
                        const buttons = Array.from(document.querySelectorAll('button[onclick*="fn_search"]'));
                        const targetBtn = buttons.find(btn => {{
                            const onclick = btn.getAttribute('onclick');
                            // fn_search(N) 형태에서 N 추출
                            const match = onclick ? onclick.match(/fn_search\\((\\d+)\\)/) : null;
                            return match && parseInt(match[1]) === {next_page_num};
                        }});

                        if (targetBtn && !targetBtn.disabled) {{
                            targetBtn.click();
                            return true;
                        }}
                        return false;
                    """)

                    if not clicked:
                        logging.info(f"[INFO] {next_page_num}페이지 버튼 없음. 종료")
                        break

                    time.sleep(CrawlerConfig.ELEMENT_WAIT)

                current_page += 1

        return all_links

    def extract_job_detail(self,
                           url: str) -> Dict:
        """파서를 선택해서 사용"""
        with self.get_driver() as driver:
            try:
                driver.get(url)
                time.sleep(CrawlerConfig.PAGE_LOAD_WAIT)

                # HTML 가져오기
                html = driver.page_source

                # 선택된 파서 사용
                parser = self.parsers.get(self.parser_name)
                if not parser:
                    raise ValueError(f"존재하지 않는 parser: {self.parser_name}")

                data = parser(html)
                data['url'] = url

                # Remember 사이트인 경우 기업 정보 추출
                if self.parser_name == 'remember' and data.get('companyUrl'):
                    driver.get(data['companyUrl'])
                    time.sleep(CrawlerConfig.ELEMENT_WAIT)
                    # Remember 기업 정보 파싱 로직 필요 시 추가

                return data

            except Exception as e:
                logging.error(f"[ERROR] 오류 ({url}): {e}")
                return {'url': url, 'error': str(e)}

    @staticmethod
    def save_data(data: List[Dict],
                  filename: str = "results.json"):
        """데이터 저장"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV도 저장
        df = pd.DataFrame(data)
        csv_name = filename.replace('.json', '.csv')
        df.to_csv(csv_name, index=False, encoding="utf-8-sig")
        
        logging.info(f"[SAVE] {len(data)}개 레코드 저장 완료: {filename}, {csv_name}")


class ParallelCrawler:
    """병렬 크롤링 전용 클래스"""

    def __init__(self,
                 parser_name: str = 'bootcamper',
                 max_workers: int = 5,
                 headless: bool = True):
        self.parser_name = parser_name
        self.max_workers = max_workers
        self.headless = headless
    
    def crawl_links(self,
                    links: List[str],
                    batch_size: int = 10) -> List[Dict]:
        """링크 병렬 크롤링"""
        all_results = []
        total = len(links)
        
        logging.info(f"[INFO] 총 {total}개 링크를 {self.max_workers}개 워커로 처리 시작")
        
        with ThreadPoolExecutor(max_workers = self.max_workers) as executor:
            # 미래 객체 생성
            future_to_url = {
                executor.submit(self._crawl_single, url): url 
                for url in links
            }
            
            # 완료되는 대로 처리
            for i, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                try:
                    result = future.result()
                    all_results.append(result)
                    logging.info(f"[PROGRESS] {i}/{total} 완료: {url}")
                    
                    # 배치 단위 중간 저장
                    if i % batch_size == 0:
                        Crawler.save_data(
                            all_results, 
                            filename = f"results_batch_{i//batch_size}.json"
                        )
                        
                except Exception as e:
                    logging.error(f"[ERROR] {url} 처리 실패: {e}")
                    all_results.append({'url': url, 'error': str(e)})
        
        return all_results
    
    def _crawl_single(self,
                      url: str) -> Dict:
        """단일 링크 크롤링 (워커 함수)"""
        crawler = Crawler(parser_name=self.parser_name, headless=self.headless)
        return crawler.extract_job_detail(url)


def main():
    # Step 1: 링크 수집
    logging.info("=" * 50)
    logging.info("Step 1: 링크 수집 시작")
    logging.info("=" * 50)

    # Bootcamper 크롤링
    # crawler = Crawler(parser_name='bootcamper', headless=CrawlerConfig.HEADLESS)
    # url = 'https://bootcamper.co.kr'
    # links = crawler.scroll_and_get_links(url, pattern="/class/")

    # HRD-net 크롤링
    crawler = Crawler(
        parser_name=CrawlerConfig.DEFAULT_PARSER,
        headless=CrawlerConfig.HEADLESS
    )
    base_url = 'https://m.work24.go.kr/hr/a/a/1100/trnnCrsInf.do?tracseTme=1&endDate=20261121&keyword1=&keyword2=&pageSize=10&orderBy=&startDate_datepicker=2025-11-21&currentTab=1&topMenuYn=&pop=&tracseId=AIG20253001077153&keywordTrngNm=&crseTracseSeNum=&keywordType=1&gb=&keyword=&kDgtlYn=&ncs=20%7C%EC%A0%95%EB%B3%B4%ED%86%B5%EC%8B%A0+%EC%A0%84%EC%B2%B4&area=00%7C%EC%A0%84%EA%B5%AD+%EC%A0%84%EC%B2%B4&orderKey=&mberSe=&kdgLinkYn=&srchType=all_type&tranRegister=&mberId=&searchYn=N&pageId=2&programMenuIdentification=EBG020000510010&endDate_datepicker=2026-11-21&monthGubun=&pageIndex=1&bgrlInstYn=&tracseTab=1&startDate=20251121&crseTracseSe=&crseTracseSeKDT=&gvrnInstt=&selectNCSKeyword=&action=trnnCrsInfPost.do'

    # 페이지 순회하며 링크 수집
    links = crawler.collect_hrd_links(base_url, max_pages=CrawlerConfig.MAX_PAGES)

    logging.info(f"[INFO] 총 {len(links)}개 링크 수집 완료")

    # 링크 저장 (재시작 시 사용 가능)
    with open("job_links.json", "w", encoding = "utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent = 2)

    # Step 2: 병렬 크롤링
    logging.info("=" * 50)
    logging.info("Step 2: 병렬 크롤링 시작")
    logging.info("=" * 50)

    parallel_crawler = ParallelCrawler(
        parser_name=CrawlerConfig.DEFAULT_PARSER,
        max_workers=CrawlerConfig.MAX_WORKERS,
        headless=CrawlerConfig.HEADLESS
    )
    results = parallel_crawler.crawl_links(
        links,
        batch_size=CrawlerConfig.BATCH_SIZE
    )

    # Step 3: 최종 저장
    logging.info("=" * 50)
    logging.info("Step 3: 최종 데이터 저장")
    logging.info("=" * 50)

    Crawler.save_data(results, filename="final_results.json")

    # 통계 출력
    success_count = sum(1 for r in results if 'error' not in r)
    error_count = len(results) - success_count

    logging.info("=" * 50)
    logging.info(f"크롤링 완료!")
    logging.info(f"  - 성공: {success_count}개")
    logging.info(f"  - 실패: {error_count}개")
    logging.info(f"  - 총합: {len(results)}개")
    logging.info("=" * 50)


class SiteParser:
    """사이트별 파서를 모아놓는 클래스"""

    @staticmethod
    def parse_bootcamper(html: str) -> Dict:
        """Bootcamper 사이트 파싱"""
        soup = BeautifulSoup(html,
                             'html.parser')
        data = {}

        # 1. title
        title = soup.select_one('h1.text-xl')
        data['title'] = title.get_text(strip = True) if title else None

        # 2. tags
        tag_wrapper = soup.select_one('div.flex.flex-wrap.gap-1')
        if tag_wrapper:
            tags = tag_wrapper.select('span.rounded-full.bg-\\[\\#efefef\\]')
            data['tags'] = [tag.get_text(strip = True).strip('#') for tag in tags]
        else:
            data['tags'] = []

        # 3. 주요 정보 (교육기관, 모집기간, 교육일정, 수업시간, 수업방식, 교육장소, 교육정원)
        info_grid = soup.select_one('div.grid.grid-rows-\\[repeat\\(4\\,\\ auto\\)\\]')
        if info_grid:
            info_items = info_grid.select('div.border-b.flex')
            for item in info_items:
                label_span = item.select_one('span.bg-\\[\\#EFEFEF\\]')
                value_span = item.select_one('span.flex.items-center.p-3')
                if label_span and value_span:
                    label = label_span.get_text(strip = True)
                    value = value_span.get_text(strip = True)
                    data[label] = value

        # 4-8. section 정보 파싱 헬퍼 함수
        def parse_section(section_title: str) -> Dict:
            """섹션별 정보 파싱"""
            section_data = {}
            sections = soup.select('section.py-8.font-medium')

            for section in sections:
                h3 = section.select_one('h3.text-lg')
                if h3 and section_title in h3.get_text():
                    wrapper = section.select_one('div.space-y-4')
                    if wrapper:
                        # 방법 1: div.flex.flex-wrap.gap-x-2 형식 (수강대상, 취업서비스 등)
                        items = wrapper.select('div.flex.flex-wrap.gap-x-2')
                        if items:
                            for item in items:
                                label_div = item.select_one('div.text-bcMainRed.font-bold')
                                value_div = item.select_one('div.leading-6')
                                if label_div:
                                    label = label_div.get_text(strip = True)
                                    value = value_div.get_text(strip = True) if value_div else None
                                    section_data[label] = value
                        else:
                            # 방법 2: 직접 div 구조 (수강료 등)
                            # wrapper 바로 아래의 div들 찾기
                            all_labels = wrapper.select('div.text-bcMainRed.font-bold')
                            for label_div in all_labels:
                                label = label_div.get_text(strip = True)
                                # 형제 요소 중 div.leading-6 찾기
                                parent = label_div.parent
                                value_div = parent.select_one('div.leading-6') if parent else None
                                if value_div:
                                    # div.leading-normal이 있으면 그것을, 없으면 leading-6 텍스트
                                    value_normal = value_div.select_one('div.leading-normal')
                                    value = value_normal.get_text(strip = True) if value_normal else value_div.get_text(strip = True)
                                else:
                                    value = None
                                section_data[label] = value
                    break

            return section_data

        # 4. 어떤 분이 수강하면 좋을까요?
        data['수강대상'] = parse_section('어떤 분이')

        # 5. 지원 절차를 알려주세요
        sections = soup.select('section.py-8.font-medium')
        for section in sections:
            h3 = section.select_one('h3.text-lg')
            if h3 and '지원 절차' in h3.get_text():
                wrapper = section.select_one('div.space-y-4')
                if wrapper:
                    steps = []
                    items = wrapper.select('div.flex.flex-wrap.gap-x-2')
                    for item in items:
                        label_div = item.select_one('div.text-bcMainRed.font-bold')
                        value_div = item.select_one('div.leading-6')
                        
                        label_text = label_div.get_text(strip = True)
                        value_text = value_div.get_text(strip = True)

                        if label_text and value_text:
                            steps.append({
                                label_text: value_text
                            })
                    data['지원절차'] = steps
                break

        # 6. 수강료는?
        data['수강료'] = parse_section('수강료')

        # 7. 자세한 커리큘럼을 알고 싶어요
        sections = soup.select('section.py-8.font-medium')
        for section in sections:
            h3 = section.select_one('h3.text-lg')
            if h3 and '커리큘럼' in h3.get_text():
                wrapper = section.select_one('div.space-y-4')
                if wrapper:
                    description = wrapper.select_one('div.mb-2')
                    link = wrapper.select_one('a.text-sm')
                    data['커리큘럼'] = {
                        '설명': description.get_text(strip = True) if description else None,
                        '링크': link['href'] if link and link.get('href') else None
                    }
                break

        # 8. 어떤 취업서비스가 제공되나요?
        data['취업서비스'] = parse_section('취업')

        return data

    @staticmethod
    def parse_remember(html: str) -> Dict:
        """Remember 사이트 파싱 (React 기반)

        Note: Remember는 React로 구현되어 JavaScript 실행이 필요할 수 있습니다.
        필요시 driver.execute_script()를 사용한 별도 메서드로 구현하세요.

        기존 JavaScript 파싱 로직:

        const result = {};

        const title = document.querySelector('h1');
        result.title = title ? title.textContent.trim() : null;

        const allDivs = Array.from(document.querySelectorAll('div'));
        ['연봉', '근무지', '경력', '학력', '마감일'].forEach(label => {
            const labelDiv = allDivs.find(d => d.textContent.trim() === label);
            if (labelDiv && labelDiv.nextElementSibling) {
                result[label] = labelDiv.nextElementSibling.textContent.trim();
            }
        });

        ['회사소개', '주요업무', '자격 요건', '우대사항', '채용절차', '기타안내'].forEach(section => {
            const heading = Array.from(document.querySelectorAll('h2, h3, strong'))
                .find(h => h.textContent.includes(section));
            if (heading) {
                const content = heading.closest('section') || heading.parentElement;
                result[section] = content ? content.textContent.trim() : null;
            }
        });

        const stackSpans = document.querySelectorAll('span.sc-9ab07b31-1, span.hLGjbI');
        if (stackSpans.length > 0) {
            result['기술스택'] = Array.from(stackSpans).map((el, idx) => ({
                index: idx + 1,
                text: el.textContent.trim()
            }));
        }

        const companyLink = Array.from(document.querySelectorAll('a'))
            .find(a => a.href.includes('/company/'));
        result.companyUrl = companyLink ? companyLink.href : null;

        기업 정보 JavaScript 로직:

        const result = {};
        const allDivs = Array.from(document.querySelectorAll('div'));

        ['대표자', '설립일', '업종', '기업유형', '위치'].forEach(label => {
            const labelDiv = allDivs.find(d => d.textContent.trim() === label);
            if (labelDiv && labelDiv.nextElementSibling) {
                result[label] = labelDiv.nextElementSibling.textContent.trim();
            }
        });

        const homepage = Array.from(document.querySelectorAll('a'))
            .find(a => a.href.includes('http') && !a.href.includes('rememberapp'));
        result['홈페이지'] = homepage ? homepage.href : null;

        const salary = document.querySelector('b');
        result['평균연봉'] = salary ? salary.textContent.trim() : null;
        """
        soup = BeautifulSoup(html, 'html.parser')
        # BeautifulSoup으로 파싱 시도 (React 렌더링 후 HTML)
        # 필요시 위의 JavaScript 로직을 별도 메서드로 구현
        return {}

    @staticmethod
    def parse_saramin(html: str) -> Dict:
        """사람인 사이트 파싱 (나중에 추가)"""
        soup = BeautifulSoup(html, 'html.parser')
        return {}
    
    @staticmethod
    def parse_hrd_net(html: str) -> Dict:
        """HRD-net (고용24) 사이트 파싱"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}

        # 좌측 영역 찾기
        left_area = soup.select_one('div.left_area.br.js_s')
        if not left_area:
            return data

        # 1. 교육원 이름
        corp_info = left_area.select_one('p.corp_info strong')
        data['교육원'] = corp_info.get_text(strip=True) if corp_info else None

        # 2. 타이틀
        title = left_area.select_one('strong.title')
        data['title'] = title.get_text(strip=True) if title else None

        # 3. 모집 상태
        status_btn = left_area.select_one('p.btn.small')
        data['모집상태'] = status_btn.get_text(strip=True) if status_btn else None

        # 4. ul.list 안의 li 항목들 파싱
        info_list = left_area.select_one('ul.list')
        if info_list:
            list_items = info_list.find_all('li', recursive=False)

            for li in list_items:
                strong = li.find('strong', class_='block')
                if not strong:
                    continue

                label = strong.get_text(strip=True)

                # 각 항목별 처리
                if '훈련기관 직종별 취업률' in label:
                    bar = li.select_one('span.bar')
                    data['취업률'] = bar.get('label') if bar and bar.get('label') else bar.get_text(strip=True) if bar else None

                elif '수강생 평균 만족도' in label:
                    blind_span = li.select_one('span.blind')
                    if blind_span and blind_span.get('title'):
                        data['만족도'] = blind_span['title']
                    else:
                        data['만족도'] = blind_span.get_text(strip=True) if blind_span else None

                elif 'NCS 직무분류' in label:
                    con = li.select_one('span.con.mb08')
                    data['NCS직무분류'] = con.get_text(strip=True) if con else None

                elif 'NCS 수준' in label:
                    con = li.select_one('span.con.mb08')
                    data['NCS수준'] = con.get_text(strip=True) if con else None

                elif 'NCS 적용 여부' in label:
                    con = li.select_one('span.con.mb08')
                    data['NCS적용여부'] = con.get_text(strip=True) if con else None

                elif '관련 자격증' in label:
                    con = li.select_one('span.con.mb08')
                    data['관련자격증'] = con.get_text(strip=True) if con else None

                elif '훈련기간' in label:
                    con = li.select_one('span.con.mb08')
                    data['훈련기간'] = con.get_text(strip=True) if con else None

                elif '훈련시간' in label:
                    con = li.select_one('span')
                    data['훈련시간'] = con.get_text(strip=True) if con else None

                elif '수강생 평균 연령대' in label:
                    con = li.select_one('span.con.mb08')
                    data['평균연령대'] = con.get_text(strip=True) if con else None

                elif '담당자 성명' in label:
                    con = li.select_one('span.con.mb08')
                    data['담당자성명'] = con.get_text(strip=True) if con else None

                elif '담당자 전화번호' in label:
                    con = li.select_one('span.con.mb08')
                    data['담당자전화'] = con.get_text(strip=True) if con else None

                elif '담당자 이메일' in label:
                    con = li.select_one('span.con.mb08')
                    data['담당자이메일'] = con.get_text(strip=True) if con else None

                elif '주관부처' in label:
                    con = li.select_one('span.con.mb08')
                    data['주관부처'] = con.get_text(strip=True) if con else None

                elif '훈련유형' in label:
                    con = li.select_one('span.con.mb08')
                    data['훈련유형'] = con.get_text(strip=True) if con else None

                elif '취업처 임금평균' in label:
                    con = li.select_one('span.con.mb08')
                    data['임금평균'] = con.get_text(strip=True) if con else None

                elif '시간표' in label:
                    link = li.select_one('a.verPC')
                    data['시간표'] = link.get_text(strip=True) if link else None

                elif '주야구분/주말여부' in label:
                    con = li.select_one('span.con.mb08')
                    data['주야구분'] = con.get_text(strip=True) if con else None

                elif '실시현황' in label:
                    con = li.select_one('span.con.mb08')
                    data['실시현황'] = con.get_text(strip=True) if con else None

                elif '원격/집체 여부' in label:
                    con = li.select_one('span.con.mb08')
                    data['수업방식'] = con.get_text(strip=True) if con else None

                elif '안내사항' in label or li.select_one('span.tit'):
                    # 안내사항은 별도 처리
                    tit_span = li.select_one('span.tit')
                    if tit_span and '안내사항' in tit_span.get_text():
                        con_span = li.select_one('span.con')
                        data['안내사항'] = con_span.get_text(strip=True) if con_span else None

        # 5. 우측 영역 - 훈련비
        flex1 = soup.select_one('div.flex1')
        if flex1:
            # 훈련비 찾기
            training_cost_h3 = flex1.find('h3', class_='t3_sb', string=lambda x: x and '훈련비' in x)
            if training_cost_h3:
                # 형제 요소에서 ul.emp_info_dtl 찾기
                ul = training_cost_h3.find_next_sibling('ul', class_='emp_info_dtl')
                if ul:
                    cost_p = ul.select_one('p[style*="font-size: 20px"]')
                    data['훈련비'] = cost_p.get_text(strip=True) if cost_p else None

        return data


if __name__ == "__main__":
    '''
    사용 방법

    # Bootcamper 크롤링
    crawler = Crawler(parser_name='bootcamper', headless=True)
    links = crawler.scroll_and_get_links('https://bootcamper.co.kr', pattern='/class/')
    results = [crawler.extract_job_detail(link) for link in links]

    # Remember 크롤링 (나중에)
    crawler = Crawler(parser_name='remember', headless=True)
    # Remember용 파서는 필요 시 구현

    🟦 방법 1: 직접 실행 (가장 간단) ✅
        python crawler_moduler.py

    이렇게 실행하면 main() 함수가 자동으로 실행되면서:
        1. Bootcamper 사이트에서 링크 수집
        2. 병렬로 크롤링
        3. JSON/CSV 파일로 저장

        별도 코드 작성 필요 없음!

    🟦 방법 2: 모듈로 import해서 사용
        다른 파일(예: my_script.py)이나 Jupyter notebook에서:

        from crawler_moduler import Crawler, ParallelCrawler

    # 링크만 수집하고 싶을 때
        crawler = Crawler(parser_name='bootcamper', headless=True)
        links = crawler.scroll_and_get_links('https://bootcamper.co.kr', pattern='/class/')
        print(f"수집된 링크: {len(links)}개")

    # 특정 링크만 크롤링하고 싶을 때
        result = crawler.extract_job_detail(links[0])
        print(result)

    # 병렬 크롤링
        parallel = ParallelCrawler(parser_name='bootcamper', max_workers=5)
        results = parallel.crawl_links(links[:10])  # 처음 10개만


    처음 사용할 때: 방법 1 (직접 실행)
        python crawler_moduler.py

    커스터마이징이 필요할 때: 방법 2 (import 사용)
        - URL 바꾸기
        - 일부 링크만 테스트
        - 다른 파서 사용

    '''
    main()