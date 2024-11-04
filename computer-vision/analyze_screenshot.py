import pytesseract
from PIL import Image
import openai
import sys
import os

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    print("Error: OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

def extract_text_from_image(image_path):
    # Open the image file
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        sys.exit(1)

    # Use pytesseract to extract text
    text = pytesseract.image_to_string(image)
    return text

def analyze_text_with_llm(text, user_prompt):
    # Combine user prompt with the extracted text
    full_prompt = f"{user_prompt}\n\nExtracted Text:\n{text}"

    # Call the OpenAI ChatCompletion API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4", # for better results
            # model="gpt-3.5-turbo", # for testing
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error with OpenAI API request: {e}")
        sys.exit(1)


def advanced_prompt():
    # Open the file in read mode
    with open('advanced-o1-prompt.txt', 'r') as file:
        # Read the contents of the file and store it in a string
        file_contents = file.read()
    # Advanced prompt with additional context
    return file_contents

def main():
    if sys.argv[1].lower() in ["-h","--help","help"]:
        print("Usage: python analyze_screenshot.py image_path 'Your analysis prompt here'")
        sys.exit(0)

    # Use 'or' to provide default values if sys.argv doesn't have enough arguments
    image_path = sys.argv[1] if len(sys.argv) > 1 else "shakebeer.png"
    user_prompt = sys.argv[2] if len(sys.argv) > 2 else advanced_prompt() # "Summarize what this picture is"

    print(f"Image path: {image_path}")
    print(f"User prompt: {user_prompt}")
    print("\n\n===== Processing Image and Analyzing with LLM =====\n\n")

    # Extract text from the image
    extracted_text = extract_text_from_image(image_path)

    if not extracted_text.strip():
        print("No text found in the image.")
        sys.exit(1)

    # Analyze the extracted text with the LLM
    analysis = analyze_text_with_llm(extracted_text, user_prompt)

    print("\nAnalysis:")
    print(analysis)

if __name__ == "__main__":
    main()
