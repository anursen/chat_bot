# Tool
#https://python.langchain.com/docs/how_to/#tools
from typing import Annotated, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool

111111111111111111111111111111111111111111111111111111111
@tool
def multiply(a: int, b: int,c,d) -> int:
    """Multiply two numbers."""
    return a * b


# Let's inspect some of the attributes associated with the tool.
print(multiply.name)
print(multiply.description)
print(multiply.args)

222222222222222222222222222222222222
@tool
async def amultiply(a: int, b: int) -> int:
    """Asynch Multiply two numbers."""
    return a * b

print(amultiply.name)
print(amultiply.description)
print(amultiply.args)

3333333333333333333333333333333
@tool
def multiply_by_max(
    a: Annotated[str, "scale factor"],
    b: Annotated[List[int], "list of ints over which to take maximum"],
) -> int:
    """Multiply a by the maximum of b."""
    return a * max(b)

print(multiply_by_max.args)

multiply_by_max.args_schema.schema()

4444444444444444444444444444444444444444
class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool("multiplication-tool", args_schema=CalculatorInput, return_direct=True)
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Let's inspect some of the attributes associated with the tool.
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)

5555555555555555555555555555555
@tool(parse_docstring=True)
def foo(bar: str, baz: int,aa: int) -> str:
    """The foo.

    Args:
        bar: The bar.
        baz: The baz.
        aa : aaa.
    """
    return bar

foo.args_schema.schema()

666666666666666666666666666666
from langchain_core.tools import StructuredTool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

async def amultiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator = StructuredTool.from_function(func=multiply, coroutine=amultiply)

print(calculator.invoke({"a": 2, "b": 5}))
print(await calculator.ainvoke({"a": 2, "b": 5}))

77777777777777777777777777777777777777
from langchain_core.tools import StructuredTool
from typing import Annotated, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


calculator = StructuredTool.from_function(
    func=multiply,
    name="Calculator",
    description="multiply numbers",
    args_schema=CalculatorInput,
    return_direct=True,
    # coroutine= ... <- you can specify an async method if desired as well
)

print(calculator.invoke({"a": 2, "b": 3}))
print(calculator.name)
print(calculator.description)
print(calculator.args)

8888888888888888888888888888888888888888888888
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
