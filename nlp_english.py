#---------------------------------------
import sys
import os
from langdetect import detect
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk import download, pos_tag
import random
#---------------------------------------
download("punkt")
download("wordnet")
download("stopwords")
download('averaged_perceptron_tagger_eng')
#---------------------------------------

def read_text(input_source):
	if os.path.exists(input_source):
		with open(input_source, "r", encoding="utf-8") as file:
			text = file.read()
	else:
		text = input_source
	return text

def detect_language(text):
	return detect(text)

def stylometric_analysis(text):
	"""
    Performs stylometric analysis on the input text.

    Computes metrics such as word count, character count, and the top 10 most
    frequent words.

    Args:
        text (str): Input text.

    Returns:
        dict: A dictionary containing stylometric information:
            - 'word_count': Total number of words.
            - 'char_count': Total number of characters.
            - 'word_frequencies': List of the 10 most frequent words and their counts.
    """
	words = word_tokenize(text)
	word_count = len(words)
	char_count = len(text)
	word_frequencies = FreqDist(words)
	return {
			"word_count"      : word_count,
			"char_count"      : char_count,
			"word_frequencies": word_frequencies.most_common(10),
	}

def generate_alternatives(text):
	"""
    Generates an alternative version of the input text by replacing words with synonyms.

    Uses WordNet to find synonyms for words. At least 20% of the words should
    be replaced with their alternatives if available.

    Args:
        text (str): Input text.

    Returns:
        str: Modified text with replaced words.
    """
	words = word_tokenize(text)
	new_text = []
	for word in words:
		synsets = wordnet.synsets(word)
		if synsets:
			synonyms = [lemma.name() for lemma in synsets[0].lemmas() if lemma.name() != word]
			if synonyms:
				new_text.append(random.choice(synonyms))
			else:
				new_text.append(word)
		else:
			new_text.append(word)
	return " ".join(new_text)

def extract_keywords_and_generate_sentences(text, num_keywords=5):
	"""
	Extracts keywords from the text and generates meaningful sentences for each keyword.

	Uses NLTK for tokenization, filtering stopwords, and determining the most frequent words.
	Generates contextually appropriate sentences for each keyword based on its part of speech (POS).

	Args:
		text (str): Input text.
		num_keywords (int): Number of top keywords to extract.

	Returns:
		list: List of sentences generated using the extracted keywords.
	"""
	stop_words = set(stopwords.words("english"))
	words = word_tokenize(text)
	
	# Filter words: remove stopwords, punctuation, and convert to lowercase
	filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
	
	# Frequency distribution to get top keywords
	fdist = FreqDist(filtered_words)
	keywords = [word for word, freq in fdist.most_common(num_keywords)]
	
	# Generate sentences based on POS tagging
	sentences = []
	for keyword in keywords:
		pos = pos_tag([keyword])[0][1]  # Get part of speech for the keyword
		
		if pos.startswith('NN'):  # Noun
			sentences.append(f"The text highlights the importance of {keyword}.")
		elif pos.startswith('VB'):  # Verb
			sentences.append(f"The text emphasizes the act of {keyword}.")
		elif pos.startswith('JJ'):  # Adjective
			sentences.append(f"The text describes something as {keyword}.")
		else:  # Generic fallback
			sentences.append(f"The text discusses {keyword}.")
	
	return sentences


def main(input_source):
	text = read_text(input_source)
	
	#Identifică limba în care este scris acel text.#
	#---------------------------------------------------------------------
	language = detect_language(text)
	print(f"Detected language: {language}")
	#---------------------------------------------------------------------
	
	#Afișează informatii stilometrice#
	#---------------------------------------------------------------------
	analysis = stylometric_analysis(text)
	print("Stylometric Analysis:")
	print(f"Word Count: {analysis['word_count']}")
	print(f"Character Count: {analysis['char_count']}")
	print(f"Top 10 Word Frequencies: {analysis['word_frequencies']}")
	#---------------------------------------------------------------------
	
	#Generează versiuni alternative ale acelui text#
	#---------------------------------------------------------------------
	alternative_text = generate_alternatives(text)
	print("\nAlternative Text:")
	print(alternative_text)
	#---------------------------------------------------------------------
	
	#Extrage cuvinte cheie și generează propoziții#
	#---------------------------------------------------------------------
	sentences = extract_keywords_and_generate_sentences(text)
	print("\nGenerated Sentences:")
	for sentence in sentences:
		print(sentence)
	#---------------------------------------------------------------------


if __name__ == "__main__":
	source = input("Enter text or file path: ")
	main(source)
