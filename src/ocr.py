#=========================
#1. import dependancies
#=========================

import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")


# 2. Create Azure client


from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)


# 3.Run OCR on each page

import json
import time

input_folder = "data/pages1-16"
output_file = "data/ocr_output/ocr_result.json"

files = sorted(
    [f for f in os.listdir(input_folder) if f.endswith(".pdf")],
    key=lambda x: int(x.split("-")[-1].split(".")[0])
)


ocr_results = []

for file_name in files:
    file_path = os.path.join(input_folder, file_name)
    print("Processing:", file_name)

    try:
        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-read",
                document=f
            )
            result = poller.result()

        page_text = ""

        for page in result.pages:
            for line in page.lines:
                page_text += line.content + "\n"

        ocr_results.append({
            "file_name": file_name,
            "text": page_text.strip()
        })

    except Exception as e:
        print("Error in", file_name, ":", e)

    time.sleep(1)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(ocr_results, f, ensure_ascii=False, indent=2)

print("OCR Done ")


import json

json_path = "data/ocr_output/ocr_result.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Total pages:", len(data))
print(data[0]["text"][:500])


##### 5. Cleaning #####


import re

all_text = ""
for item in data:
    all_text += item["text"] + "\n"


cleaned_text = re.sub(r"\n+", "\n", all_text)

cleaned_text = cleaned_text.replace("\n", " ")

cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
sentences = [s.strip() for s in sentences if s.strip()]

cleaned_output_file = "data/ocr_output/cleaned_text.json"

with open(cleaned_output_file, "w", encoding="utf-8") as f:
    json.dump(sentences, f, ensure_ascii=False, indent=2)

print("Total sentences:", len(sentences))
print(sentences[:5])
