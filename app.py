import streamlit as st
import csv
import os
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
driver_path = os.getenv('CHROMEDRIVER_PATH')
if not driver_path:
    raise ValueError("Please set the CHROMEDRIVER_PATH environment variable")

# 크롬 드라이버 실행
service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=service, options=options)

def twitter_login(driver, wait):
    driver.get('https://x.com/i/flow/login')
    try:
        username = wait.until(EC.presence_of_element_located((By.NAME, 'text')))
        username.send_keys('au8ust22nd')
        username.send_keys(Keys.RETURN)
        password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password.send_keys('880822kh!!')
        password.send_keys(Keys.RETURN)
        time.sleep(5)
    except Exception as e:
        print(f"Login failed: {e}")

def crawl_tweets(driver, wait, user, max_scroll_attempts=10):
    driver.get(f'https://twitter.com/{user}')
    all_tweets = []
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tweets = soup.find_all('div', {'data-testid': 'tweetText'})

        for tweet in tweets:
            tweet_text = tweet.get_text()
            if tweet_text and tweet_text not in all_tweets:
                all_tweets.append(tweet_text)

        scroll_attempts += 1

    return all_tweets

def summarize_and_extract_keywords(tweets):
    text = ' '.join(tweets)
    summary = ' '.join(tweets[:5])
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()[:10]
    return summary, keywords

twitter_accounts = ['DegenerateNews', 'WatcherGuru', 'CoinDesk', 'Cointelegraph', 'crypto']
wait = WebDriverWait(driver, 60)
twitter_login(driver, wait)

results = []
for account in twitter_accounts:
    tweets = crawl_tweets(driver, wait, account)
    summary, keywords = summarize_and_extract_keywords(tweets)
    results.append({'account': account, 'summary': summary, 'keywords': keywords})

driver.quit()

trend_analysis = []
for result in results:
    trend_analysis.append(f"{result['account']}의 주요 트렌드: {result['summary']}")

with open('twitter_trend_analysis_summary.txt', 'w', encoding='utf-8') as file:
    for line in trend_analysis:
        file.write(line + '\n')

with open('twitter_trend_analysis_raw.txt', 'w', encoding='utf-8') as file:
    for result in results:
        file.write(f"Tweets from {result['account']}:\n")
        for tweet in result['tweets']:
            file.write(tweet + '\n')
        file.write("\n")

st.title('Twitter Trend Analysis')
st.write("트위터 계정의 주요 트렌드와 키워드 분석 결과를 확인하세요.")

for line in trend_analysis:
    st.write(line)

st.write("\nTop 10 Keywords:\n")
for result in results:
    st.write(f"\nKeywords for {result['account']}:\n")
    for keyword in result['keywords']:
        st.write(keyword)