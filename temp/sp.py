import spacy
from spacy import displacy
from spacy.tokens import Span

nlp = spacy.load('en_core_web_sm')
  
sentence = "inverter not working since yesterday"
  
doc = nlp(sentence)
fb_ent = Span(doc, 0, 1, label="PRODUCT")
doc.set_ents([fb_ent], default="unmodified")

# Option 2: Assign a complete list of ents to doc.ents
doc.ents = list(doc.ents) + [fb_ent]
  
for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)

# print("\n", doc)
# displacy.serve(doc, style="ent")