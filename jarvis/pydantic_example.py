
from pydantic import BaseModel

class InputModel(BaseModel):
    name : str
    age : int
    weight : float
    birth_date : datetime

def my_function(input_data : InputModel):
    return (f"name : {input_data.name}, age: {input_data.age}, weight: {input_data.weight}, birth_date; {input_data.birth_date}")

data = InputModel(name = '1111'
                  ,age = 32
                  ,weight = 12.3
                  ,birth_date = '1981-10-25T17:33:15Z' )
my_function(data)
