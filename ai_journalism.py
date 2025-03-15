import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import json
import random
import logging
from googlenews import GoogleNews

nltk.download('punkt')
nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)

class NewsScraper:
    def __init__(self, query):
        self.query = query
        self.google_news = GoogleNews()

    def fetch_articles(self):
        self.google_news.search(self.query)
        articles = self.google_news.results(sort=True)
        return articles

class ArticleProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_article(self, article):
        text = article['content']
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = text.lower()
        words = word_tokenize(text)
        words = [word for word in words if word not in self.stop_words]
        return ' '.join(words)

class SentimentAnalyzer:
    def __init__(self):
        self.model = make_pipeline(CountVectorizer(), MultinomialNB())

    def train_model(self, data, labels):
        self.model.fit(data, labels)

    def predict_sentiment(self, text):
        return self.model.predict([text])

class DataCollector:
    def collect_data(self, articles):
        data = []
        for article in articles:
            processed_text = ArticleProcessor().clean_article(article)
            data.append({
                'title': article['title'],
                'description': processed_text,
                'url': article['link']
            })
        return data

class AIJournalism:
    def __init__(self):
        self.scraper = NewsScraper("latest news")
        self.analyzer = SentimentAnalyzer()

    def run(self):
        logging.info("Fetching articles...")
        articles = self.scraper.fetch_articles()
        collector = DataCollector()
        data = collector.collect_data(articles)

        # Sample synthetic data for training
        synthetic_data = [
            ("I love sunny days", "positive"),
            ("I hate rain", "negative"),
            ("The weather is great", "positive"),
            ("I am feeling sad today", "negative"),
            ("What a beautiful morning", "positive"),
        ]
        texts, labels = zip(*synthetic_data)
        self.analyzer.train_model(texts, labels)

        logging.info("Analyzing Sentiments...")
        for item in data:
            sentiment = self.analyzer.predict_sentiment(item['description'])
            item['sentiment'] = sentiment[0]

        logging.info("Generated Articles with Sentiments:")
        for item in data:
            logging.info(f"Title: {item['title']}, Sentiment: {item['sentiment']}, URL: {item['url']}")

if __name__ == "__main__":
    journalism = AIJournalism()
    journalism.run()