from dotenv import load_dotenv 
from google import genai

# Loads the env variables
load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# Create a .env file with your key with format of GEMINI_API_KEY=YOUR_KEY
# Get key from Google AI Studio: https://aistudio.google.com/api-keys

# Try Except block to try to get key
try:
    client = genai.Client()
except Exception as e:
    print('Error initializing Gemini Client')
    client = None

# 1. Combind all the json content to summarize into one block
def combine_content(content_to_summarize):

    combined_content = ""
    for json_item in content_to_summarize:
        combined_content += json_item.get('text', '') + "\n\n"
    return combined_content

# 2. Build prompt for the model
def build_prompt(combined_content, summary_length, additional_info):

    # Define the desired summary length for the LLM
    length_instruction = {
        "short": "Write a concise summary in 3-5 sentences.",
        "medium": "Write a detailed summary in 5-8 sentences.",
        "long": "Write an in-depth summary with up to 10 sentences."
    }.get(summary_length.lower(), "Write a concise summary.")

    # Define additional info instruction
    info_instruction = "Also, include a small section of additional, related information on the topic." if additional_info.lower() == "yes" else ""

    # End prompt for the model
    prompt = f"""
    You are an AI Summary Generator. Your task is to summarize the provided content based on the user's requirements.

    **Instructions:**
    1. {length_instruction}
    2. {info_instruction}

    **Content to Summarize:**
    ---
    {combined_content.strip()}
    """

    return prompt

# 3. Function to combine content and build prompt
def combine_and_build(content_to_summarize, summary_length, additional_info):
    combined_content = combine_content(content_to_summarize)
    prompt = build_prompt(combined_content, summary_length, additional_info)
    return combined_content, prompt


# 3. Function to call the gemini to summarize
def call_gemini_summary(content_to_summarize, summary_length, additional_info):

    # Checking if connection to Gemini is there
    if client is None:
        return {"error": "Server Error: Gemini API client not initialized. Check API Key."}, 500
    
    try:
        # Combine content and build prompt
        combined_content, prompt = combine_and_build(
            content_to_summarize, summary_length, additional_info
        )

        # Call the Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.3
            }
        )

        # Format the successful response
        ai_data = {
            "summary_length_requested": summary_length,
            "additional_info_requested": additional_info,
            "summary_text": response.text,
            "source_content_chars": len(combined_content)
        }
        
        return ai_data, 200
    
    # error if it goes over the limits "sourced this online"
    except Exception as e:
        return {"error": f"Server Error (Gemini API): Check API key/rate limits. Details: {str(e)}"}, 500