import json
import urllib.request
import urllib.error
import time

API_KEY = "AIzaSyAfYzrSyZdX9_t_c1zNntg1Y6zU2-9SNjA"
MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview"
]

class LLMClient:
    def __init__(self, api_key=API_KEY, models=MODELS):
        self.api_key = api_key
        self.models = models

    def generate_content(self, prompt, max_retries=3):
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
                    with urllib.request.urlopen(req) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        # Extract text
                        try:
                            text = result['candidates'][0]['content']['parts'][0]['text']
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
