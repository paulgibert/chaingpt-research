#!/bin/bash
# $1: Assistant ID
# $2: File ID
curl https://api.openai.com/v1/assistants/$1/files/$2 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1" \
  -X DELETE