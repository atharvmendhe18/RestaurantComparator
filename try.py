import csv
sentiment_and_summary_db = r"C:\Desktop\/Codes\Zomato_comparator\Database\/sentiment_and_summary_database.csv"
with open(sentiment_and_summary_db, 'w',newline='',encoding='utf-8') as write_sentiment:
    writer = csv.writer(write_sentiment)
    writer.writerow(['Name','Sentiment','Summary'])