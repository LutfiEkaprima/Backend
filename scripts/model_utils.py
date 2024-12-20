import tensorflow as tf
import numpy as np
from pathlib import Path
from PIL import Image
import io

# Load the model once at startup
model_path = Path(__file__).resolve().parent.parent / "model" / "model.h5"
model = tf.keras.models.load_model(model_path)

# Define class labels (update based on your trained model)
class_labels = [
    "beans", "beef", "bell pepper", "bread", "butter", "cabbage", "carrot",
    "cheese", "chicken", "egg", "eggplant", "fish", "onion", "pasta",
    "peanut", "pork", "potato", "rice", "shrimp", "tofu", "tomato", "zucchini"
]

def preprocess_image(image_bytes):
    """
    Preprocess the uploaded image for the CNN model.
    :param image_bytes: The raw image bytes.
    :return: Preprocessed image ready for prediction.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((128, 128))  # Match your model's input size
    image = np.array(image) / 255.0  # Normalize to [0, 1] range
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image


def predict_ingredient(image_bytes):
    """
    Predict the ingredient in the image.
    :param image_bytes: The raw image bytes.
    :return: Predicted ingredient and confidence score.
    """
    image = preprocess_image(image_bytes)
    predictions = model.predict(image)
    predicted_index = np.argmax(predictions)
    confidence = predictions[0][predicted_index]
    predicted_label = class_labels[predicted_index]
    return predicted_label, confidence
