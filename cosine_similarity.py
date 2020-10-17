import re, math
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string
nltk.download('stopwords')

stop = set(stopwords.words('english'))

exclude = set(string.punctuation)

WORD = re.compile(r'\w+')

# Removal of Punctuation
def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

# Removal of StopWords
def removeStopWords(text):
    return " ".join([i for i in text.lower().split() if i not in stop])

# Removal of Punctuation
# Only Cosine Similarity
def get_cosine(text1, text2):
    # Reference - https://en.wikipedia.org/wiki/Cosine_similarity

    vector1 = text_to_vector(removeStopWords(text1).lower())
    vector2 = text_to_vector(removeStopWords(text2).lower().replace("<b>","").replace("</b>",""))
    
    intersection = set(vector1.keys()) & set(vector2.keys())
    numerator = sum([vector1[x] * vector2[x] for x in intersection])
    
    sum1 = sum([vector1[x]**2 for x in vector1.keys()])
    sum2 = sum([vector2[x]**2 for x in vector2.keys()])
    
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        print("denominator : ", denominator)
        return 0.0
    else:
        return float(numerator) / denominator

