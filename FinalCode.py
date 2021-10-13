# make https requests
import requests
# import beautifulsoup
from bs4 import BeautifulSoup
# file
import json
# natrual language processing
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import spacy
sp = spacy.load('en_core_web_sm')

import operator
import string
import os
import collections
from collections import Counter

# perform topic modeling
import gensim
from gensim.corpora import Dictionary
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# plot graphs
import matplotlib.pyplot as plt
import numpy as np

import re
import pandas as pd


"""
1) [5 points] Choose one or more news websites to analyze, such as news.yahoo.com, www.cnn.com, 
or www.aljazeera.com (we will make no assumptions about your political affiliations based on your 
choice of source. You may also use specialty sites such as www.people.com or www.espn.com. 
Indicate your preference in the spreadsheet located here (you may not choose a source that another 
group has already chosen): 
https://docs.google.com/spreadsheets/d/14mWBrlU_xn5vnF8JZLlJUDbAB3T0NZfUsUkPyeyzGhE/edit#gid=0
"""

# Scraping website 1 - https://www.cbssports.com/olympics/

# request page using home html
mainSite = "https://www.cbssports.com/olympics/"

"""
2) [5 points] Write a script using beautifulsoup that will download at least 100 full articles from the 
site. The script should not hardcode any sites other than the homepage, and it should be able to run 
at any time and collect the most recent articles.
3) [5 points] Place the articles retrieved into a file called articles.json in the root level of your github repo. 
Each line of this file should contain the data of one article, with the following fields: title, author, date, and body. 
If any of these cannot be found, use "None." however there must be a body, and this should be the entire text of the 
main body, with all hyperlinks and media removed. It must be at least 100 words long.
"""
# number of articles we wish to collect (groups of 9 so round down)
n = 70

# json file to store articles
filenameArticle = 'articles.json'

# initailly should be empty file
with open(filenameArticle, mode='w', encoding='UTF-8') as f:
    json.dump([], f, indent = 1)

