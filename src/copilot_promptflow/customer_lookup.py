import os

from promptflow import tool

from api import get_customer_info

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def customer_lookup(customerId: int) -> str:
  response = get_customer_info(customerId)
  return response
