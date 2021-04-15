import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
import operator

from pyignite import Client
import json

import sys

from ignite import IgniteData

class ObjectiveExtractor:

    txt = ""
    stop_words = set(stopwords.words('english'))
    
    def __init__(self, IDK, txt, objective, ITEMS, GREETING_INPUTS, END_GREETING_INPUTS):
        self.IDK = IDK
        self.txt = txt
        self.objective = objective
        self.items = ITEMS 
        self.GREETING_INPUTS = GREETING_INPUTS
        self.END_GREETING_INPUTS = END_GREETING_INPUTS

        self.Ignite = IgniteData()

    def update_txt(self, txt):
        self.txt = txt

    def get_objectives(self):
        return self.objective

    def is_done(self):
        return self.objective["completed"]

    def pos_tag(self):
        tokenized = sent_tokenize(self.txt)
        tg = list()
        for i in tokenized:

            # Word tokenizers is used to find the words 
            # and punctuation in a string
            wordsList = nltk.word_tokenize(i)

            # removing stop words from wordList
            wordsList = [w for w in wordsList if not w in stop_words] 

            #  Using a Tagger. Which is part-of-speech 
            # tagger or POS-tagger. 
            tagged = nltk.pos_tag(wordsList)
            tg.extend(tagged)
        return tg

    def sentiment_score(self, txt):
        sia = SentimentIntensityAnalyzer()
        return sia.polarity_scores(txt)

    def cosine(self, X, Y):
        # tokenization
        X_list = word_tokenize(X) 
        Y_list = word_tokenize(Y)

        # sw contains the list of stopwords
        sw = stopwords.words('english') 
        l1 =[];l2 =[]

        # remove stop words from the string
        X_set = {w for w in X_list if not w in sw} 
        Y_set = {w for w in Y_list if not w in sw}

        # form a set containing keywords of both strings 
        rvector = X_set.union(Y_set) 
        for w in rvector:
            if w in X_set: l1.append(1) # create a vector
            else: l1.append(0)
            if w in Y_set: l2.append(1)
            else: l2.append(0)
        c = 0

        # cosine formula 
        for i in range(len(rvector)):
                c+= l1[i]*l2[i]
        cosine = c / float((sum(l1)*sum(l2))**0.5)
        return cosine
    
    def product_option(self, buy):
        buy = False
        XL = self.items
        Y = self.txt
        cos_l = list()
        for pos, X in enumerate(XL): 
            cos_l.append((X, self.cosine(X, Y), pos))
    #     print(cos_l)
        sorted_cos_l = sorted(cos_l, key=operator.itemgetter(1), reverse=True)
        
        mx = sorted_cos_l[0][1] - 0.25
        choice = list()
        for i in sorted_cos_l:
            if (i[0] == "new installation" or i[0] == "buy x") and i[1] >= 0.5:
                buy = True    
                continue
            if i[1] >= 0.7:
                choice.append(i)
                break
            elif i[1] >= mx:
                choice.append(i)
    #     print(choice, len(choice))
        return choice, buy


    def extract(self):
        if self.objective["stage"] == 0 or self.objective["stage"] == 1:
            if self.txt in self.GREETING_INPUTS:
                pass
                # out = "Hi, How can I help you?"
                # print(out)
            elif self.txt in self.END_GREETING_INPUTS:
                # out = "Thank you for using our service"
                # print(out)
                self.objective["completed"] = True
                return (True,)
            else:
                cho, buy = self.product_option(self.txt.lower())
                self.objective["new_service"] = buy
                self.objective["stage"] = 1
                self.Ignite.putData(self.objective,  self.IDK)
                if len(cho) > 0:
                    if len(cho) == 1:
                        self.objective["complaint"] = cho[0][0]
                        self.objective["stage"] = 2
                        self.Ignite.putData(self.objective,  self.IDK)
                        return (False, )
                    elif len(cho) > 1:
                        print(cho)
                        return False, cho
                else:
                    # out = "I couldn't recognize service request"
                    pass
        elif self.objective["stage"] == 2: 
            score = self.sentiment_score(self.txt)
            if score["neg"] >= 0.5:
                self.objective["desc"] = "None"
            else:
                self.objective["desc"] = self.txt
            self.objective["stage"] = 3
            self.Ignite.putData(self.objective,  self.IDK)
            return (False, )

        elif self.objective["stage"] == 3: 
            # print("Can you please provide more description of problem?")
            # self.txt = input()
            score = self.sentiment_score(self.txt)
            if score["neg"] >= 0.5:
                self.objective["addr"] = "None"
            else:
                self.objective["addr"] = self.txt
            self.objective["stage"] = 4
            self.Ignite.putData(self.objective,  self.IDK)
            return (False, )

        elif self.objective["stage"] == 4: 
            # print("Can you please provide more description of problem?")
            # self.txt = input()
            score = self.sentiment_score(self.txt)
            if score["neg"] >= 0.5:
                self.objective["mob"] = "None"
            else:
                self.objective["mob"] = self.txt
            self.objective["stage"] = 5
            self.Ignite.putData(self.objective,  self.IDK)
            return (False, )

        elif self.objective["stage"] == 5: 
            # print("Can you please provide more description of problem?")
            # self.txt = input()
            score = self.sentiment_score(self.txt)
            if score["neg"] >= 0.5:
                self.objective["landmark"] = "None"
            else:
                self.objective["landmark"] = self.txt
            self.objective["stage"] = 6
            self.Ignite.putData(self.objective,  self.IDK)
            return (False, )

        elif self.objective["stage"] == 6: 
            # print("Can you please provide more description of problem?")
            # self.txt = input()
            score = self.sentiment_score(self.txt)
            if score["neg"] >= 0.5:
                self.objective["confirm"] = False
                # out = "Thank you for using our service"
                # print(out)
            else:
                self.objective["confirm"] = True
            self.objective["completed"] = True
            self.objective["stage"] = 7
            self.Ignite.putData(self.objective,  self.IDK)
            return (True, )    

