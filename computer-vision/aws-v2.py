import boto3

def check_aws_env_vars():
    # List of required environment variables
    required_env_vars = [
        'AWS_ACCESS_KEY', 
        'AWS_ACCOUNT_ID', 
        'AWS_REGION', 
        'AWS_SECRET_ACCESS_KEY'
    ]

    # Check if any required environment variable is missing
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

def describe_image(image_path):
    # make sure aws is setup
    check_aws_env_vars()

    # Set up the AWS client
    client = boto3.client('rekognition')

    # Load the image
    with open(image_path, 'rb') as image_file:
        img_bytes = image_file.read()

    # Call Rekognition for label detection
    response_labels = client.detect_labels(Image={'Bytes': img_bytes}, MaxLabels=10, MinConfidence=75)

    # Call Rekognition for facial analysis
    response_faces = client.detect_faces(Image={'Bytes': img_bytes}, Attributes=['ALL'])

    # Call Rekognition for text detection (OCR)
    response_text = client.detect_text(Image={'Bytes': img_bytes})

    # Call Rekognition for moderation labels (e.g., adult content detection)
    response_moderation = client.detect_moderation_labels(Image={'Bytes': img_bytes}, MinConfidence=75)

    # Call Rekognition for celebrity recognition (if relevant)
    response_celebrities = client.recognize_celebrities(Image={'Bytes': img_bytes})

    # Print the detected labels (general objects, scenes, etc.)
    print('Detected labels in image:')
    for label in response_labels['Labels']:
        print(f'{label["Name"]} (Confidence: {label["Confidence"]:.2f}%)')
        if 'Instances' in label:
            for instance in label['Instances']:
                print(f'  - Bounding Box: {instance.get("BoundingBox", "N/A")}')
                print(f'  - Confidence: {instance.get("Confidence", "N/A")}')

    # Print the facial analysis (emotions, gender, age range, etc.)
    if response_faces['FaceDetails']:
        print("\nDetected faces and emotions:")
        for face in response_faces['FaceDetails']:
            print(f'  - Age Range: {face["AgeRange"]["Low"]} - {face["AgeRange"]["High"]}')
            print(f'  - Gender: {face["Gender"]["Value"]}')
            print(f'  - Emotions: {", ".join([emotion["Type"] for emotion in face["Emotions"] if emotion["Confidence"] > 75])}')
            print(f'  - Smile: {"Yes" if face["Smile"]["Value"] else "No"}')

    # Print detected text (OCR)
    if response_text['TextDetections']:
        print("\nDetected text in image:")
        for text in response_text['TextDetections']:
            print(f'  - Text: {text["DetectedText"]}')
            print(f'  - Confidence: {text["Confidence"]:.2f}%')

    # Print moderation labels (e.g., adult content detection)
    if response_moderation['ModerationLabels']:
        print("\nModeration labels detected (for potential unsafe content):")
        for label in response_moderation['ModerationLabels']:
            print(f'{label["Name"]} (Confidence: {label["Confidence"]:.2f}%)')

    # Print detected celebrities
    if response_celebrities['CelebrityFaces']:
        print("\nRecognized celebrities:")
        for celebrity in response_celebrities['CelebrityFaces']:
            print(f'  - Name: {celebrity["Name"]}')
            print(f'  - Confidence: {celebrity["MatchConfidence"]:.2f}%')

# Call the function with your image file
# describe_image('issue-pic.png')

# other test
describe_image('show-me.png')