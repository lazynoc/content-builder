#!/usr/bin/env python3
"""
Simple test script to check OpenAI API key
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables from parent directory
load_dotenv('../.env')

# Configure OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(f"API Key found: {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY else "No API key found")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say hello"}
        ],
        max_tokens=10
    )
    print("✅ API key is working!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ API key error: {e}") 