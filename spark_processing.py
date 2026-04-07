import os
os.environ["JAVA_HOME"] = "C:\\Program Files\\Eclipse Adoptium\\jdk-11.0.30.7-hotspot"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace

# Create Spark session
spark = SparkSession.builder \
    .appName("Sentiment Analysis") \
    .getOrCreate()

# Load dataset
df = spark.read.csv("data/tweets.csv", inferSchema=True)

# Assign proper column names
columns = ["sentiment", "id", "date", "query", "user", "text"]
df = df.toDF(*columns)

# Show original data
print("=== ORIGINAL DATA ===")
df.show(5)

# 🔹 DATA CLEANING
clean_df = df.withColumn("clean_text", lower(col("text")))

# Remove URLs
clean_df = clean_df.withColumn(
    "clean_text",
    regexp_replace("clean_text", "http\\S+|www\\S+", "")
)

# Remove mentions (@username)
clean_df = clean_df.withColumn(
    "clean_text",
    regexp_replace("clean_text", "@\\w+", "")
)

# Remove hashtags (#tag → tag)
clean_df = clean_df.withColumn(
    "clean_text",
    regexp_replace("clean_text", "#", "")
)

# Remove special characters
clean_df = clean_df.withColumn(
    "clean_text",
    regexp_replace("clean_text", "[^a-zA-Z\\s]", "")
)

# Show cleaned data
print("=== CLEANED DATA ===")
clean_df.select("text", "clean_text").show(5)



from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from textblob import TextBlob

# Sentiment function
def get_sentiment(text):
    if text is None:
        return "neutral"
    
    polarity = TextBlob(text).sentiment.polarity
    
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"

# Convert to Spark UDF
sentiment_udf = udf(get_sentiment, StringType())

# Apply sentiment analysis
result_df = clean_df.withColumn("sentiment_result", sentiment_udf(col("clean_text")))

print("=== SENTIMENT RESULTS ===")
result_df.select("clean_text", "sentiment_result").show(10)





from pyspark.sql.functions import explode, split

# Split sentences into words
words_df = result_df.withColumn(
    "word",
    explode(split(col("clean_text"), " "))
)

# Remove empty words
words_df = words_df.filter(col("word") != "")

# Count frequency
word_count = words_df.groupBy("word").count()

# Show top 10 trending words
print("=== TRENDING WORDS ===")
word_count.orderBy(col("count").desc()).show(10)


print("=== SENTIMENT DISTRIBUTION ===")
result_df.groupBy("sentiment_result").count().show()

# Convert Spark DataFrame to Pandas
pandas_df = result_df.select("clean_text", "sentiment_result").toPandas()

# Save as single CSV (simple way)
pandas_df.to_csv("processed_data.csv", index=False)

print("Data saved as processed_data.csv")