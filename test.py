import streamlit as st
import requests
import base64
import os
from PIL import Image
from io import BytesIO
import time
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()  # This will automatically load variables from a .env file

# Set the platform for OpenGL (needed for rendering 3D models)
os.environ["PYOPENGL_PLATFORM"] = "egl"

# Load and display the logo at the top
logo_path = "assets/image.png"  # Ensure this path is correct for your uploaded logo
st.image(logo_path, width=100)

# Title of the application
st.title("2D Image to 3D Model Viewer")

# API key from environment variable
API_KEY = os.getenv("MESHY_API_KEY")  # Get the API key from environment variable

# Ensure API key is set
if not API_KEY:
    st.error("API key is missing. Please provide your Meshy AI API key.")
    st.stop()

# Function to convert image to base64 encoding
def image_to_base64(image_file):
    # Open image and ensure it's in RGB mode to avoid issues with transparency
    image = Image.open(image_file)
    
    # If the image has an alpha channel (RGBA), convert it to RGB
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    buffered = BytesIO()
    image.save(buffered, format="JPEG")  # Save as JPEG (or you can choose PNG if needed)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to send image to Meshy AI and get 3D model URL
def send_to_meshy(image_file):
    # Convert the image to base64 format
    image_base64 = image_to_base64(image_file)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",  # Set the appropriate content type for the request
    }

    data = {
        "image_url": f"data:image/jpeg;base64,{image_base64}",
        "enable_pbr": True,
        "should_remesh": True,
        "should_texture": True
    }

    try:
        # Make a POST request to Meshy AI to generate the 3D model
        response = requests.post("https://api.meshy.ai/openapi/v1/image-to-3d", 
                                 json=data, 
                                 headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            model_id = result.get("result", None)
            if model_id:
                return model_id
            else:
                st.error("No model ID returned from Meshy AI.")
                return None
        else:
            st.error(f"Error from Meshy AI: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

# Function to check the progress of the model generation
def check_progress(model_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    url = f"https://api.meshy.ai/openapi/v1/image-to-3d/{model_id}"

    try:
        # Poll the status of the 3D model generation
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            progress = result.get("progress", 0)
            status = result.get("status", "pending")
            if status == "completed":
                return True, progress  # Completed, return True and progress
            else:
                return False, progress  # Not completed, return False and current progress
        else:
            st.error(f"Error fetching progress: {response.status_code} - {response.text}")
            return False, 0
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return False, 0

# Function to retrieve the 3D model using the model_id
def get_3d_model(model_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    url = f"https://api.meshy.ai/openapi/v1/image-to-3d/{model_id}/download"
    
    try:
        # Get the download URL of the 3D model in .glb format
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            model_data = response.content
            return model_data
        else:
            st.error(f"Error fetching 3D model: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

# File uploader for 2D image
image_file = st.file_uploader("Upload a 2D Image (PNG, JPG)", type=["png", "jpg", "jpeg"])

if image_file is not None:
    st.image(Image.open(image_file), caption="Uploaded 2D Image", use_container_width=True)

    with st.spinner("Generating 3D model... Please wait!"):
        try:
            # Send the image to Meshy AI and get the model ID
            model_id = send_to_meshy(image_file)
            
            if model_id:
                # Show progress bar and poll for completion
                progress_bar = st.progress(0)  # Initialize the progress bar
                st.write("Generating 3D model, please wait...")

                model_ready = False
                while not model_ready:
                    model_ready, progress = check_progress(model_id)
                    progress_bar.progress(progress)  # Update progress bar
                    time.sleep(5)  # Wait before checking the status again

                # Once model generation is completed, get the model
                model_data = get_3d_model(model_id)
                
                if model_data:
                    # Display the 3D model (GLB file) download button
                    st.success("3D model generated successfully!")
                    st.download_button(
                        label="Download 3D Model",
                        data=model_data,
                        file_name="3d_model.glb",
                        mime="model/gltf-binary"
                    )

        except Exception as e:
            st.error(f"Error generating the 3D model: {e}")
