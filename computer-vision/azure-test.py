from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os

subscription_key = 'your_subscription_key'
endpoint = 'your_endpoint'

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def describe_image(image_path):
    with open(image_path, 'rb') as image_stream:
        description = computervision_client.describe_image_in_stream(image_stream)
    
    # Output descriptions
    if description.captions:
        for caption in description.captions:
            print(f"Description: {caption.text} (Confidence: {caption.confidence:.2f})")
    else:
        print("No description found.")

# Call the function with your image file
describe_image('issue-pic.png')
