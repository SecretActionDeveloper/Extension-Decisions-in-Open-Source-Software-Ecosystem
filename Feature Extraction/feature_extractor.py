import pandas as pd
from ast import literal_eval
import os
from groq import Groq
import string
import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import time
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Initialize NLP tools
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    if isinstance(text, str):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
        text = re.sub(r'\s+', ' ', text).strip()

        # Replace abbreviations
        abbreviations = {"pr": "pullrequest"}
        for abbr, full_form in abbreviations.items():
            text = text.replace(abbr, full_form)

        words = word_tokenize(text)
        filtered_words = [word for word in words if word not in stop_words]  # Remove stop words
        lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
        text = " ".join(lemmatized_words)

        # Remove unwanted characters
        replace_list = [',', '\'', '\"', '_', '-', "\\", "/", "\n"]
        for char in replace_list:
            text = text.replace(char, '')

    return text

def extract_between_characters(s, start_char, end_char):
    start_index = s.find(start_char)
    if start_index == -1:
        return None  # Start character not found
    end_index = s.find(end_char, start_index + 1)
    if end_index == -1:
        return None  # End character not found
    return s[start_index + 1:end_index]

# Load Groq API key
with open('groq_api.txt', 'r') as file:
    groq_api_key = file.read().strip()

client = Groq(api_key=groq_api_key)

prompt = (
    """
    capacity and Role: Requirement Analyst
    Insight: We are looking to extract software features and functionalities from software descriptions. 
    Software features define the capabilities of the software.
    Statement: Extract system functionalities from a given list of descriptions.
    Personality: Accurate and precise, and ensure the features are supported by the descriptions.
    Experiment: Output all features in a Python list. ONLY output the Python list.
    Here are the descriptions: 
    """
)

# Load dataset
input_file = "Path to the data file"
df = pd.read_csv(input_file)

# Ensure required columns exist
df["Features_raw"] = df.get("Features_raw", "")
df["features_cleaned"] = df.get("features_cleaned", "")

for i in range(len(df)):
    if not df["Features_raw"].iloc[i]:
        time.sleep(5)
        print(f"Processing {i + 1}/{len(df)}")
        description = literal_eval(df["action_file_descriptions"].iloc[i])

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a Requirement Analyst."},
                {"role": "user", "content": prompt + str(description)},
            ],
            model="llama3-8b-8192",
            temperature=0.0,
        )

        try:
            content = literal_eval(chat_completion.choices[0].message.content)
        except Exception:
            answer = chat_completion.choices[0].message.content
            try:
                content = extract_between_characters(answer, "[", "]").split(", ")
            except Exception:
                content = re.sub(r'[\[\]]', '', answer).split(',')

        df.at[i, "Features_raw"] = content

        if isinstance(content, list):
            cleaned_features = [clean_text(feature) for feature in content]
            df.at[i, "features_cleaned"] = cleaned_features
        else:
            df.at[i, "features_cleaned"] = False

