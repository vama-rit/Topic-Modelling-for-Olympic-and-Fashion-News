import pandas as pd 
import json 

df = pd.read_csv('topic_table.csv')
topics = list(df.columns)
file = open('articles.json',mode='r', encoding='UTF-8')
articles = json.load(file)

for topic in topics:
    wordList = list(df[topic])
    maxCount = 0
    maxCountArticleName = ''
    maxCountArticleDate = ''
    for article in articles:
        count = 0
        preprocessed = article['preprocessed'].split(" ")
        for word in preprocessed:
            if word in wordList:
                count +=1
        if count > maxCount:
            maxCount = count 
            maxCountArticleName = article['title']
            maxCountArticleDate = article['date']
    print("------------------------------------------------------------")
    print("Topic : " + topic + "\n No. of occurences : " + str(maxCount) + "\n Article name : " + maxCountArticleName + "\n Article Date : " + maxCountArticleDate)
    
