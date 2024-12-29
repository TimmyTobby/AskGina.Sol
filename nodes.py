from retrievers import retriever, create_realtime_retriever_2
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document


load_dotenv()
groq_api = os.getenv('GROQ_API_KEY')
if groq_api:
    print('Connection Successful')
tavily_api = os.getenv('TAVILY_API_KEY')
if tavily_api:
    print("Connection Successful")

llm = ChatGroq(model='llama-3.1-70b-versatile')

# Web search Tool
web_search_tool = TavilySearchResults(k=2)

### Retrieve Node ###
def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---STATIC DOCUMENT RETRIEVAL---")
    question = state["question"]

    # Write retrieved documents to documents key in state
    documents = retriever.invoke(question)
    return {"documents": documents}

# Generate component
rag_prompt = """You are an assistant for question-answering tasks. 

Use the following pieces of retrieved context to answer the question. 

If you don't know the answer, just say that you don't know. 

Use three sentences maximum and keep the answer concise.

Question: {question} 

Context: {context} 

Answer:"""
# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


### Generate Node ###
def generate(state):
    """
    Generate answer using RAG on retrieved documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("GENERATING RESPONSE...")
    question = state["question"]
    documents = state["documents"]
    loop_step = state.get("loop_step", 0)

    # RAG generation
    docs_txt = format_docs(documents)
    rag_prompt_formatted = rag_prompt.format(context=docs_txt, question=question)

    generation = llm.invoke([HumanMessage(content=rag_prompt_formatted)])
    
    return {"generation": generation, "loop_step": loop_step + 1}


## Defining Grade Relevance Model
class GradeDocumentRelevance(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(description="Documents are relevant to the question, 'relevant' or 'not_relevant'")

# LLM with structured output
llm_doc_grader = llm.with_structured_output(GradeDocumentRelevance)

doc_relevance_system_instructions = """
You are an expert in assessing the relevance of a retrieved document to a user query.

Evaluate relevance based on the following criteria:
1. **Alignment with Query Intent**: The document must address the subject or topic of the query. If it contains useful or supporting information for the query, it is "relevant."
2. **Semantic Understanding**: The document should provide context, explanations, or details that help answer the query. Exact keywords are not required if the overall meaning aligns.
3. **Partial Relevance**: If the document partially answers the query or contains some useful context but is incomplete, still classify it as "relevant."

Score the document as:
- 'Relevant' if it provides meaningful information or partially helps answer the query, even indirectly.
- 'Not_Relevant' only if it is completely unrelated to the query or fails to provide any useful context.

Consider both direct and indirect relevance. Be fair but critical, ensuring your assessment reflects the user's intent accurately.
"""

# user prompt
user_prompt = "Here is the retrieved document: \n\n {document} \n\n Here is the user question: \n\n {question}"
### Grade Document Node ###
def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    print("---CHECKING DOCUMENT RELEVANCE TO THE QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    web_search = "No"
    
    for doc in documents:
        doc_grader_prompt_formatted = user_prompt.format(
            document=doc.page_content, question=question
        )

        score = llm_doc_grader.invoke(
            [SystemMessage(content=doc_relevance_system_instructions)]
            + [HumanMessage(content=doc_grader_prompt_formatted)]
        )
        grade = score.binary_score

        # Document relevant
        if grade.lower() == "relevant":
            print("---DOCUMENT IS RELEVANT---")
            filtered_docs.append(doc)

        # Document not relevant
        else:
            print("---DOCUMENT IS NOT RELEVANT---")
            # We do not include the document in filtered_docs
            # We set a flag to indicate that we want to run web search
            web_search = "Yes"
            continue

    return {"documents": filtered_docs, "web_search": web_search}

### Web Search Node ###

def web_search(state):
    """
    Web search based based on the question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Appended web results to documents
    """

    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([doc["content"] for doc in docs])
    web_results = Document(page_content=web_results)

    documents.append(web_results)
    return {"documents": documents}

# Function to handle invocation with retriever reloading
# def invoke_realtime_retriever(embedding_model, query):
#     # Reload the retriever each time by creating a new one with the latest data
#     realtime_retriever = create_realtime_retriever(embedding_model)
    
#     # Now you can invoke the retriever with the query
#     documents = realtime_retriever.invoke(query)
    
#     return documents

def real_time_ret(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("REAL TIME")
    question = state['question']
    documents = create_realtime_retriever_2()
    return {'documents': documents}