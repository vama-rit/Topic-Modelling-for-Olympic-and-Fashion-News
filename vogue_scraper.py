#!/usr/bin/env python
# coding: utf-8

# In[32]:


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

"""
1) [5 points] Choose one or more news websites to analyze, such as news.yahoo.com, www.cnn.com, 
or www.aljazeera.com (we will make no assumptions about your political affiliations based on your 
choice of source. You may also use specialty sites such as www.people.com or www.espn.com. 
Indicate your preference in the spreadsheet located here (you may not choose a source that another 
group has already chosen): 
https://docs.google.com/spreadsheets/d/14mWBrlU_xn5vnF8JZLlJUDbAB3T0NZfUsUkPyeyzGhE/edit#gid=0
"""
# request page using home html
mainSite = "https://www.vogue.com/fashion?us_site=y/"

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
n = 100

# json file to store articles
filenameArticle = 'articles_vogue.json'

# initailly should be empty file
with open(filenameArticle, mode='w', encoding='UTF-8') as f:
    json.dump([], f)

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

        if("/article/" in articleLink):
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
                    json.dump(data, f)

# """
# 4) [10 points] Add an additional field to articles.json, called "preprocessed." This should take the body field and 
# remove stop words, lemmatize and stem (if appropriate) and/or removing frequent, infrequent words.

# 5) [5 points] Call the script that performs 1-4 scraper.py and place in the root directory of your repo. You should 
# indicate in the comments clearly where you perform each of the tasks listed above.
# """

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
# the index of the word we are changing
index = 0

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
    # add the new sentence to the file
    with open(filenameArticle, mode='r+', encoding='UTF-8') as f:
        data = json.load(f)
        # add the text of the file
        data[index]['preprocessed']= preprocessPost
        f.seek(0)
        json.dump(data, f)

    filePost.close()
    # increment to next value
    index+=1
