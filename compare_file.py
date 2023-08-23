import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Read the content of the first file
with open('/home/jerry/zap/uploaded/5_iottalk_tw/iottalk-v1-master_da_Bulb_index.html', 'r') as file:
    file1_content = file.read()

# Read the content of the second file
with open('/home/jerry/zap/uploaded/5_iottalk_tw/iottalk-v1-master_lib_templates_remotecontrol.html', 'r') as file:
    file2_content = file.read()

# Initialize the TF-IDF vectorizer
vectorizer = TfidfVectorizer(tokenizer=word_tokenize, stop_words=stopwords.words('english'))

# Preprocess and vectorize the content of the first file
file1_vector = vectorizer.fit_transform([file1_content])

# Preprocess and vectorize the content of the second file
file2_vector = vectorizer.transform([file2_content])

# Calculate the cosine similarity between the vectors
similarity_score = nltk.cluster.util.cosine_distance(file1_vector.toarray()[0], file2_vector.toarray()[0])

# Print the similarity score
print(f"Similarity Score: {similarity_score}")

