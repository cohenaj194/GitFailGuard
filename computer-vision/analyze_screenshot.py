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
            model="gpt-4", # "gpt-3.5-turbo", # for testing
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

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_screenshot.py image_path 'Your analysis prompt here'")
        sys.exit(1)

    image_path = sys.argv[1]
    user_prompt = sys.argv[2]

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
