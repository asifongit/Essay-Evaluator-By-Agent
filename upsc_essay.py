import operator
from typing import TypedDict, Annotated
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

# --- Setup and Initializations ---

# Load environment variables (e.g., OPENAI_API_KEY) from a .env file
load_dotenv()

# Initialize the ChatModel
API_KEY = os.getenv("PERPLEXITY_API_KEY")

model = ChatOpenAI(
    model="sonar",
    api_key=API_KEY,                        # REQUIRED
    base_url="https://api.perplexity.ai"    # REQUIRED
)
# --- Schemas for Structured Output ---

class EvaluationSchema(BaseModel):
    """Schema for structured evaluation output."""
    feedback: str = Field(description='Detailed feedback for the essay')
    score: int = Field(description='Score out of 10', ge=0, le=10)

# Create a parser
parser = PydanticOutputParser(pydantic_object=EvaluationSchema)

# --- State for LangGraph ---

class UPSCState(TypedDict):
    """Represents the state of the essay evaluation workflow."""
    essay: str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    overall_feedback: str
    # individual_scores is a list that will be appended to by each node
    individual_scores: Annotated[list[int], operator.add]
    avg_score: float

# --- Graph Nodes (Evaluation Functions) ---

def evaluate_language(state: UPSCState):
    """Evaluates the language quality of the essay."""
    prompt = PromptTemplate(
        template="Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10.\n{format_instructions}\nEssay:\n{essay}",
        input_variables=["essay"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | model | parser
    output = chain.invoke({"essay": state["essay"]})
    
    return {'language_feedback': output.feedback, 'individual_scores': [output.score]}

def evaluate_analysis(state: UPSCState):
    """Evaluates the depth of analysis of the essay."""
    prompt = PromptTemplate(
        template="Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10.\n{format_instructions}\nEssay:\n{essay}",
        input_variables=["essay"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | model | parser
    output = chain.invoke({"essay": state["essay"]})

    return {'analysis_feedback': output.feedback, 'individual_scores': [output.score]}

def evaluate_thought(state: UPSCState):
    """Evaluates the clarity of thought of the essay."""
    prompt = PromptTemplate(
        template="Evaluate the clarity of thought of the following essay and provide a feedback and assign a score out of 10.\n{format_instructions}\nEssay:\n{essay}",
        input_variables=["essay"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | model | parser
    output = chain.invoke({"essay": state["essay"]})

    return {'clarity_feedback': output.feedback, 'individual_scores': [output.score]}

def final_evaluation(state: UPSCState):
    """Summarizes all feedback and calculates the average score."""
    
    # 1. Generate summarized feedback using the model
    prompt = (
        f'Based on the following feedbacks create a summarized feedback \n '
        f'language feedback - {state["language_feedback"]} \n '
        f'depth of analysis feedback - {state["analysis_feedback"]} \n '
        f'clarity of thought feedback - {state["clarity_feedback"]}'
    )
    overall_feedback = model.invoke(prompt).content

    # 2. Calculate the average score
    avg_score = sum(state['individual_scores']) / len(state['individual_scores'])

    # Return the overall feedback and the average score
    return {'overall_feedback': overall_feedback, 'avg_score': avg_score}

# --- Build the LangGraph Workflow ---

# 1. Create the graph
graph = StateGraph(UPSCState)

# 2. Add nodes for each evaluation step
graph.add_node('evaluate_language', evaluate_language)
graph.add_node('evaluate_analysis', evaluate_analysis)
graph.add_node('evaluate_thought', evaluate_thought)
graph.add_node('final_evaluation', final_evaluation)

# 3. Add edges (define workflow)
# Start node sends the essay to all three evaluation nodes in parallel
graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_analysis')
graph.add_edge(START, 'evaluate_thought')

# All three evaluation nodes feed their results into the final_evaluation node
graph.add_edge('evaluate_language', 'final_evaluation')
graph.add_edge('evaluate_analysis', 'final_evaluation')
graph.add_edge('evaluate_thought', 'final_evaluation')

# The final evaluation node marks the end of the workflow
graph.add_edge('final_evaluation', END)

# 4. Compile the workflow
workflow = graph.compile()

if __name__ == "__main__":
    essay=input("Enter the essay")

    # Initial state containing the essay to be evaluated
    intial_state = {
        'essay': essay
    }

    # Run the workflow and print the final result
    result = workflow.invoke(intial_state)
    print(result)