import os
import json
import pathlib
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from prompt import system_prompt
from dotenv import load_dotenv
import pickle
import random
import threading
from tools import Tools

load_dotenv()

MAX_RETRIES = 2
RETRY_DELAY = 3

class GeminiAPI:
    def __init__(self):
        print("Initializing GeminiAPI...")
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.history_file = 'conversation_history.pkl'
        self._load_system_prompt()
        self._create_model()
        self.max_history_length = 13  # Set the maximum number of messages to keep
        print("GeminiAPI initialized.")

    def _load_system_prompt(self):
        with open('prompt.py', 'r') as f:
            exec(f.read())
        self.system_prompt = system_prompt

    def _create_model(self):
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 4096,
            "response_mime_type": "text/plain",
        }
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY: HarmBlockThreshold.BLOCK_NONE,
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=self.system_prompt,
            safety_settings=safety_settings,
            tools=Tools.get_available_tools()
        )
        # print(self.model._tools.to_proto())

    def process_audio(self, audio_file, tts_engine=None):
        return self.generate_response(audio_file, input_type="audio", tts_engine=tts_engine)
    
    def process_text(self, text, tts_engine=None):
        return self.generate_response(text, input_type="text", tts_engine=tts_engine)

    def generate_response(self, input_data, input_type="text", tts_engine=None):
        # Load conversation history from file
        if os.path.exists(self.history_file):
            with open(self.history_file, 'rb') as f:
                history = pickle.load(f)
        else:
            history = []

        # Trim history while ensuring it starts with a user or model message
        trimmed_history = []
        for message in reversed(history):
            if not trimmed_history or 'function_response' not in message.parts[0]:
                trimmed_history.insert(0, message)
                if len(trimmed_history) >= self.max_history_length:
                    break
            elif trimmed_history:
                trimmed_history.insert(0, message)

        # Start chat session with system prompt and trimmed history
        chat_session = self.model.start_chat(history=trimmed_history)

        # Prepare input based on type
        if input_type == "audio":
            content = [
                {
                    "mime_type": "audio/wav",
                    "data": pathlib.Path(input_data).read_bytes()
                }
            ]
        else:
            content = input_data

        # Send message and process response
        try:
            response = chat_session.send_message(content)
            total_tokens = response.usage_metadata.total_token_count
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            
            for retry in range(MAX_RETRIES):
                print(f"Retrying ({retry + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                
                try:
                    response = chat_session.send_message(content)
                    total_tokens = response.usage_metadata.total_token_count
                    break  # Break out of the retry loop if successful
                except Exception as e:
                    print(f"Error generating response during retry {retry + 1}: {str(e)}")
            else:  # Execute if the loop completes without breaking
                print("Max retries reached. Setting response to 'there was an error'.")
                response = genai.protos.ChatResponse(
                    parts=[genai.protos.Part(text="It seems there was an error, please try again later.")]
                )
                total_tokens = 0

        print("_" * 100)
        print(f"Total token count: {total_tokens}")
        print("_" * 100)
        
        chat_local_history = []

        def process_part(part):
            if part.text:
                chat_local_history.append(part.text.strip())
                
                # Send the text to the TTS engine in a separate thread
                if tts_engine:
                    # Remove symbols that TTS would read out as full characters
                    cleaned_text = part.text.strip()
                    for symbol in ['*', '#', '@', '^', '~', '`', '|']:
                        cleaned_text = cleaned_text.replace(symbol, '')
                    
                    # Remove emojis
                    import re
                    emoji_pattern = re.compile("["
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U00002702-\U000027B0"
                        u"\U000024C2-\U0001F251"
                        "]+", flags=re.UNICODE)
                    cleaned_text = emoji_pattern.sub(r'', cleaned_text)
                    
                    # Remove extra whitespace
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                    
                    print(cleaned_text)
                    threading.Thread(target=tts_engine.speak, args=(cleaned_text,)).start()
                    
            elif hasattr(part, 'function_call'):
                fn = part.function_call
                args_dict = dict(fn.args)
                print(f"Function call: {fn.name} with arguments: {args_dict}")
                result = Tools.call_function(fn.name, **args_dict)
                print(f"Function output: {result}")
                
                function_responses.append(genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fn.name,
                        response={'result': result}
                    )
                ))

        while True:
            function_responses = []
            for part in response.parts:
                process_part(part)

            if function_responses:
                # Send all function responses back to the model
                response = chat_session.send_message(
                    genai.protos.Content(parts=function_responses)
                )
            else:
                # If no function calls were made, exit the loop
                break

        # Save updated history using chat_session.history
        with open(self.history_file, 'wb') as f:
            pickle.dump(chat_session.history, f)

        return chat_local_history
    
def test_gemini_api():
    gemini_api = GeminiAPI()
    response = gemini_api.generate_response("Try a different location, maybe a city?")
    print(response)

if __name__ == "__main__":
    test_gemini_api()