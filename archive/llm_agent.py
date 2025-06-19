from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

def ask_llm(question, context):
    prompt = PromptTemplate(
        input_variables=["question", "context"],
        template="""
You are a helpful data assistant. A user has asked a question about available datasets.

Question: {question}

Here are summaries of relevant files:
{context}

Based on this, provide a clear answer or next steps.
"""
    )
    full_prompt = prompt.format(question=question, context=context)
    response = llm([HumanMessage(content=full_prompt)])
    return response.content
