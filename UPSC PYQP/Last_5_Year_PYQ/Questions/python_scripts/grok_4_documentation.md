# Grok 4 API Documentation Reference

## 🚀 Model Overview

**Grok 4** - Our latest and greatest flagship model, offering unparalleled performance in natural language, math and reasoning - the perfect jack of all trades.

## 📊 Model Specifications

### Basic Info
- **Model Name**: `grok-4-0709`
- **Aliases**: `grok-4`, `grok-4-latest`
- **Region**: `us-east-1`
- **Context Window**: 256,000 tokens

### Capabilities
- ✅ **Function calling** - Connect the xAI model to external tools and systems
- ✅ **Structured outputs** - Return responses in a specific, organized formats
- ✅ **Reasoning** - The model thinks before responding

## 💰 Pricing (per million tokens)

| Token Type | Price |
|------------|-------|
| **Input** | $3.00 |
| **Cached input** | $0.75 |
| **Output** | $15.00 |

**Note**: You are charged for each token used when making calls to our API.
**Cached input tokens** can significantly reduce your costs.

## ⚡ Rate Limits

- **Requests per minute**: 120
- **Tokens per minute**: 200,000

## 🔧 Quickstart Example

```python
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key="<YOUR_XAI_API_KEY_HERE>")

chat = client.chat.create(model="grok-4-0709", temperature=0)
chat.append(system("You are a PhD-level mathematician."))
chat.append(user("What is 2 + 2?"))

response = chat.sample()
print(response.content)
```

## 📚 Key Features

### 1. **Function Calling**
Connect the xAI model to external tools and systems.

### 2. **Structured Outputs**
Return responses in a specific, organized formats.

### 3. **Reasoning**
The model thinks before responding.

## 🌐 API Endpoints

### Base URL
- **Region**: `us-east-1`

### Available Endpoints
- Chat completions
- Messages (Anthropic compatible)
- Image generations
- API key management
- Model listing
- Tokenization
- Deferred chat completions

## 🔗 Resources

- **Community Integrations**: Available
- **xAI API Developer Discord**: Available
- **Email Support**: xAI Support
- **Service Status**: Available

## 📖 Documentation Sections

### Getting Started
- Overview
- Introduction
- The Hitchhiker's Guide to Grok
- Models and Pricing
- What's New?
- Key Information
- Billing
- Consumption and Rate Limits
- Regional Endpoints
- Usage Explorer
- Using Management API
- Migrating to New Models
- Debugging Errors

### Guides
- Chat
- Chat with Reasoning
- Live Search
- Image Understanding
- Image Generations
- Stream Response
- Deferred Chat Completions
- Asynchronous Requests
- Function Calling
- Structured Outputs
- Fingerprint
- Migration from Other Providers

### API Reference
- REST API Reference
- Management API Reference
- Community Integrations
- FAQ - General
- FAQ - xAI API
- Accounts
- Billing
- Team Management
- Security
- FAQ - Grok Website / Apps

## 💡 Cost Optimization Tips

1. **Use Cached Input**: $0.75 vs $3.00 per million tokens
2. **Batch Requests**: Reduce API calls by processing multiple items together
3. **Optimize Prompts**: Remove redundant instructions
4. **Monitor Usage**: Track token consumption with Usage Explorer

## 🚨 Important Notes

- **Higher Context Pricing**: Different rates for requests exceeding 128k context window
- **Token Counting**: Charged for each token used
- **Rate Limits**: 120 requests/minute, 200k tokens/minute
- **Regional Endpoints**: Ensure you're using the correct region for optimal performance 