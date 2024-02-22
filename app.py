# [WIP] Adding more extensive news search tools

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
import gradio as gr

# define tools
search_tool = DuckDuckGoSearchRun()

def execute_crewai_application(topic: str, openai_api_key: str):

# define llm
    llm = ChatOpenAI(model="gpt-4-turbo-preview",
                    api_key=openai_api_key,
                    temperature=0.5,
                    max_tokens=1000)    
# Create Agents
    news_search_agent = Agent(
        role='News Searcher',
        goal='Generate key points for each news article from the latest news',
        backstory='Expert in analysing and generating key points from news content for quick updates.',
        tools=[search_tool],
        allow_delegation=True,
        verbose=True,
        llm=llm
    )

    writer_agent = Agent(
        role='Writer',
        goal='Identify all the topics received. Use the Search tool for detailed exploration of each topic. Summarise the retrieved information in depth for every topic.',
        backstory='Expert in crafting engaging narratives from complex information.',
        tools=[search_tool],
        allow_delegation=True,
        verbose=True,
        llm=llm
    )

# 3. Creating Tasks
    news_search_task = Task(
        description='Search for the latest news on topic and create key points for each news.',
        agent=news_search_agent,
        context=topic,
        tools=[search_tool]
    )

    writer_task = Task(
        description="""
        Go step by step.
        Step 1: Identify all the topics received.
        Step 2: Use the Search tool to search for information on each topic one by one. 
        Step 3: Go through every topic and write an in-depth summary of the information retrieved.
        Don't skip any topic.
        """,
        agent=writer_agent,
        context=[news_search_task],
        tools=[search_tool]
    )

# 4. Creating Crew
    news_crew = Crew(
        agents=[news_search_agent, writer_agent],
        tasks=[news_search_task, writer_task],
        process=Process.sequential, 
        manager_llm=llm
    )

# Execute the crew 
    result = news_crew.kickoff()
    print(result)

def gradio_interface(topic, openai_api_key):
    return execute_crewai_application(topic, openai_api_key)

description_text = """
Enter a topic and your OpenAI API key.
---
Get your OpenAI API here: https://openai.com/blog/openai-api
---
"""
iface = gr.Interface(fn=gradio_interface,  
                     inputs=[
                         gr.Textbox(label="Enter a topic to search"),
                         gr.Textbox(label="OpenAI API Key", type="password")
                         
                     ],
                     outputs=gr.Textbox(),  
                     title="CrewAI News Search and Summarization",
                     description=description_text)

iface.launch()
