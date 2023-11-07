# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations

import os
import openai
import jinja2
import pathlib

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import RawVectorQuery

from streaming_utils import add_context_to_streamed_response


async def chat_completion(messages: list[dict], stream: bool = False,
                          session_state: any = None, context: dict[str, any] = {}):
    # make a copy of the context and modify it with the retrieved documents
    context = dict(context)

    # call Azure OpenAI with the system prompt and user's question
    response = openai.ChatCompletion.create(
        engine=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        messages=messages, temperature=context.get("temperature", 0.7),
        stream=stream,
        max_tokens=800)

    # add context in the returned response
    if not stream:
        response.choices[0]['context'] = context
    else:
        response = add_context_to_streamed_response(response, context)
    return response
