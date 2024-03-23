from transformers import pipeline
import pandas as pd

pipe_SentimentAnalysis = pipeline(
    "text-classification", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", return_all_scores = True, device = -1)


def get_sentiment(res_name):
    df = pd.read_csv(f"C:\Desktop\Codes\Zomato_comparator\Database\{res_name}_reviews.csv", encoding='utf-8')
    df.dropna(axis=0, inplace=True)
    sentiments = []
    for review in df['Review']:
        sentiments.append(pipe_SentimentAnalysis(review)[0])

    sentiment_dict = {
    'positive': 0,
    'negative': 0,
    }

    for sentiment in sentiments:
        if sentiment[0]['score'] > 0.4:
            sentiment_dict['positive'] += 1
        else:
            sentiment_dict['negative'] += 1  
        
    if sentiment_dict['positive'] > sentiment_dict['negative']:
        return "Positive"
    else:
        return "Negative"      
    

