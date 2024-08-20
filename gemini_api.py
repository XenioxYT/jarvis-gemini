import pathlib
import google.generativeai as genai
from dotenv import load_dotenv
from prompt import system_prompt
import os

class GeminiAPI:
    def __init__(self):
        load_dotenv()
        self.client = genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        pass

    def process_audio(self, audio_file):
        # Send audio to Gemini API and get text response
        pass


def test_function(test=False):
    """Set a test function to test the gemini api

    Args:
        test (bool, optional): Defaults to False.
    """
    if test:
        return "This works"
    else:
        return "This does not work"

# example function to call the gemini api with audio file:
import time

def process_audio_demo():
    load_dotenv()
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    instructions = "You are a helpful assistant. Keep your responses concise and to the point."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", system_instruction=system_prompt)
    
    start_time = time.time()
    
    response = model.generate_content([
        {
            "mime_type": "audio/ogg",
            "data": pathlib.Path("test_audio1.ogg").read_bytes()
        }],
        tools=[
            {
                "function_declarations": [
                    {
                        "name": "test_function",
                        "description": "A test function that prints 'This works' if the input is True",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "test": {
                                    "type": "boolean",
                                    "description": "Boolean input for the test function"
                                }
                            },
                            "required": ["test"]
                        }
                    }
                ]
            },
        ]
    )
    
    print(response)
    # Process and print the response parts in order
    print("Response parts:")
    for part in response.parts:
        if part.text:
            # Print text content
            print(f"Text: {part.text.strip()}")
        elif hasattr(part, 'function_call'):
            # Print function call details
            fn = part.function_call
            print(f"Function Call: {fn.name}")
            # Convert MapComposite to a regular dictionary
            args_dict = dict(fn.args)
            print(f"Arguments: {args_dict}")
            
            # Execute the function
            if fn.name == "test_function":
                print("Function output: " + test_function(**args_dict))
        else:
            # Handle any unexpected part types
            print(f"Unknown part type: {type(part)}")
        print("---")
    
    end_time = time.time()
    
    print(f"Processing time: {end_time - start_time:.2f} seconds")

process_audio_demo()


"""
GenerateContentResponse(
    done=True,
    iterator=None,
    result=protos.GenerateContentResponse({
      "candidates": [
        {
          "content": {
            "parts": [
              {
                "function_call": {
                  "name": "test_function",
                  "args": {
                    "test": true
                  }
                }
              }
            ],
            "role": "model"
          },
          "finish_reason": "STOP",
          "index": 0,
          "safety_ratings": [
            {
              "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
              "probability": "NEGLIGIBLE"
            },
            {
              "category": "HARM_CATEGORY_HATE_SPEECH",
              "probability": "NEGLIGIBLE"
            },
            {
              "category": "HARM_CATEGORY_HARASSMENT",
              "probability": "NEGLIGIBLE"
            },
            {
              "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              "probability": "NEGLIGIBLE"
            }
          ]
        }
      ],
      "usage_metadata": {
        "prompt_token_count": 73,
        "candidates_token_count": 14,
        "total_token_count": 87
      }
    }),
)
"""