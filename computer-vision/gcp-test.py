from google.cloud import vision
import io

def describe_image(image_path):
    client = vision.ImageAnnotatorClient()

    # Load the image
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Perform label detection on the image
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # Print the descriptions
    print('Labels in the image:')
    for label in labels:
        print(f'{label.description} (Score: {label.score})')

    if response.error.message:
        raise Exception(f'{response.error.message}')

# Call the function with your image file
describe_image('issue-pic.png')
