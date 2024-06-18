import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from rake_nltk import Rake
import nltk

nltk.download('punkt')
nltk.download('stopwords')

# 크롬 드라이버 경로 설정
driver_path = '/Users/1110398/Desktop/chromedriver'  # 크롬 드라이버의 실제 경로로 수정하세요.
service = Service(driver_path)
options = webdriver.ChromeOptions()

# 헤드리스 모드 설정
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Chrome이 자동화된 소프트웨어에 의해 제어되고 있다는 메시지를 제거
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 크롬 드라이버 실행
driver = webdriver.Chrome(service=service, options=options)

# 트위터 로그인 함수
def twitter_login(driver, wait):
    driver.get('https://x.com/i/flow/login')
    try:
        username = wait.until(EC.presence_of_element_located((By.NAME, 'text')))
        username.send_keys('au8ust22nd')  # 실제 트위터 아이디로 수정하세요.
        username.send_keys(Keys.RETURN)
        password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password.send_keys('880822kh!!')  # 실제 트위터 비밀번호로 수정하세요.
        password.send_keys(Keys.RETURN)
        time.sleep(5)  # 로그인 완료 대기
    except Exception as e:
        print(f"Login failed: {e}")

# 트윗 크롤링 함수
def crawl_tweets(driver, wait, user, max_scroll_attempts=10):
    driver.get(f'https://twitter.com/{user}')
    all_tweets = []
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(3)  # Page Down 후 페이지 로드 대기
        
        # 페이지 소스를 가져와서 BeautifulSoup으로 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tweets = soup.find_all('div', {'data-testid': 'tweetText'})

        for tweet in tweets:
            tweet_text = tweet.get_text()
            if tweet_text and tweet_text not in all_tweets:
                all_tweets.append(tweet_text)

        scroll_attempts += 1

    return all_tweets

# 텍스트 요약 및 키워드 추출 함수
def summarize_and_extract_keywords(tweets):
    # 텍스트 데이터 전처리
    filtered_tweets = [tweet for tweet in tweets if "http" not in tweet and "We're on Telegram" not in tweet and len(tweet) > 20]
    text = ' '.join(filtered_tweets)
    
    # 간단한 요약
    summary = ' '.join(filtered_tweets[:5])
    
    # 키워드 추출
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()[:10]

    return summary, keywords, filtered_tweets

def truncate_summary(summary, length=100):
    if len(summary) <= length:
        return summary
    else:
        truncated = summary[:length]
        last_space = truncated.rfind(' ')
        return truncated[:last_space] + "..."

# 트위터 계정 리스트
twitter_accounts = ['DegenerateNews', 'WatcherGuru', 'CoinDesk', 'Cointelegraph', 'crypto']  # 실제 트위터 계정으로 수정하세요.

# 로그인
wait = WebDriverWait(driver, 60)
twitter_login(driver, wait)

# 결과 저장용 리스트
results = []

# 각 계정의 트윗을 크롤링하여 요약 및 키워드 추출
for account in twitter_accounts:
    tweets = crawl_tweets(driver, wait, account)
    summary, keywords, filtered_tweets = summarize_and_extract_keywords(tweets)
    results.append({
        'account': account,
        'summary': truncate_summary(summary, 200),
        'keywords': keywords,
        'tweets': filtered_tweets
    })

# 크롤링 완료 후 드라이버 종료
driver.quit()

# 분석 결과 요약 생성
trend_analysis = []
for i, result in enumerate(results):
    trend_analysis.append(f"{i+1}. {result['account']} 계정의 주요 트렌드: {result['summary']}")

# 파일로 저장
with open('twitter_trend_analysis_summary.txt', 'w', encoding='utf-8') as summary_file, open('twitter_trend_analysis_raw.txt', 'w', encoding='utf-8') as raw_file:
    # 요약 파일 작성
    for line in trend_analysis:
        summary_file.write(line + '\n')
    
    summary_file.write("\nTop 10 Keywords:\n")
    for result in results:
        summary_file.write(f"\nKeywords for {result['account']}:\n")
        for keyword in result['keywords']:
            summary_file.write(f"{keyword}\n")
    
    # Raw 데이터 파일 작성
    for result in results:
        raw_file.write(f"Raw tweets for {result['account']}:\n")
        for tweet in result['tweets']:
            raw_file.write(f"{tweet}\n")
        raw_file.write("\n")