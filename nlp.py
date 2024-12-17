# ---------------------------------------------
import nltk
import stanza
import spacy_stanza
import spacy
from spacy.lang.ro.examples import sentences
from langdetect import detect
import rowordnet as ro
# ---------------------------------------------

import random
from collections import Counter
import sys


def read_input():
	if len(sys.argv) > 1:
		fisier = sys.argv[1]
		try:
			with open(fisier, 'r', encoding='utf-8') as f:
				text = f.read()
				return text
		except FileNotFoundError:
			return f"Eroare: Fișierul '{fisier}' nu a fost găsit."
		except Exception as e:
			return f"Eroare la citirea fișierului: {e}"
	else:
		print("Introduceți textul manual (terminați cu Enter):")
		text = input()
		return text


def show_semantic_analysis(text: str):
	# inca e in lucru
	# stanza.download('ro')
	# nlp = spacy.load('ro_core_news_sm')
	nlp = spacy_stanza.load_pipeline('ro')
	doc = nlp(text)
	for token in doc:
		print('{:<12}{:<10}{:<10}{:<10}'.format(token.text, token.pos_, token.dep_, token.head.text))


def show_text_language(text):
	try:
		language = detect(text)
		print(f"Textul este scris în limba {language}.")
	except Exception as e:
		return f"Error: {e}"


def show_stoichiometric_details(text: str):
	words = nltk.word_tokenize(text)
	words_length = len(words)
	character_length = len(text)
	
	words_frequency = Counter(words)
	
	print("Informații stilometrice:")
	print(f"  - Lungime în caractere: {character_length}")
	print(f"  - Lungime în cuvinte: {words_length}")
	print("  - Frecvența cuvintelor:")
	for word, frequency in words_frequency.items():
		print(f"    * {word}: {frequency} ori")


def show_synonyms(word: str):
	wn = ro.RoWordNet()
	
	synset_ids = wn.synsets(literal=word)
	
	if not synset_ids:
		print(f"Nu au fost găsite sinonime pentru cuvântul '{word}'.")
		return
	
	print(f"Sinonime pentru cuvântul '{word}':")
	
	for synset_id in synset_ids:
		synset = wn.synset(synset_id)
		literals = synset.literals
		print(f"  - Synset ID: {synset_id}, Sinonime: {', '.join(literals)}")


def show_similar_text(text: str, replacement_rate=0.2):
	wn = ro.RoWordNet()
	
	words = text.split()
	
	num_replacements = max(1, int(len(words) * replacement_rate))
	
	indices_to_replace = random.sample(range(len(words)), num_replacements)
	
	for idx in indices_to_replace:
		word = words[idx]
		
		synset_ids = wn.synsets(literal=word.lower())
		
		if synset_ids:
			synset_id = random.choice(synset_ids)
			synset = wn.synset(synset_id)
			
			# Sinonimele, hipernimele și antonimele
			synonyms = synset.literals
			hypernyms = [wn.synset(rel[0]).literals for rel in wn.outbound_relations(synset_id) if rel[1] == 'hypernym']
			antonyms = [f"nu {ant}" for ant in synset.literals if
			            ant != word.lower()]
			
			# Inlocuitor potrivit
			candidates = set(synonyms) | {lit for hyp in hypernyms for lit in hyp} | set(antonyms)
			candidates.discard(word.lower())
			
			if candidates:
				replacement = random.choice(list(candidates))
				words[idx] = replacement
	
	print(' '.join(words))


if __name__ == "__main__":
	text = "Astăzi este o zi frumoasă, perfectă pentru a învăța ceva nou."
	show_text_language(text)
	show_stoichiometric_details(text)
	# show_semantic_analysis(text)
	show_synonyms("pentru")
	show_similar_text(text)
