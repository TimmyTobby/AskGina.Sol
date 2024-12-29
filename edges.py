from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from typing import Annotated, Literal, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
load_dotenv()
groq_api = os.getenv('GROQ_API_KEY')
if groq_api:
    print('Connection Successful')
llm = ChatGroq(model='llama-3.1-70b-versatile')


# Router Model
class Router(BaseModel):
    """ Route a user query to the most relevant datasource. """

    datasource: Literal["static", "dynamic"] = Field(
        description="Given a user question choose to route it as a static query or a dynamic query.",
    )

# LLM with structured output
llm_router = llm.with_structured_output(Router)

# Instructions
route_instructions = """
You are an expert in determining the appropriate data source for a user query.

If the query is about retrieving real-time information (e.g., recent events, live updates, or dynamic data), route it to "dynamic".

If the query involves historical data or static content (e.g., knowledge retrieval from a vector database), route it to "static".

"""

### Question Router Edge ###

def route_question(state):
    """
    Route question to web search or RAG 

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    source = llm_router.invoke([SystemMessage(content=route_instructions)] + [HumanMessage(content=state["question"])]) 
    
    if source.datasource == 'static':
        print("---ROUTE QUESTION TO STATIC QUERY RAG---")
        return "static"
    
    elif source.datasource == 'dynamic':
        print("---ROUTE QUESTION TO DYNAMIC QUERY RAG---")
        return "dynamic"

### Generation Decision Edge ###

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or add web search

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    web_search = state["web_search"]
    

    if web_search == "Yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print("---DECISION: NOT ALL DOCUMENTS ARE RELEVANT TO QUESTION, INCLUDE WEB SEARCH---")
        return "websearch"
    
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"
    
# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(description="Answer addresses the question, 'yes' or 'no'")
    explanation: str = Field(description="Explain the reasoning for the score")

# LLM with function call 
llm_answer_grader = llm.with_structured_output(GradeAnswer)

# Answer grader system instructions 
answer_grader_system_instructions = """
You are a teacher grading a quiz.

You will be given a QUESTION and a STUDENT ANSWER.

Here is the grade criteria to follow:

(1) Ensure the STUDENT ANSWER is concise and relevant to the QUESTION. Avoid unnecessary information that does not help answer the question.

(2) Ensure the STUDENT ANSWER directly helps to answer the QUESTION, even if it includes extra context (e.g., disclaimers) that provide more clarity or real-time information.

Score:

A score of "yes" means the answer directly addresses the question without unnecessary details. This is the highest (best) score.

A score of "no" means the answer does not sufficiently address the question or includes irrelevant or excessive details.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct.

Avoid simply stating the correct answer at the outset.
"""
# Grader prompt
answer_grader_prompt = "QUESTION: \n\n {question} \n\n STUDENT ANSWER: {generation}"


### Generation wrt Document and Question Grader Edge ###

def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    # print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    # documents = state["documents"]
    generation = state["generation"]
    max_retries = state.get("max_retries", 3) # Default to 3 if not provided

    # hallucination_grader_prompt_formatted = hallucination_grader_prompt.format(documents=format_docs(documents), generation=generation.content)
    # answer_document_score = structured_llm_hallucination_grader.invoke([SystemMessage(content=hallucination_grader_system_instructions)] + [HumanMessage(content=hallucination_grader_prompt_formatted)])
    # answer_document_grade = answer_document_score.binary_score

    # # Check hallucination
    # if answer_document_grade.lower() == "yes":
    #     print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")

    # Check question-answering
    print("---GRADE GENERATION vs QUESTION---")
        
    # Test using question and generation from above 
    answer_question_grader_prompt_formatted = answer_grader_prompt.format(question=question, generation=generation.content)
    answer_question_score = llm_answer_grader.invoke([SystemMessage(content=answer_grader_system_instructions)] + [HumanMessage(content=answer_question_grader_prompt_formatted)])
    answer_question_grade = answer_question_score.binary_score

    if answer_question_grade.lower() == "yes":
        print("---DECISION: GENERATION ADDRESSES QUESTION---")
        return "useful"
    
    elif answer_question_grade.lower() == "no":
        print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
        return "not useful"
    
    elif state["loop_step"] > max_retries:
        print("---DECISION: MAX RETRIES REACHED---")
        return "max retries"  
