# ---------------------------------------------
import nltk
import stanza
import spacy_stanza
import spacy
from rowordnet import Synset
from spacy.lang.ro.examples import sentences
from langdetect import detect
import rowordnet as ro
# ---------------------------------------------

import random
from collections import Counter, defaultdict
import sys

def read_input():
	if len(sys.argv) > 1:
		file = sys.argv[1]
		try:
			with open(file, 'r', encoding='utf-8') as f:
				text = f.read()
				return text
		except FileNotFoundError:
			return f"Eroare: Fișierul '{file}' nu a fost găsit."
		except Exception as e:
			return f"Eroare la citirea fișierului: {e}"
	else:
		print("Introduceți textul manual (terminați cu Enter):")
		text = input()
		return text

def show_text_language(text: str):
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
		
def show_semantic_analysis(text: str):
	# stanza.download('ro')
	# nlp = spacy.load('ro_core_news_sm') CAND RULEZI PRIMA DATA SCOTI COMENTARIILE
	nlp = spacy_stanza.load_pipeline('ro')
	doc = nlp(text)
	for token in doc:
		print('{:<12}{:<10}{:<10}{:<10}'.format(token.text, token.pos_, token.dep_, token.head.text))

def show_synonyms(word: str):
	wn = ro.RoWordNet()
	synset_id = wn.synsets(word)[0]
	print("\nCuvantul: {}".format(wn.synset(synset_id).literals))
	print("Sinonime:")
	outbound_relations = wn.outbound_relations(synset_id)
	for outbound_relation in outbound_relations:
		target_synset_id = outbound_relation[0]
		relation = outbound_relation[1]
		if relation == "synonym":
			print("\tSinonim: {}".format(wn.synset(target_synset_id).literals))
	
def print_outbound_relations(word):
	wn = ro.RoWordNet()
	synset_id = wn.synsets(word)[0]
	print("\nPrint all outbound relations of {}".format(wn.synset(synset_id)))
	outbound_relations = wn.outbound_relations(synset_id)
	for outbound_relation in outbound_relations:
		target_synset_id = outbound_relation[0]
		relation = outbound_relation[1]
		print("\tRelation [{}] to synset {}".format(relation, wn.synset(target_synset_id)))
	
	inbound_relations = wn.inbound_relations(synset_id)
	print("\nPrint all inbound relations of {}".format(wn.synset(synset_id)))
	for inbound_relation in inbound_relations:
		source_synset_id = inbound_relation[0]
		relation = inbound_relation[1]
		print("\tRelation [{}] from synset {}".format(relation, wn.synset(source_synset_id)))


if __name__ == "__main__":
	text = "Astăzi este o zi frumoasă, perfectă pentru a învăța ceva nou."
	#show_text_language(text)
	#show_stoichiometric_details(text)
	#show_semantic_analysis(text)
	print_outbound_relations("casă")