# perform topic modeling
import gensim
from gensim.corpora import Dictionary
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# read the json files
import json

# plot graphs
import matplotlib.pyplot as plt
import numpy as np

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
