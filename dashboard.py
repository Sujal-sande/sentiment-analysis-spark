import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from collections import Counter
from streamlit_autorefresh import st_autorefresh

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Sentiment Dashboard",
    layout="wide"
)

# ---------------- FORCE DARK THEME ----------------
st.markdown("""
<style>

/* Full background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Remove white blocks */
[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}

/* KPI Cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 15px;
}

/* Headings */
h1 {
    text-align: center;
    color: #00F5D4;
}
h2, h3 {
    color: #00ADB5;
}

/* Fix text visibility */
div, label, span {
    color: white !important;
}

/* Inputs */
input {
    background-color: #1f2937 !important;
    color: white !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: #1f2937;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🚀 Social Media Sentiment Dashboard")
st.markdown("<h3 style='text-align:center; color:#ccc;'>Real-time Big Data Sentiment Insights</h3>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("processed_data.csv")

# ---------------- TOPIC SEARCH ----------------
st.markdown("## 🔍 Topic-Based Analysis")

topic = st.text_input("Enter topic (e.g., Tesla, IPL, iPhone)")

if topic:
    df = df[df["clean_text"].str.contains(topic, case=False)]
    
    if df.empty:
        st.warning(f"No data found for '{topic}'")
    else:
        st.success(f"Showing results for: {topic}")

# ---------------- STREAMING MODE ----------------
st.markdown("## ⚡ Live Streaming Mode")

start_stream = st.toggle("Start Streaming")

if start_stream:
    # Auto refresh every 3 seconds
    count = st_autorefresh(interval=3000, limit=100, key="fizzbuzzcounter")

    # Gradually increase data size
    batch_size = min((count + 1) * 5000, len(df))
    df = df.head(batch_size)

    st.info(f"Streaming {batch_size} records...")
else:
    st.success("Streaming paused")


# ---------------- SIDEBAR FILTER ----------------
st.sidebar.title("⚙️ Filters")

selected_sentiment = st.sidebar.multiselect(
    "Select Sentiment",
    options=df["sentiment_result"].unique(),
    default=df["sentiment_result"].unique()
)

df = df[df["sentiment_result"].isin(selected_sentiment)]

# ---------------- KPI SECTION ----------------
total = len(df)
positive = len(df[df["sentiment_result"] == "positive"])
negative = len(df[df["sentiment_result"] == "negative"])
neutral = len(df[df["sentiment_result"] == "neutral"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Total Tweets", total)
col2.metric("😊 Positive", positive)
col3.metric("😡 Negative", negative)
col4.metric("😐 Neutral", neutral)

st.markdown("---")


# ---------------- SMART INSIGHTS ----------------
st.subheader("🧠 Smart Insights")

# Calculate counts
total = len(df)
positive = len(df[df["sentiment_result"] == "positive"])
negative = len(df[df["sentiment_result"] == "negative"])
neutral = len(df[df["sentiment_result"] == "neutral"])

# Avoid division error
if total > 0:
    pos_pct = (positive / total) * 100
    neg_pct = (negative / total) * 100
    neu_pct = (neutral / total) * 100
else:
    pos_pct = neg_pct = neu_pct = 0

insights = []

# Insight 1: Majority sentiment
if pos_pct > neg_pct and pos_pct > neu_pct:
    insights.append(f"✅ Majority sentiment is Positive ({pos_pct:.1f}%)")
elif neg_pct > pos_pct and neg_pct > neu_pct:
    insights.append(f"❌ Majority sentiment is Negative ({neg_pct:.1f}%)")
else:
    insights.append(f"⚖️ Neutral sentiment dominates ({neu_pct:.1f}%)")

# Insight 2: Negative spike warning
if neg_pct > 40:
    insights.append("🚨 High negative sentiment detected!")

# Insight 3: Positive dominance
if pos_pct > 60:
    insights.append("🔥 Strong positive sentiment trend!")

# Insight 4: Neutral dominance
if neu_pct > 50:
    insights.append("😐 Conversations are mostly neutral")

# Insight 5: Trending word
from collections import Counter
from wordcloud import STOPWORDS

stopwords = set(STOPWORDS)

words = [
    word for word in " ".join(df["clean_text"].dropna()).split()
    if word.lower() not in stopwords and len(word) > 4
]

if words:
    top_word = Counter(words).most_common(1)[0][0]
    insights.append(f"🔥 Trending topic: {top_word}")

# Display insights
for insight in insights:
    st.markdown(f"- {insight}")


# ---------------- ALERT SYSTEM ----------------

st.subheader("🚨 Alerts")

alert_triggered = False

# Alert 1: High negative sentiment
if neg_pct > 40:
    
    st.error("🚨 ALERT: High negative sentiment detected!")
    alert_triggered = True

# Alert 2: Sudden imbalance
if abs(pos_pct - neg_pct) > 50:
    st.warning("⚠️ Large imbalance between sentiments!")

# Alert 3: Very low activity
if total < 100:
    st.info("ℹ️ Low data volume detected")

# If no alerts
if not alert_triggered:
    st.success("✅ System stable: No major issues detected")



# ---------------- SENTIMENT CHART ----------------
st.subheader("📊 Sentiment Analysis Overview")

sentiment_count = df["sentiment_result"].value_counts().reset_index()
sentiment_count.columns = ["sentiment", "count"]

col1, col2 = st.columns(2)

with col1:
    fig_bar = px.bar(
        sentiment_count,
        x="sentiment",
        y="count",
        color="sentiment",
        color_discrete_map={
            "positive": "#00F5D4",
            "negative": "#FF6B6B",
            "neutral": "#FFD166"
        }
    )
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )
    st.plotly_chart(fig_bar, width="stretch")

with col2:
    fig_pie = px.pie(
        sentiment_count,
        names="sentiment",
        values="count",
        hole=0.4,
        color_discrete_map={
            "positive": "#00F5D4",
            "negative": "#FF6B6B",
            "neutral": "#FFD166"
        }
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )
    st.plotly_chart(fig_pie, width="stretch")

st.markdown("---")

# ---------------- SEARCH ----------------
st.subheader("🔍 Search Tweets")

search = st.text_input("Type keyword...")

if search:
    filtered = df[df["clean_text"].str.contains(search, case=False)]
    st.dataframe(filtered.head(20))

# ---------------- TOP WORDS ----------------
st.subheader("🔥 Top Trending Words")

words = " ".join(df["clean_text"].dropna()).split()
common_words = Counter(words).most_common(10)

words_df = pd.DataFrame(common_words, columns=["word", "count"])

fig_words = px.bar(
    words_df,
    x="word",
    y="count",
    color="count",
    color_continuous_scale="Teal"
)

fig_words.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig_words, width="stretch")

st.markdown("---")

# ---------------- WORD CLOUD ----------------
st.subheader("☁️ Word Cloud")

text_data = df["clean_text"].dropna().astype(str)
text_data = text_data[text_data.str.len() > 2]

combined_text = " ".join(text_data)

if combined_text.strip() == "":
    st.warning("No data for word cloud")
else:
    wordcloud = WordCloud(
        width=900,
        height=400,
        background_color="black",
        colormap="viridis",
        stopwords=set(STOPWORDS)
    ).generate(combined_text)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud)
    ax.axis("off")
    st.pyplot(fig)

st.markdown("---")

# ---------------- DATA TABLE ----------------
st.subheader("📄 Data Preview")
st.dataframe(df.head(50))


# ---------------- REPORT GENERATOR ----------------
st.markdown("## 🧾 Generate Report")

if st.button("📄 Generate Report"):

    # Recalculate values
    total = len(df)
    positive = len(df[df["sentiment_result"] == "positive"])
    negative = len(df[df["sentiment_result"] == "negative"])
    neutral = len(df[df["sentiment_result"] == "neutral"])

    if total > 0:
        pos_pct = (positive / total) * 100
        neg_pct = (negative / total) * 100
        neu_pct = (neutral / total) * 100
    else:
        pos_pct = neg_pct = neu_pct = 0

    # Generate insights again
    insights = []

    if pos_pct > neg_pct and pos_pct > neu_pct:
        insights.append(f"Majority sentiment is Positive ({pos_pct:.1f}%)")
    elif neg_pct > pos_pct and neg_pct > neu_pct:
        insights.append(f"Majority sentiment is Negative ({neg_pct:.1f}%)")
    else:
        insights.append(f"Neutral sentiment dominates ({neu_pct:.1f}%)")

    if neg_pct > 40:
        insights.append("High negative sentiment detected")

    if pos_pct > 60:
        insights.append("Strong positive sentiment trend")

    # Create report text
    report = f"""
SOCIAL MEDIA SENTIMENT ANALYSIS REPORT
--------------------------------------

Total Tweets: {total}

Positive: {positive} ({pos_pct:.2f}%)
Negative: {negative} ({neg_pct:.2f}%)
Neutral: {neutral} ({neu_pct:.2f}%)

INSIGHTS:
"""

    for ins in insights:
        report += f"- {ins}\n"

    # Download button
    st.download_button(
        label="⬇️ Download Report",
        data=report,
        file_name="sentiment_report.txt",
        mime="text/plain"
    )