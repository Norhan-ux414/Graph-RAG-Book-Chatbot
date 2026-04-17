import os
import re
from dotenv import load_dotenv
from neo4j import GraphDatabase
import ollama

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

MODEL_NAME = "llama3"


def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]


def generate_cypher_from_question(question):
    prompt = f"""
You are an expert Neo4j assistant.

Graph schema:
- Nodes: (:Entity {{name, label}})
- Relationships: dynamically created from extracted verbs, such as ANSWERED, CAME, DID, GOT, RELATED_TO, etc.

Task:
Convert the user's question into ONE valid Cypher query only.
Return ONLY the Cypher query.
Do not explain anything.
Do not use markdown.
Do not include backticks.

Examples:
Question: Show all nodes
Cypher: MATCH (n) RETURN n LIMIT 20

Question: Show all relationships
Cypher: MATCH p=()-[r]->() RETURN p LIMIT 20

Question: Find entity Steve Jobs
Cypher: MATCH (n:Entity {{name: "Steve Jobs"}}) RETURN n

Question: What is connected to Steve Jobs?
Cypher: MATCH (a:Entity {{name: "Steve Jobs"}})-[r]-(b) RETURN a.name AS source, type(r) AS relation, b.name AS target LIMIT 20

User question:
{question}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    cypher = response["message"]["content"].strip()
    return cypher


def extract_cypher(text):
    text = text.strip()

    text = re.sub(r"^```[a-zA-Z]*", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    return text


def chatbot():
    print("Smart Chatbot started ✅")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Chatbot stopped.")
            break

        try:
            cypher = generate_cypher_from_question(question)
            cypher = extract_cypher(cypher)

            print("\nGenerated Cypher:")
            print(cypher)

            results = run_query(cypher)

            print("\nBot answer:")
            if results:
                for item in results[:10]:
                    print(item)
            else:
                print("No results found.")

            print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print("Error:", e)
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    chatbot()
    driver.close()
