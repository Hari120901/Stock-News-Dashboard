# terminal_dashboard.py
import streamlit as st
import pandas as pd
import feedparser
from textblob import TextBlob
from datetime import datetime, timedelta
import time

# --------------------------
# AUTO REFRESH every 2 minutes
# --------------------------
refresh_interval = 120  # seconds
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
else:
    if time.time() - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = time.time()
        st.experimental_rerun()

# --------------------------
# STOCK LIST (50 NSE stocks)
# --------------------------
stocks = [
"HDFCBANK","RELIANCE","ICICIBANK","BHARTIARTL","SBIN","SHRIRAMFIN","LT","INFY","INDIGO","TCS",
"ETERNAL","BEL","M&M","AXISBANK","KOTAKBANK","BAJFINANCE","SUNPHARMA","ITC","JIOFIN","ULTRACEMCO",
"TATASTEEL","ONGC","COALINDIA","MARUTI","TMPV","HINDALCO","BAJAJ-AUTO","POWERGRID","NTPC","ADANIPORTS",
"EICHERMOT","ADANIENT","TITAN","DRREDDY","APOLLOHOSP","GRASIM","ASIANPAINT","TRENT","WIPRO","MAXHEALTH",
"HDFCLIFE","HINDUNILVR","HCLTECH","BAJAJFINSV","NESTLEIND","TECHM","CIPLA","TATACONSUM","JSWSTEEL","SBILIFE"
]

# --------------------------
# RSS FEEDS
# --------------------------
feeds = [
"https://news.google.com/rss/search?q=indian+stock+market",
"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
]

# Keywords that imply high impact
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
                time_stamp = datetime(*entry.published_parsed[:6])
            except:
                time_stamp = datetime.now()
            news_list.append({
                "headline": entry.title,
                "link": entry.link,
                "time": time_stamp
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
# CATEGORIZE BY TIME
# --------------------------
def categorize(df):
    now = datetime.now()
    table = []
    for stock in stocks:
        stock_df = df[df["Stock"]==stock]
        last30 = stock_df[stock_df["Time"] >= now - timedelta(minutes=30)]
        today = stock_df[stock_df["Time"].dt.date == now.date()]
        yesterday = stock_df[stock_df["Time"].dt.date == now.date()-timedelta(days=1)]
        
        last30_time = last30["Time"].iloc[0].strftime("%d-%m %H:%M") if not last30.empty else ""
        today_time = today["Time"].iloc[0].strftime("%d-%m %H:%M") if not today.empty else ""
        yesterday_time = yesterday["Time"].iloc[0].strftime("%d-%m %H:%M") if not yesterday.empty else ""
        
        table.append({
            "Stock": stock,
            "Last 30 Min": " | ".join(last30["Headline"].head(1)),
            "Last 30 Min Time": last30_time,
            "Today": " | ".join(today["Headline"].head(1)),
            "Today Time": today_time,
            "Yesterday": " | ".join(yesterday["Headline"].head(1)),
            "Yesterday Time": yesterday_time,
            "Sentiment": " | ".join(stock_df["Sentiment"].head(1)),
            "Signal": " | ".join(stock_df["Signal"].head(1)),
            "Impact": " | ".join(stock_df["Impact"].head(1))
        })
    return pd.DataFrame(table)

# --------------------------
# STREAMLIT DASHBOARD
# --------------------------
st.set_page_config(layout="wide")
st.title("📊 NSE Stock News Terminal - Auto Refresh Every 2 Minutes")

news_df = fetch_news()
matched_df = match_stocks(news_df)

if not matched_df.empty:
    matched_df["Time"] = pd.to_datetime(matched_df["Time"])
    dashboard = categorize(matched_df)

    # Highlight sentiment
    def highlight_sentiment(val):
        if val=="Positive": return 'background-color: #d4edda'  # Green
        elif val=="Negative": return 'background-color: #f8d7da'  # Red
        else: return 'background-color: #fefefe'  # White

    st.dataframe(
        dashboard.style.applymap(
            lambda x: highlight_sentiment(x) if x in ["Positive","Negative","Neutral"] else '',
            subset=["Sentiment"]
        ),
        height=900,
        use_container_width=True
    )
else:
    st.write("No recent news for your stocks.")