# ========================================= Testing ============================================

# objective = {
#         "stage": 0,
#         "new_service": False,
#         "complaint": "",
#         "desc": "",
#         "addr": "",
#         "mob": "",
#         # "loc": "",
#         # "lat": "",
#         # "long": "",
#         "landmark": "",
#         "confirm": "",
#         "completed": False
#     }


# GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
# END_GREETING_INPUTS = ("bye", "quit", "see you")

# PROD = [
#     'E Bike',
#     'E Trance +',
#     'Gorilla Fan',
#     'Gorilla Fan Pedestal Fan',
#     'Gorilla Fan Wall Mounted',
#     'Off Grid Solar Power Plant',
#     'On Grid Solar System',
#     'Super Fan A1',
#     'Super Fan V1',
#     'Super Fan X1',
#     'On Grid',
#     'Off Grid',
#     'E Vehicles',
#     'Energy Efficient & Renewable Energy Products',
#     'Water Heater',
#     'battery'
# ]

# ITEMS = PROD + ["New installation", "Buy x", "Cost of"]
# ITEMS = list(set(map(lambda x: x.lower(), ITEMS)))

# IDK = sys.argv[1]

# Ignite = IgniteData()
# try:
#     temp = Ignite.getData(IDK)
#     if temp.get("stage", 0) > 0:
#         objective = temp
# except:
#     pass

# txt = sys.argv[2]
# print("txt:", txt)
# obj = ObjectiveExtractor(IDK, txt, objective, ITEMS, GREETING_INPUTS, END_GREETING_INPUTS)
# done = obj.extract()
# print("Ignite:", Ignite.getData(IDK))

# if len(done) > 1:
#     print("Cho:", done[1])

# # if cho:
# #     print('\n'.join([x[0] for x in cho]))
# #     txt = input("enter choice")
# #     obj.update_txt(txt)
# #     obj.extract()
# #     print("Ignite:", Ignite.getData(IDK))

# # txt = input("enter desc")
# # obj.update_txt(txt)
# # obj.extract()
# # print("Ignite:", Ignite.getData(IDK))

# print("Class:", obj.get_objectives())

