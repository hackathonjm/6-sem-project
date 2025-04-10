import json
import nltk
import os
import csv
import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

nltk.download('stopwords', quiet=True)

class StudentChatBot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = LogisticRegression()
        self.inputs = []
        self.outputs = []
        self._load_dataset()
        self._train_model()

    def _load_dataset(self):
        dataset_file = 'dataset.json'
        if not os.path.exists(dataset_file):
            raise FileNotFoundError(f"{dataset_file} not found.")
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            self.inputs.append(item['input'])
            self.outputs.append(item['output'])

    def _preprocess(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        tokens = text.split()
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(filtered_tokens)

    def _train_model(self):
        processed_inputs = [self._preprocess(text) for text in self.inputs]
        X = self.vectorizer.fit_transform(processed_inputs)
        y = self.outputs
        self.classifier.fit(X, y)

    def get_response(self, user_input):
        processed_input = self._preprocess(user_input)
        X = self.vectorizer.transform([processed_input])
        prediction = self.classifier.predict(X)
        response = prediction[0]
        self._log_conversation(user_input, response)
        return response

    def _log_conversation(self, user_input, response):
        log_file = 'chat_log.csv'
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['User Input', 'Chatbot Response'])
            writer.writerow([user_input, response])

chatbot = StudentChatBot()

def get_bot_response(user_input):
    return chatbot.get_response(user_input)
