#!/bin/bash
curl "https://api.openai.com/v1/assistants" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
    "instructions": "You are a helpful assistant that provides instructions for building software projects from source.",
    "name": "C3P0-Assistant",
    "tools": [{"type": "retrieval"}],
    "model": "gpt-4-1106-preview"
  }'
