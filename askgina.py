from typing import Annotated, Sequence, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.graph import END
import json
import operator
from typing_extensions import TypedDict
from typing import List, Annotated
from langgraph.graph import END, StateGraph, START
from IPython.display import Image, display
from typing import Optional, List
from nodes import real_time_ret, web_search, retrieve, grade_documents, generate
from edges import route_question, decide_to_generate, grade_generation_v_documents_and_question


# defiing the flow
class GraphState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    question: str  # User question
    generation: str  # LLM generation
    web_search: str  # Binary decision to run web search
    max_retries: int  # Max number of retries for answer generation
    answers: int  # Number of answers generated
    loop_step: Annotated[int, operator.add]
    documents: List[str]  # List of retrieved documents 

workflow = StateGraph(GraphState)
# retriever_tool = create_retriever_tool(
#     realtime_retriever,
#     "retrieve_realtime_info",
#     "Search and return information on the solana blockchain."
# )
# real_time_retriever = ToolNode([retriever_tool])
# Define the nodes
workflow.add_node('real_time_retrieve', real_time_ret)
workflow.add_node("websearch", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate

# Build graph
workflow.set_conditional_entry_point(
    route_question,
    {
        "static": "retrieve",
        "dynamic": "real_time_retrieve",
    },
)
workflow.add_edge("websearch", "generate")
workflow.add_edge('real_time_retrieve', 'generate')
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "websearch": "websearch",
        "generate": "generate",
    },
)
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "useful": END,
        "not useful": "websearch",
        "max retries": END,
    },
)

# Compile
graph = workflow.compile()
# display(Image(graph.get_graph().draw_mermaid_png()))

# Generate and save the image
image_path = "workflow.png"
graph_image = graph.get_graph().draw_mermaid_png()

with open(image_path, 'wb') as f:
    f.write(graph_image)
