import streamlit as st
import requests
import base64
import os
from PIL import Image
from io import BytesIO
import time
<<<<<<< HEAD
import tempfile
import trimesh
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenGL platform
=======
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()  # This will automatically load variables from a .env file

# Set the platform for OpenGL (needed for rendering 3D models)
>>>>>>> f40436a2afb66782036e7d95002dc5ac5472a378
os.environ["PYOPENGL_PLATFORM"] = "egl"

# Load API key from environment variables
API_KEY = os.getenv("MESHY_API_KEY")

if not API_KEY:
    st.error("API key is missing. Please set the MESHY_API_KEY in your environment.")
    st.stop()

<<<<<<< HEAD
# Convert image to base64
def image_to_base64(image_file):
    image = Image.open(image_file)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Send image to Meshy AI and extract task ID
def send_to_meshy(image_file):
    image_base64 = image_to_base64(image_file)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
=======
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
>>>>>>> f40436a2afb66782036e7d95002dc5ac5472a378

    data = {
        "image_url": f"data:image/jpeg;base64,{image_base64}",
        "enable_pbr": True,
        "should_remesh": True,
        "should_texture": True
    }

    try:
        response = requests.post(
            "https://api.meshy.ai/openapi/v1/image-to-3d", 
            json=data, 
            headers=headers
        )

        if response.status_code in [200, 202]:
            result = response.json()
            model_id = result.get("task_id") or result.get("result") or result.get("id")
            if not model_id:
                st.error("Failed to retrieve model ID from response.")
                return None
            return model_id

        st.error(f"Failed to send image. Error: {response.status_code} - {response.text}")
        return None

    except Exception as e:
        st.error(f"Failed to send image to Meshy AI: {e}")
        return None

# Check progress dynamically
def check_progress(model_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    url = f"https://api.meshy.ai/openapi/v1/image-to-3d/{model_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()

            progress = result.get("progress", 0)
            status = result.get("status", "pending").lower()
            if status in ["completed", "finished", "succeeded"]:
                model_urls = result.get("model_urls", {})
                glb_url = model_urls.get("glb")
                return True, 100, glb_url
            elif status in ["failed", "error"]:
                st.error("Model generation failed.")
                return False, 0, None

            return False, int(progress), None
        
        st.error(f"Failed to check progress. Status: {response.status_code}")
        return False, 0, None

    except Exception as e:
        st.error(f"Failed to check progress: {e}")
        return False, 0, None

# Visualize the 3D model using Plotly
def visualize_3d_model(glb_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as tmpfile:
        tmpfile.write(glb_data)
        tmpfile.close()
        try:
<<<<<<< HEAD
            mesh = trimesh.load_mesh(tmpfile.name)
            if mesh.is_empty:
                st.error("The 3D model is empty or invalid.")
            else:
                # Extract vertices and faces for Plotly visualization
                vertices = mesh.vertices
                faces = mesh.faces
                x, y, z = vertices.T
                i, j, k = faces.T

                # Create Plotly 3D Mesh
                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=x, y=y, z=z,
                        i=i, j=j, k=k,
                        color='lightblue',
                        opacity=0.50
                    )
                ])

                fig.update_layout(
                    scene=dict(
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        zaxis=dict(visible=False)
                    ),
                    margin=dict(l=0, r=0, t=0, b=0)
                )

                # Display the 3D plot
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Failed to visualize 3D model: {e}")

# Upload 2D Image
st.title("2D Image to 3D Model Converter")
image_file = st.file_uploader("Upload a 2D Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if image_file:
    st.image(Image.open(image_file), caption="Uploaded Image", use_container_width=True)

    if st.button("Generate 3D Model"):
        with st.spinner("Sending image to Meshy AI..."):
            model_id = send_to_meshy(image_file)
        
        if model_id:
            st.write("Generating 3D model...")

            # Initialize progress bar
            progress_bar = st.progress(0)

            # Polling loop to check progress
            model_ready = False
            glb_url = None
            glb_data = None  # To store the GLB data
            while not model_ready:
                model_ready, progress, glb_url = check_progress(model_id)
                progress_bar.progress(progress)
                time.sleep(2)  # Poll every 2 seconds

                # Check if model is ready or there was an error
                if model_ready or progress == 100:
                    break  # Exit loop if model is ready or completed

            if model_ready and glb_url:
                st.success("3D model generation completed!")

                # Fetch the GLB file data
                try:
                    glb_response = requests.get(glb_url)
                    if glb_response.status_code == 200:
                        glb_data = glb_response.content
                        visualize_3d_model(glb_data)  # Visualize the 3D model
                    else:
                        st.error("Failed to retrieve GLB file.")
                except Exception as e:
                    st.error(f"Error fetching the GLB file: {e}")

            else:
                st.error("Failed to retrieve GLB URL.")
=======
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
>>>>>>> f40436a2afb66782036e7d95002dc5ac5472a378
