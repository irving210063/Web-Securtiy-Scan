import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
nltk.download('stopwords')
nltk.download('punkt')
# Read the content of the first HTML file
with open('/home/jerry/zap/uploaded/5_iottalk_tw/iottalk-v1-master_da_Bulb_index.html', 'r') as file:
    file1_content = file.read()

# Read the content of the second HTML file
with open('/home/jerry/zap/uploaded/5_iottalk_tw/iottalk-v1-master_da_CHT_Dashboard_index_disable.html', 'r') as file:
    file2_content = file.read()

# Extract the textual content from the HTML files
def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ')
    return text

file1_text = extract_text(file1_content)
file2_text = extract_text(file2_content)

# Create a list to store the similarity scores
similarity_scores = []

# Initialize the TF-IDF vectorizer
vectorizer = TfidfVectorizer(tokenizer=word_tokenize, stop_words=stopwords.words('english'))

# Preprocess and vectorize the content of the first file
file1_vector = vectorizer.fit_transform([file1_text])

# Preprocess and vectorize the content of the second file
file2_vector = vectorizer.transform([file2_text])

# Calculate the cosine similarity between the vectors
similarity_score = nltk.cluster.util.cosine_distance(file1_vector.toarray()[0], file2_vector.toarray()[0])

# Print the similarity score
print(f"Similarity Score: {similarity_score}")
