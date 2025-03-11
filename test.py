import streamlit as st
import trimesh
import os
from PIL import Image
import plotly.graph_objects as go

os.environ["PYOPENGL_PLATFORM"] = "egl"

# Load and display the logo at the top
logo_path = "assets/image.png"  # Ensure this path is correct for your uploaded logo
st.image(logo_path, width=100)

# Title of the application
st.title("2D Image to 3D Model Viewer")

MODEL_PATH = "assets/img3.glb"  

image_file = st.file_uploader("Upload a 2D Image (PNG, JPG)", type=["png", "jpg", "jpeg"])

if image_file is not None:
    st.image(Image.open(image_file), caption="Uploaded 2D Image", use_column_width=True)

    with st.spinner("Generating 3D model... Please wait!"):
        try:
            import time
            time.sleep(4) 

            mesh = trimesh.load(MODEL_PATH, force='mesh')
            vertices = mesh.vertices
            faces = mesh.faces
            
            if len(vertices) == 0 or len(faces) == 0:
                st.error("The model contains no vertices or faces!")
            else:
                x, y, z = vertices.T
                i, j, k = faces.T

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

                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Error generating the 3D model: {e}")




