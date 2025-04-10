import json
import os
import csv
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Basic English stopwords list (no NLTK needed)
BASIC_STOPWORDS = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves", "he", "him",
    "his", "himself", "she", "her", "hers", "herself", "it", "its",
    "itself", "they", "them", "their", "theirs", "themselves", "what",
    "which", "who", "whom", "this", "that", "these", "those", "am",
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "having", "do", "does", "did", "doing", "a", "an", "the",
    "and", "but", "if", "or", "because", "as", "until", "while", "of",
    "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to",
    "from", "up", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "s", "t", "can", "will", "just", "don",
    "should", "now"
])

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

        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            self.inputs.append(item['input'])
            self.outputs.append(item['output'])

    def _preprocess(self, text):
        """Simplified tokenizer without punkt – lowercase, remove punctuation, stopwords."""
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)  # Matches words only
        filtered_tokens = [word for word in tokens if word not in BASIC_STOPWORDS]
        return ' '.join(filtered_tokens)

    def _train_model(self):
        """Train TF-IDF + Logistic Regression on the dataset."""
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
        """Log conversations to chat_log.csv."""
        log_file = 'chat_log.csv'
        file_exists = os.path.isfile(log_file)

        with open(log_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['User Input', 'Chatbot Response'])
            writer.writerow([user_input, response])

# Initialize chatbot instance once
chatbot = StudentChatBot()

# Function to be imported in app.py
def get_bot_response(user_input):
    return chatbot.get_response(user_input)
