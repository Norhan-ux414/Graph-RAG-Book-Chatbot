import json
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))


def clean_relation_name(relation_text):
    relation_text = relation_text.strip().replace(" ", "_").replace("-", "_")
    relation_text = "".join(ch for ch in relation_text if ch.isalnum() or ch == "_")
    return relation_text.upper() if relation_text else "RELATED_TO"


def get_first_verb(tokens):
    for token in tokens:
        if token["pos"] == "VERB":
            return clean_relation_name(token["text"])
    return "RELATED_TO"

def esc(text):
    return text.replace("\\", "\\\\").replace("'", "\\'")


def generate_cypher_queries(data):
    queries = []

    for item in data:
        sentence = item["sentence"]
        entities = item["entities"]
        tokens = item["tokens"]

        if len(entities) == 0:
            continue

        # create nodes
        for ent in entities:
            q = (
                f"MERGE (n:Entity {{name: '{esc(ent['text'])}'}}) "
                f"SET n.label = '{esc(ent['label'])}';"
            )
            queries.append(q)

        # create relationship if at least 2 entities
        if len(entities) >= 2:
            subject = entities[0]["text"]
            obj = entities[1]["text"]
            relation = get_first_verb(tokens)

            q = (
                f"MATCH (a:Entity {{name: '{esc(subject)}'}}), "
                f"(b:Entity {{name: '{esc(obj)}'}}) "
                f"MERGE (a)-[r:{relation}]->(b) "
                f"SET r.sentence = '{esc(sentence)}';"
            )
            queries.append(q)

    return queries


def save_queries(queries, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for q in queries:
            f.write(q + "\n")
    print("Cypher queries saved ✅")


def execute_queries(queries):
    with driver.session() as session:
        for q in queries:
            session.run(q)
    print("Neo4j insertion done ✅")


def main():
    input_path = "data/ocr_output/ner_pos_output.json"
    cypher_output_path = "data/ocr_output/generated_queries.cypher"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    queries = generate_cypher_queries(data)
    print("Total queries generated:", len(queries))

    save_queries(queries, cypher_output_path)
    execute_queries(queries)

    driver.close()


if __name__ == "__main__":
    main()
