import json
import nltk
import os
import csv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import time

# Download required NLTK resources (if not already)
def ensure_nltk_resources():
    """Ensure NLTK resources are downloaded."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Initialize required resources
ensure_nltk_resources()

class StudentChatBot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = LogisticRegression()
        self.inputs = []
        self.outputs = []
        self._load_dataset()
        self._train_model()

    def _load_dataset(self):
        """Load Q&A pairs from dataset.json."""
        dataset_file = 'dataset.json'
        if not os.path.exists(dataset_file):
            raise FileNotFoundError(f"{dataset_file} not found. Please ensure it's in the directory.")

        try:
            with open(dataset_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from {dataset_file}. Please check the file format.")

        # Parse the data
        for item in data:
            self.inputs.append(item.get('input'))
            self.outputs.append(item.get('output'))

    def _preprocess(self, text):
        """Preprocess text: tokenize, remove punctuation, and stopwords."""
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalnum()]  # Remove punctuation
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(filtered_tokens)

    def _train_model(self):
        """Train TF-IDF + Logistic Regression on the dataset."""
        if not self.inputs or not self.outputs:
            raise ValueError("Inputs and outputs are empty. Please ensure the dataset is loaded correctly.")

        processed_inputs = [self._preprocess(text) for text in self.inputs]
        X = self.vectorizer.fit_transform(processed_inputs)
        y = self.outputs
        self.classifier.fit(X, y)

    def get_response(self, user_input):
        """Generate response for given user input."""
        processed_input = self._preprocess(user_input)
        X = self.vectorizer.transform([processed_input])
        prediction = self.classifier.predict(X)
        response = prediction[0]
        self._log_conversation(user_input, response)
        return response

    def _log_conversation(self, user_input, response):
        """Log conversations to chat_log.csv with a timestamp."""
        log_file = 'chat_log.csv'
        file_exists = os.path.isfile(log_file)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

        try:
            with open(log_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['Timestamp', 'User Input', 'Chatbot Response'])
                writer.writerow([timestamp, user_input, response])
        except Exception as e:
            print(f"Error logging conversation: {e}")

# Initialize chatbot instance once
chatbot = StudentChatBot()

# Function to be imported in app.py
def get_bot_response(user_input):
    """Return chatbot's response based on user input."""
    return chatbot.get_response(user_input)