for i in range(1, n//9+1):
    # next set of 9 articles we wish to scrape
    nextSite = mainSite+str(i)
    page = requests.get(nextSite)

    # create beautifulsoup parser
    soup = BeautifulSoup(page.content, "html.parser")

    # iterate through articles on first page
    for articles in soup.find_all('h5', class_="article-list-pack-title col-4"):
        # find the link to the next article.
        # Must give header to cbs sports
        articleLink = "https://www.cbssports.com"+articles.a['href']
        articlePage = requests.get(articleLink)
        articleSoup = BeautifulSoup(articlePage.content, 'html.parser')

        article = {}

        # add link of article
        article["link"] = articleLink

        # add title of article
        title = articleSoup.find('h1', class_="Article-headline")
        if(not title == None):
            article["title"] = title.text.strip()
        else:
            article["title"] = None


        # add subheader of title
        subheader = articleSoup.find('h2', class_="Article-subline")
        if(not subheader == None):
            article['subtitle'] = subheader.text.strip()
        else:
            article['subtitle'] = None

        # article info (title, date published, time published, readtime)
        otherInfo = articleSoup.find("div", class_="ArticleAuthor")
        # author
        author = otherInfo.find('span', class_="ArticleAuthor-nameText").text
        if(not author == None):
            article['author'] = author.strip()
        else:
            article['author'] = None
        # time posted
        posted = otherInfo.find('time', class_="TimeStamp")['data-date-time-ago-options']
        if(posted == None):
            article['date'] = None
            article['time'] = None
        else:
            postedDict = json.loads(posted)
            date = postedDict["month"]+"/"+postedDict["day"]+"/"+postedDict["year"]
            time = postedDict["hour"]+":"+postedDict["min"]
            article['date'] = date
            article['time'] = time

        # content
        content = articleSoup.find('div', class_="Article-bodyContent")
        # sections
        sections = []
        # get top three headers
        for sectionIndex in range(0, 4):
            headerType = 'h'+str(sectionIndex)
            sectionNames = content.find_all(headerType)
            # increment through the sections
            for s in sectionNames:
                # only want text paragraphs
                if (s.attrs == {} and len(s.text)>0):
                    sections.append(s.text.strip())
        if(len(sections) == 0):
            article['section'] = None
        else:
            article['section'] = sections
        # paragraphs
        paragraphs = content.find_all('p')
        writtenContent = ""
        prefix = ""
        # convert into one line
        for p in paragraphs:
            # only want text paragraphs and paragraphs containing text
            if(p.attrs == {} and len(p.text.strip())>0):
                # only want 'p'
                writtenContent = writtenContent + prefix +  p.text.strip()
                prefix = " "
        article['body'] = writtenContent
        # lists
        lists = content.find_all('ul')
        listElements = []
        # increment through the lists
        for l in lists:
            nextList = l.find_all('li')
            for element in nextList:
                listElements.append(element.text)
        if(len(listElements)==0):
            article['list'] = None
        else:
            article['list'] = listElements

        # check body is greater then 100 characters
        if(len(writtenContent.split(" ")) > 100):
            print(article)
            with open(filenameArticle, 'r+') as f:
                data = json.load(f)
                data.append(article)
                f.seek(0)
                json.dump(data, f, indent = 1)

# Scraping website 2 - https://www.vogue.com
mainSite = "https://www.vogue.com/fashion?us_site=y/"

visitedLinks = []
for i in range(1, n//9+1):
    # next set of 9 articles we wish to scrape
    nextSite = mainSite+str(i)
    page = requests.get(nextSite)
    
    # create beautifulsoup parser
    soup = BeautifulSoup(page.content, "html.parser")
    # iterate through articles on first page
    for articles in soup.find_all('a', class_="summary-item__hed-link"):
        # find the link to the next article.
        # Must give header to cbs sports
        articleLink = "https://www.vogue.com"+articles['href']
        
        if("/article/" in articleLink and articleLink not in visitedLinks):
            visitedLinks.append(articleLink)
            articlePage = requests.get(articleLink)
            articleSoup = BeautifulSoup(articlePage.content, 'html.parser')

            article = {}

            # add link of article
            article["link"] = articleLink
            print(article["link"])
            # add title of article
            title = articleSoup.find('h1', class_="content-header__row content-header__hed")
            if(not title == None):
                article["title"] = title.text.strip()
            else:
                article["title"] = None

            author = articleSoup.find("span", class_ = "byline__name")
            if(not author == None):
                article['author'] = author.text.strip()
            else:
                article['author'] = None

            # time posted
            posted = articleSoup.find('time', class_="content-header__publish-date")
            if(posted == None):
                article['date'] = None
                article['time'] = None
            else:

                article['date'] = posted.text
                article['time'] = None

            # content
            content = articleSoup.find('div', class_="article__body")
            # sections
            sections = []
            # get top three headers
            for sectionIndex in range(0, 4):
                headerType = 'h'+str(sectionIndex)
                sectionNames = content.find_all(headerType)
                # increment through the sections
                for s in sectionNames:
                    # only want text paragraphs
                    if (s.attrs == {} and len(s.text)>0):
                        sections.append(s.text.strip())
            if(len(sections) == 0):
                article['section'] = None
            else:
                article['section'] = sections
            # paragraphs
            paragraphs = content.find_all('p')
            writtenContent = ""
            prefix = ""
            # convert into one line
            for p in paragraphs:
                # only want text paragraphs and paragraphs containing text
                if(p.attrs == {} and len(p.text.strip())>0):
                    # only want 'p'
                    writtenContent = writtenContent + prefix +  p.text.strip()
                    prefix = " "
            article['body'] = writtenContent
            # lists
            lists = content.find_all('ul')
            listElements = []
            #increment through the lists
            for l in lists:
                nextList = l.find_all('li')
                for element in nextList:
                    listElements.append(element.text)
            if(len(listElements)==0):
                article['list'] = None
            else:
                article['list'] = listElements
            # check body is greater then 100 characters
            if(len(writtenContent.split(" ")) > 100):
                print(article)
                with open(filenameArticle, 'r+') as f:
                    data = json.load(f)
                    data.append(article)
                    f.seek(0)
                    json.dump(data, f, indent = 1)
                    
# Scraping website 3 - https://www.abcnews.com


"""
4) [10 points] Add an additional field to articles.json, called "preprocessed." This should take the body field and 
remove stop words, lemmatize and stem (if appropriate) and/or removing frequent, infrequent words.
5) [5 points] Call the script that performs 1-4 scraper.py and place in the root directory of your repo. You should 
indicate in the comments clearly where you perform each of the tasks listed above.
"""
# open the file to read from
filePost = open(filenameArticle,mode='r', encoding='UTF-8')
# get the data and store in dictionary
dataArticles = json.load(filePost)

# create the set of stopwords
nltk.download('stopwords')
englishStopWords = list(stopwords.words('english'))

# use natural language toolkit lemmatizer
wnl = WordNetLemmatizer()
punctuation =  '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

# keep track of all words, useful in removing frequent words
articleWords = []
# keep track of sentences
preprocessArticles = []

# iterate through the text
for postText in dataArticles:
    # grab the text, change to lower case, and tokenize it
    body = postText['body'].lower()
    link = postText['link']
    postTolkens = sp(body) #word_tokenize(body)

    # create a sentence of words
    preprocessPost = ""
    prefix = ""

    # filter so no longer contains the stopping words
    for word in postTolkens:
        # get rid of stopwords and find stem or word
        if (not word.text.replace("'", "") in englishStopWords
                # get rid of n't, which was a problem when tokenizing
                and not word.text.replace("'", "") in ["nt"]):
            # get rid of punctuation
            onlyPunctuation = True
            for c in word.text:
                if(not c in string.punctuation):
                    onlyPunctuation = False
                    break
            if(not onlyPunctuation):
                preprocessPost += prefix + (word.lemma_)
                prefix = " "

                # add the word to the list of words
                articleWords.append(word.lemma_)
    preprocessArticles.append(preprocessPost)
filePost.close()

# number of most frequent words to remove
numTopics = 100

# remove frequent words
countWords = Counter(articleWords)
highestFrequence = countWords.most_common(numTopics)
highestFrequenceWord = []
# convert to a list that is easy to check if contains word
for wordData in highestFrequence:
    highestFrequenceWord.append(wordData[0])

# iterate through the preprocess articles
for i in range(0, len(preprocessArticles)):
    body = preprocessArticles[i]

    # create a sentence of words
    preprocessPost = ""
    prefix = ""

    # filter so no longer contains the frequent words
    for word in body.split():
        # get rid of freqentWords
        if (not word.replace("'", "") in highestFrequenceWord):
            preprocessPost += prefix + (word)
            prefix = " "
    #print(preprocessPost)

    # add the new sentence to the file
    with open(filenameArticle, mode='r+', encoding='UTF-8') as f:
        data = json.load(f)
        # add the text of the file
        data[i]['preprocessed'] = preprocessPost
        f.seek(0)
        json.dump(data, f, indent = 1)
        
"""
6) [10 points] Using gensim, perform topic modeling on your data for between 10 and 30 topics. For each topic model, you 
should measure its performance using perplexity, Bayesian information criterion, and/or coherence. For each measurement, 
use matplotlib to graph each measure for each of the number of topics used. 
[10 points] A pdf of this graph(s) should appear in your project report.
"""
def createTopicModes():
    # open the file to read from
    file = open("articles.json", mode = 'r', encoding='UTF-8')
    # get the data and store in dictinary
    data = json.load(file)

    # keep track of preprocessed words
    preprocessText = []
    for article in data:
        preprocessText.append(article["preprocessed"].split())

    # create a bag of words
    bagOfWords = Dictionary(preprocessText)
    corpus = []
    for text in preprocessText:
        new = bagOfWords.doc2bow(text)
        corpus.append(new)

    # keep track of number of topics and coherence
    numTopics = []
    perplexities = []
    coherences = []

    # keep track of the actual topic models
    topicModels = []

    # iterate through the different number of topics
    for nt in range(10,31):
        # create topic model
        topicModel = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=bagOfWords, num_topics=nt, per_word_topics =True)
        topicModels.append(topicModel)

        # calculate the perplexity, lower better
        p = topicModel.log_perplexity(corpus)
        perplexities.append(p)
        # calculate the coherence value, higher better
        cm = CoherenceModel(model=topicModel, corpus=corpus, coherence='u_mass')
        c = cm.get_coherence()
        # add the number of topics and coherence to the lists
        numTopics.append(nt)
        coherences.append(c)

    # plot the values
    # perpelexity
    filePerplexity="plotPerplexity.svg"
    plt.plot(numTopics, perplexities)
    # add title and labels to axis
    #TODO come up with better title
    plt.title("Perplexity over change of number of topics")
    plt.xlabel("Number of topics")
    plt.ylabel("Perplexity")
    # space the x axis
    plt.xticks(np.arange(10, 31, 2))
    # store the plot
    plt.savefig(filePerplexity)
    plt.close()

    # coherence
    fileCoherence="plotCoherence.svg"
    plt.plot(numTopics, coherences)
    # add title and labels to axis
    #TODO come up with better title
    plt.title("Coherence Values over change of number of topics")
    plt.xlabel("Number of topics")
    plt.ylabel("Coherence value")
    # space the x axis
    plt.xticks(np.arange(10, 31, 2))
    # store the plot
    plt.savefig(fileCoherence)
    plt.close()

    return topicModels


"""
7) [10 points] Choose the optimal number of topics based on your graph. Explain in your report how you came to that 
conclusion.
8) [10 points] In your report, create a table (or multiple tables if you cannot fit it in a single table) with one 
column per topic and a listing of the 20 most likely words in the rows, in descending order. [5 oints] Additionally each 
column should have two header rows, one for the topic number and the other for a name you give it, based on what the 
most likely words suggest. If you cannot think of a name for a give column, write "unclear." You should use pandas to 
help produce the LaTeX for this table.
9) [10 points] Project your articles into the topic model. For each topic, find the article where that topic is the most 
likely. [10 points] Then in your report, list each topic number followed by the name and date of the article you found.
"""
f = open("topics.txt", "r+")
f.truncate(0)

def main():
    # find the best topic model
    topicModels = createTopicModes()

    # print the topics
    for topicModel in topicModels:
        f.write("Topic of size : "+str(topicModel.num_topics)+"\n")
        for topic in topicModel.print_topics(num_words=20):
            f.write(str(topic)+"\n")
        f.write("\n")
    f.close()

if __name__ == '__main__':
	main()

lines=[]
with open('topics.txt') as file:
    next(file)
    for line in file:
        lines.append(re.split(';|,|\+|\)|\n', line))

for i in lines:
    for j in range(len(i)):
        i[j]=re.sub('[(\\\\!@\'#$/\" "]', '', i[j])
        if "*" in i[j]:
            i[j]=i[j].partition("*")[2]
    i.pop(0)
    i.remove('')
    if '' in i:
        i.remove('')

dictlist={i[len(i)-1]: i[0:(len(i)-1)] for i in lines}
df=pd.DataFrame.from_dict(dictlist,orient='index').transpose()
df.to_csv(r'topic_table.csv', index = False)
print(df.to_latex(index=True)) 

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
