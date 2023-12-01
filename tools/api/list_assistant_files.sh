#!/bin/bash
curl https://api.openai.com/v1/assistants/$OPENAI_API_ASSISTANT_ID/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"