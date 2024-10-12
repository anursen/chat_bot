from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template('''You are a home assistant system that understands user commands and helps automate tasks. Based on the user's input, identify their intention. Here are the categories of intentions you can recognize:

1. **Comfort and Environment Control** (e.g., adjusting lighting, temperature, humidity).
2. **Home Automation and Scheduling** (e.g., creating routines, setting triggers).
3. **Safety and Security** (e.g., monitoring occupancy, setting alerts).
4. **Personalized Information Requests** (e.g., weather, prayer times, location-based actions).
5. **Energy Management** (e.g., checking Tesla charger, optimizing energy usage).
6. **Daily Activity Assistance** (e.g., morning or evening routines).
7. **Task Automation** (e.g., combining multiple tasks into a single command).

Example 
Human Message : "What's the current temperature in the living room?"

AI Message : "The user is asking for the temperature in the living room. The primary intention is to check the comfort level. Retrieve the current temperature from the living room sensor and provide the value."
Human Message :"Can you check the humidity level in the bedroom?"

AI Message : "The user is requesting the humidity level in the bedroom. The intention is related to comfort and environment control. Fetch the humidity data from the bedroom sensor and share the current reading."

Human Message : {input}


''')

questions = ["What's the current temperature in the living room?"
,"Can you check the humidity level in the bedroom?"
,"Is it hot or cold in the kitchen right now?"
,"What’s the temperature in the basement?"
,"How humid is the air in the bathroom?"
,"What's the temperature in the house?"
,"Can you tell me the temperature in the kids' room?"
,"How warm is it in the garage?"
,"What's the humidity level in the office?"
,"Can you give me a status update on the living room temperature?"
,"Check the temperature in the master bedroom."
,"Is it too humid in the laundry room?"
,"What’s the current temperature near the Tesla charger?"
,"How hot is it in the sunroom?"
,"Can you monitor the temperature in the guest room?"]


responses = [
    "The user is asking for the temperature in the living room. The primary intention is to check the comfort level. Retrieve the current temperature from the living room sensor and provide the value.",
    "The user is requesting the humidity level in the bedroom. The intention is related to comfort and environment control. Fetch the humidity data from the bedroom sensor and share the current reading.",
    "The user wants to know if it is hot or cold in the kitchen. The primary intention is to check the current temperature. Retrieve the temperature data from the kitchen sensor and provide the answer.",
    "The user is asking for the temperature in the basement. The intention is to check the comfort level in that space. Fetch the basement temperature and provide the current value.",
    "The user is inquiring about the humidity in the bathroom. The primary goal is to check the moisture level in that room. Retrieve the humidity data from the bathroom sensor.",
    "The user wants to know the temperature in the house. The intention is to check the overall environment. Fetch the temperature data from the main system and provide the current house temperature.",
    "The user is asking for the temperature in the kids' room. The intention is to check the comfort level in that room. Retrieve the current temperature from the kids' room sensor.",
    "The user wants to know how warm it is in the garage. The primary intention is to check the current temperature. Retrieve the temperature data from the garage sensor and provide the result.",
    "The user is asking for the humidity level in the office. The primary intention is to monitor comfort and air quality in that space. Fetch the office humidity data and report back.",
    "The user is asking for a status update on the living room temperature. The intention is to check the current condition of the living room. Retrieve the temperature from the living room sensor and provide the value.",
    "The user wants to check the temperature in the master bedroom. The primary intention is to monitor comfort in that space. Fetch the master bedroom temperature and provide the current value.",
    "The user is asking if it is too humid in the laundry room. The intention is to check the moisture level and air quality in the room. Retrieve the humidity data and provide feedback.",
    "The user is asking for the current temperature near the Tesla charger. The primary intention is to monitor the environment around the charger. Fetch the temperature near the Tesla charger and provide the reading.",
    "The user wants to know how hot it is in the sunroom. The intention is to check the temperature in that room. Retrieve the temperature data from the sunroom sensor and provide the current value.",
    "The user is asking to monitor the temperature in the guest room. The primary intention is to check comfort in that specific room. Retrieve the current temperature from the guest room sensor."
]


from langchain_core.prompts import PromptTemplate

example_prompt = PromptTemplate.from_template("Question: {question}\n{answer}")

examples = [
    {
        "question": "Who lived longer, Muhammad Ali or Alan Turing?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: How old was Muhammad Ali when he died?
Intermediate answer: Muhammad Ali was 74 years old when he died.
Follow up: How old was Alan Turing when he died?
Intermediate answer: Alan Turing was 41 years old when he died.
So the final answer is: Muhammad Ali
""",
    },
    {
        "question": "When was the founder of craigslist born?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: Who was the founder of craigslist?
Intermediate answer: Craigslist was founded by Craig Newmark.
Follow up: When was Craig Newmark born?
Intermediate answer: Craig Newmark was born on December 6, 1952.
So the final answer is: December 6, 1952
""",
    },
    {
        "question": "Who was the maternal grandfather of George Washington?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: Who was the mother of George Washington?
Intermediate answer: The mother of George Washington was Mary Ball Washington.
Follow up: Who was the father of Mary Ball Washington?
Intermediate answer: The father of Mary Ball Washington was Joseph Ball.
So the final answer is: Joseph Ball
""",
    },
    {
        "question": "Are both the directors of Jaws and Casino Royale from the same country?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: Who is the director of Jaws?
Intermediate Answer: The director of Jaws is Steven Spielberg.
Follow up: Where is Steven Spielberg from?
Intermediate Answer: The United States.
Follow up: Who is the director of Casino Royale?
Intermediate Answer: The director of Casino Royale is Martin Campbell.
Follow up: Where is Martin Campbell from?
Intermediate Answer: New Zealand.
So the final answer is: No
""",
    },
]
print(example_prompt.invoke(examples[1]).to_string())

from langchain_core.prompts import FewShotPromptTemplate

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question: {input}",
    input_variables=["input"],
)

a = prompt.invoke({"input": "Who was the father of Mary Ball Washington?"}).to_string()
type(a)
len(a)


from langchain_core.prompts import FewShotPromptTemplate

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question: {input}",
    input_variables=["input"],
)


a = prompt.invoke({"input": "Who was the father of Mary Ball Washington?"}).to_string()



from langchain_core.tools import StructuredTool


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


async def amultiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


calculator = StructuredTool.from_function(func=multiply, coroutine=amultiply)

print(calculator.invoke({"a": 2, "b": 3}))
print(await calculator.ainvoke({"a": 2, "b": 5}))


from langchain_core.language_models import GenericFakeChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [("human", "Hello. Please respond in the style of {answer_style}.")]
)

# Placeholder LLM
llm = GenericFakeChatModel(messages=iter(["hello matey"]))

chain = prompt | llm | StrOutputParser()

as_tool = chain.as_tool(
    name="Style responder", description="Description of when to use tool."
)
as_tool.args


from typing import Optional, Type, Field
from pydantic import BaseModel, Field


from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class CustomCalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = True

    def _run(
        self, a: int, b: int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return a * b

    async def _arun(
        self,
        a: int,
        b: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        # If the calculation is cheap, you can just delegate to the sync implementation
        # as shown below.
        # If the sync calculation is expensive, you should delete the entire _arun method.
        # LangChain will automatically provide a better implementation that will
        # kick off the task in a thread to make sure it doesn't block other async code.
        return self._run(a, b, run_manager=run_manager.get_sync())


multiply = CustomCalculatorTool()
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)

print(multiply.invoke({"a": 2, "b": 3}))
print(await multiply.ainvoke({"a": 2, "b": 3}))