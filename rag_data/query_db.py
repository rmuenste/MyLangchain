# from dataclasses import dataclass
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()

CHROMA_PATH = "./chroma_storage"

PROMPT_TEMPLATE = """
Beantworte the Frage basierend auf dem folgenden Kontext:

{context}

---

Beantworte the Frage basierend auf dem obigen Kontext: {question}
"""


def main():
    # Create CLI.
#    parser = argparse.ArgumentParser()
#    parser.add_argument("query_text", type=str, help="The query text.")
#    args = parser.parse_args()
#    query_text = args.query_text
    query_text = "Wie ist die Vorgangsnummer?" 
    query_text = "An wen wurde die Aufgabe mit dem Namen VP_0008_Alpine zugewiesen?" 
    query_text = "Wurde die Aufgabe mit dem Namen VP_0008_Alpine begonnen?" 

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    print(results)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    response_text = llm.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()

