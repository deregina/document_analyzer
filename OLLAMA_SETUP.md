# Ollama Setup Guide

This application now uses **Ollama** - an open-source language model that runs locally on your machine. No API keys or credits needed!

## Step 1: Install Ollama

### macOS
```bash
# Using Homebrew (recommended)
brew install ollama

# Or download from: https://ollama.ai/download
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download the installer from: https://ollama.ai/download

## Step 2: Start Ollama

After installation, start the Ollama service:

```bash
ollama serve
```

This will start Ollama in the background. Keep this running while using the application.

## Step 3: Download a Model

You need to download at least one language model. Recommended models:

### Option 1: Llama 3.2 (Recommended - Good balance of speed and quality)
```bash
ollama pull llama3.2
```

### Option 2: Llama 3.1 (Larger, better quality)
```bash
ollama pull llama3.1
```

### Option 3: Mistral (Fast and efficient)
```bash
ollama pull mistral
```

### Option 4: Qwen2.5 (Good multilingual support)
```bash
ollama pull qwen2.5
```

## Step 4: Configure the Application (Optional)

By default, the application uses `llama3.2`. To use a different model, add this to your `.env` file:

```env
OLLAMA_MODEL=llama3.2
```

Or change it to any model you've downloaded:
```env
OLLAMA_MODEL=mistral
OLLAMA_MODEL=qwen2.5
```

## Step 5: Verify Installation

Test that Ollama is working:

```bash
ollama list
```

This should show your downloaded models.

You can also test with:
```bash
ollama run llama3.2 "Hello, how are you?"
```

## Troubleshooting

### Ollama is not running
- Make sure `ollama serve` is running
- Check if Ollama is accessible: `curl http://localhost:11434/api/tags`

### Model not found error
- Make sure you've pulled the model: `ollama pull llama3.2`
- Check available models: `ollama list`

### Performance issues
- Smaller models (like llama3.2) are faster but less capable
- Larger models (like llama3.1) are slower but more accurate
- Make sure you have enough RAM (models need 4-8GB+ depending on size)

## Available Models

Popular models you can use:
- `llama3.2` - Fast, good quality (recommended)
- `llama3.1` - Better quality, slower
- `mistral` - Fast and efficient
- `qwen2.5` - Good multilingual support
- `phi3` - Very fast, smaller model
- `gemma2` - Google's open model

See all available models: https://ollama.ai/library

## Notes

- **No internet required** after downloading models (runs completely offline)
- **No API keys needed** - completely free and open source
- **Privacy** - All processing happens locally on your machine
- **First run** - Models are downloaded once, then cached locally

