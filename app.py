import os
import streamlit as st
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

st.title("Twitter Trend Analysis")
st.write("Analyze recent tweets from specified Twitter accounts and extract trends and keywords.")

twitter_accounts = st.text_area("Enter Twitter accounts (one per line)", "DegenerateNews\nWatcherGuru\nCoinDesk\nCointelegraph\ncrypto").split()

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')

def twitter_login(driver, wait):
    driver.get('https://x.com/i/flow/login')
    username = wait.until(EC.presence_of_element_located((By.NAME, 'text')))
    username.send_keys('au8ust22nd')
    username.send_keys(Keys.RETURN)
    password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    password.send_keys('880822kh!')
    password.send_keys(Keys.RETURN)
    time.sleep(5)

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

if st.button('Analyze Tweets'):
    if not twitter_accounts:
        st.error("Please enter at least one Twitter account.")
    else:
        driver_path = CHROMEDRIVER_PATH
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
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
        
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 60)
        
        try:
            twitter_login(driver, wait)
            results = []
            for account in twitter_accounts:
                tweets = crawl_tweets(driver, wait, account)
                summary, keywords = summarize_and_extract_keywords(tweets)
                results.append({
                    'account': account,
                    'tweets': tweets,
                    'summary': summary,
                    'keywords': keywords
                })
        finally:
            driver.quit()
        
        raw_data_file = 'twitter_trend_analysis_raw.txt'
        summary_file = 'twitter_trend_analysis_summary.txt'

        with open(raw_data_file, 'w', encoding='utf-8') as file:
            for result in results:
                file.write(f"Summary for {result['account']}:\n")
                for tweet in result['tweets']:
                    file.write(f"{tweet}\n")
                file.write("\n")

        with open(summary_file, 'w', encoding='utf-8') as file:
            for i, result in enumerate(results):
                file.write(f"{i+1}. {result['account']} 계정의 주요 트렌드: {result['summary']}\n")
            file.write("\nTop 10 Keywords:\n")
            for result in results:
                file.write(f"\nKeywords for {result['account']}:\n")
                for keyword in result['keywords']:
                    file.write(f"{keyword}\n")

        st.success("Analysis completed.")
        st.download_button("Download Raw Data", data=open(raw_data_file).read(), file_name=raw_data_file)
        st.download_button("Download Summary", data=open(summary_file).read(), file_name=summary_file)