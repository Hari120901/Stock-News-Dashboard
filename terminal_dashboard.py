import streamlit as st
import pandas as pd
import feedparser
from textblob import TextBlob
from datetime import datetime, timedelta

# --------------------------
# STOCK LIST
# --------------------------
stocks = [
"HDFC Bank","Reliance Industries","ICICI Bank","State Bank of India","Tata Consultancy Services"
]

# --------------------------
# RSS FEEDS
# --------------------------
feeds = [
"https://news.google.com/rss/search?q=indian+stock+market",
"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
]

# --------------------------
# IMPACT WORDS
# --------------------------
impact_words = ["acquisition","merger","stake","block deal","bulk deal","order win",
"fraud","investigation","rating","downgrade","upgrade","fund raising"]

# --------------------------
# FETCH NEWS
# --------------------------
def fetch_news():
    news_list = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            try:
                time = datetime(*entry.published_parsed[:6])
            except:
                time = datetime.now()
            news_list.append({
                "headline": entry.title,
                "link": entry.link,
                "time": time
            })
    return pd.DataFrame(news_list)

# --------------------------
# MATCH STOCKS + SENTIMENT
# --------------------------
def match_stocks(news_df):
    matched = []
    for _, row in news_df.iterrows():
        title = row["headline"].lower()
        for stock in stocks:
            if stock.lower() in title:
                score = TextBlob(title).sentiment.polarity
                if score > 0.1:
                    sentiment = "Positive"
                    icon = "📈"
                elif score < -0.1:
                    sentiment = "Negative"
                    icon = "📉"
                else:
                    sentiment = "Neutral"
                    icon = "➖"
                impact = "High" if any(w in title for w in impact_words) else "Low"
                matched.append({
                    "Stock": stock,
                    "Headline": row["headline"],
                    "Link": row["link"],
                    "Time": row["time"],
                    "Sentiment": sentiment,
                    "Signal": icon,
                    "Impact": impact
                })
    return pd.DataFrame(matched)

# --------------------------
# DASHBOARD
# --------------------------
st.set_page_config(layout="wide")
st.title("📊 NSE Stock News Terminal - Live Updates Every 2 Minutes")

news_df = fetch_news()
matched_df = match_stocks(news_df)

if not matched_df.empty:
    matched_df["Time"] = pd.to_datetime(matched_df["Time"])
    matched_df = matched_df.sort_values(by="Time", ascending=False)
    st.dataframe(matched_df[["Stock","Headline","Signal","Sentiment","Impact","Time"]], height=800)
else:
    st.write("No recent news for your stocks.")
