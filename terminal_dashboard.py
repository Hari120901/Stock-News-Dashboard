import streamlit as st
import pandas as pd
import feedparser
from textblob import TextBlob
from datetime import datetime, timedelta
import yfinance as yf

# --------------------------
# STOCK LIST
# --------------------------
stocks = [
"HDFCBANK","RELIANCE","ICICIBANK","BHARTIARTL","SBIN","SHRIRAMFIN","LT","INFY","INDIGO","TCS",
"ETERNAL","BEL","M&M","AXISBANK","KOTAKBANK","BAJFINANCE","SUNPHARMA","ITC","JIOFIN","ULTRACEMCO",
"TATASTEEL","ONGC","COALINDIA","MARUTI","TMPV","HINDALCO","BAJAJ-AUTO","POWERGRID","NTPC","ADANIPORTS",
"EICHERMOT","ADANIENT","TITAN","DRREDDY","APOLLOHOSP","GRASIM","ASIANPAINT","TRENT","WIPRO","MAXHEALTH",
"HDFCLIFE","HINDUNILVR","HCLTECH","BAJAJFINSV","NESTLEIND","TECHM","CIPLA","TATACONSUM","JSWSTEEL","SBILIFE"
]

# Map NSE ticker symbols to Yahoo Finance symbols if needed
ticker_map = {
    "HDFCBANK":"HDFCBANK.NS", "RELIANCE":"RELIANCE.NS", "ICICIBANK":"ICICIBANK.NS",
    "BHARTIARTL":"BHARTIARTL.NS","SBIN":"SBIN.NS","TCS":"TCS.NS","INFY":"INFY.NS",
    # ... add all 50 mappings here ...
}

# --------------------------
# RSS FEEDS
# --------------------------
feeds = [
"https://news.google.com/rss/search?q=indian+stock+market",
"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
]

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
# FETCH PRICE TREND
# --------------------------
def price_trend(stock, news_time):
    try:
        ticker = ticker_map.get(stock, None)
        if not ticker:
            return "NA"
        # Get 30 min before and after news
        start = news_time - timedelta(minutes=30)
        end = news_time + timedelta(minutes=30)
        data = yf.download(ticker, start=start, end=end, interval='5m', progress=False)
        if data.empty: return "NA"
        open_price = data['Open'].iloc[0]
        close_price = data['Close'].iloc[-1]
        if close_price > open_price:
            return "Bullish 📈"
        elif close_price < open_price:
            return "Bearish 📉"
        else:
            return "Neutral ➖"
    except:
        return "NA"

# --------------------------
# STREAMLIT DASHBOARD
# --------------------------
st.set_page_config(layout="wide")
st.title("📊 NSE Stock News Terminal with Trend Impact")

news_df = fetch_news()
matched_df = match_stocks(news_df)

if not matched_df.empty:
    matched_df["Time"] = pd.to_datetime(matched_df["Time"])
    matched_df["Trend"] = matched_df.apply(lambda x: price_trend(x["Stock"], x["Time"]), axis=1)
    matched_df = matched_df.sort_values(by="Time", ascending=False)
    
    st.dataframe(matched_df[["Stock","Headline","Time","Sentiment","Signal","Impact","Trend"]], height=900)
else:
    st.write("No recent news for your stocks.")
