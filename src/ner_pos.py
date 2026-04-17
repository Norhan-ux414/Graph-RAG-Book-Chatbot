import json
import spacy


nlp = spacy.load("en_core_web_sm")


json_path = "data/ocr_output/cleaned_text.json"

with open(json_path, "r", encoding="utf-8") as f:
    sentences = json.load(f)

print("Total sentences loaded:", len(sentences))


results = []

for sentence in sentences:
    doc = nlp(sentence)

    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    tokens = []
    for token in doc:
        tokens.append({
            "text": token.text,
            "pos": token.pos_,
            "dep": token.dep_,
            "head": token.head.text
        })

    results.append({
        "sentence": sentence,
        "entities": entities,
        "tokens": tokens
    })


output_path = "data/ocr_output/ner_pos_output.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("NER + POS Done ")


print("\nSample result:")
print(json.dumps(results[0], ensure_ascii=False, indent=2))
