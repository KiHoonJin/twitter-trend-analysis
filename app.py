import streamlit as st
from playwright.sync_api import sync_playwright
import os

# 크롤링 함수 정의
def crawl_tweets(usernames):
    tweets = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 트위터 로그인
        page.goto('https://x.com/i/flow/login')
        page.fill('input[name="text"]', os.getenv('TWITTER_USERNAME'))
        page.click('div[data-testid="LoginForm_Login_Button"]')
        page.wait_for_timeout(2000)  # 2초 대기
        page.fill('input[name="password"]', os.getenv('TWITTER_PASSWORD'))
        page.click('div[data-testid="LoginForm_Login_Button"]')
        page.wait_for_timeout(5000)  # 로그인 후 5초 대기

        for user in usernames:
            page.goto(f'https://twitter.com/{user}')
            page.wait_for_timeout(5000)  # 5초 대기
            tweets[user] = []
            for tweet in page.query_selector_all('div[data-testid="tweetText"]'):
                tweets[user].append(tweet.text_content())
        browser.close()
    return tweets

# 텍스트 요약 및 키워드 추출 함수 정의
def summarize_and_extract_keywords(tweets):
    summary = {}
    for user, tws in tweets.items():
        text = ' '.join(tws)
        summary[user] = {
            'summary': text[:500] + '...' if len(text) > 500 else text,
            'keywords': extract_keywords(text)
        }
    return summary

def extract_keywords(text):
    # 간단한 키워드 추출 예제
    from collections import Counter
    words = text.split()
    keywords = Counter(words).most_common(10)
    return [word for word, freq in keywords]

# Streamlit UI 구성
st.title("Twitter Trend Analysis")
st.write("Analyze recent tweets from specified Twitter accounts and extract trends and keywords.")

user_input = st.text_area("Enter Twitter accounts (one per line)", "DegenerateNews\nWatcherGuru\nVitalikButerin\nCointelegraph\ncrypto")
usernames = [u.strip() for u in user_input.split('\n') if u.strip()]

if st.button("Analyze"):
    with st.spinner("Crawling tweets..."):
        tweets = crawl_tweets(usernames)
    with st.spinner("Summarizing and extracting keywords..."):
        summary = summarize_and_extract_keywords(tweets)

    st.write("## Summary of Twitter Accounts")
    for user, data in summary.items():
        st.write(f"### {user}")
        st.write(f"**Summary:** {data['summary']}")
        st.write(f"**Keywords:** {', '.join(data['keywords'])}")

    st.write("## Raw Tweets")
    for user, tws in tweets.items():
        st.write(f"### {user}")
        st.write('\n'.join(tws))

# 파일 저장
if st.button("Download Summary"):
    with open('summary.txt', 'w', encoding='utf-8') as f:
        for user, data in summary.items():
            f.write(f"### {user}\n")
            f.write(f"**Summary:** {data['summary']}\n")
            f.write(f"**Keywords:** {', '.join(data['keywords'])}\n\n")
    st.success('Summary saved as summary.txt')
    
if st.button("Download Raw Data"):
    with open('raw_tweets.txt', 'w', encoding='utf-8') as f:
        for user, tws in tweets.items():
            f.write(f"### {user}\n")
            f.write('\n'.join(tws))
            f.write('\n\n')
    st.success('Raw data saved as raw_tweets.txt')