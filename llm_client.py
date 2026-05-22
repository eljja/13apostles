import json
import urllib.request
import urllib.error
import time
import os

API_KEY = ""
# 1. Try local .env file first
try:
    with open(os.path.join(os.path.dirname(__file__), ".env"), "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                API_KEY = line.strip().split("=", 1)[1].strip('"\'')
except Exception:
    pass

# 2. Fall back to system environment variables
if not API_KEY:
    API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODELS = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-2.5-pro"
]

class LLMClient:
    def __init__(self, api_key=API_KEY, models=MODELS):
        self.api_key = api_key
        self.models = models

    def generate_content(self, prompt, max_retries=2, timeout=30):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        # Try models in order (main -> fallbacks)
        for model in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            
            for attempt in range(max_retries):
                try:
                    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
                    with urllib.request.urlopen(req, timeout=timeout) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        # Extract text
                        try:
                            text = result['candidates'][0]['content']['parts'][0]['text']
                            print(f"[{model}] OK (attempt {attempt+1})")
                            return text, model
                        except (KeyError, IndexError) as e:
                            print(f"[{model}] Failed to parse response format. Retrying...")
                            time.sleep(1)
                            continue
                except urllib.error.HTTPError as e:
                    print(f"[{model}] HTTP Error {e.code}: {e.reason}")
                    if e.code in [429, 500, 503]: # Rate limit or server error, wait and retry
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        break # Break out of retry loop for this model on 4xx errors
                except urllib.error.URLError as e:
                    print(f"[{model}] URL/Network Error: {str(e.reason)}")
                    time.sleep(2 ** attempt)
                    continue
                except Exception as e:
                    print(f"[{model}] Exception: {str(e)}")
                    time.sleep(1)
                    continue
            
            print(f"Model {model} failed after retries. Falling back to next model...")

        raise Exception("All LLMs failed to generate content.")

if __name__ == "__main__":
    client = LLMClient()
    try:
        response, used_model = client.generate_content("Hello! Are you ready to act as a MAGI?")
        print(f"Response from {used_model}: {response}")
    except Exception as e:
        print(f"Error: {e}")
