import boto3

def describe_image(image_path):
    # Set up the AWS client
    client = boto3.client('rekognition')

    # Load the image
    with open(image_path, 'rb') as image_file:
        img_bytes = image_file.read()

    # Call Rekognition API
    response = client.detect_labels(Image={'Bytes': img_bytes}, MaxLabels=10, MinConfidence=75)

    # Print the detected labels
    print('Detected labels in image:')
    for label in response['Labels']:
        print(f'{label["Name"]} (Confidence: {label["Confidence"]:.2f}%)')

# Call the function with your image file
describe_image('issue-pic.png')
