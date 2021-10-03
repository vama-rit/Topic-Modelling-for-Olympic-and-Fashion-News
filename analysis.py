import gensim

"""
6) [10 points] Using gensim, perform topic modeling on your data for between 10 and 30 topics. For each topic model, you 
should measure its performance using perplexity, Bayesian information criterion, and/or coherence. For each measurement, 
use matplotlib to graph each measure for each of the number of topics used. [10 points] A pdf of this graph(s) should 
appear in your project report.

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