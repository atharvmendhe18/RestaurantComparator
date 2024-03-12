from transformers import pipeline
import pandas as pd

pipe_SentimentAnalysis = pipeline(
    "text-classification", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", return_all_scores = True, device = -1)

pipe_ReviewSummarization = pipeline("summarization", model="Falconsai/text_summarization")

def get_sentiment_and_summary(res_name):
    df = pd.read_csv(f"C:\Desktop\Codes\Zomato_comparator\Database\{res_name}_reviews.csv", encoding='utf-8')
    df.dropna(axis=0, inplace=True)
    sentiments = []
    final_sentiment = None
    total_reviews = ""
    for review in df['Review']:
        sentiments.append(pipe_SentimentAnalysis(review)[0])
        total_reviews += f" {review}"

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
        final_sentiment=  "Positive"
    else:
        final_sentiment = "Negative"      
    
    summary = pipe_ReviewSummarization(total_reviews)

    return {"res_name": res_name,"sentiment": final_sentiment, "summary": summary}

