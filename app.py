import os
import requests
import io
from PIL import Image
import streamlit as st
from groq import Groq








st.set_page_config(layout="wide")


with st.sidebar:
    st.title("API Key Configuration")
    huggingface_api_key = st.text_input("Enter Hugging Face API Key", type="password")
    groq_api_key = st.text_input("Enter Groq API Key", type="password")
    
    if not huggingface_api_key or not groq_api_key:
        st.warning("Please enter both API keys to proceed.")
        


def query_image_generation(payload,api_key):
    
    API_URL = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Check for HTTP errors
    if response.status_code != 200:
        st.error("Image generation failed: " + response.text)
        return None
    
    # Check if response is JSON (likely contains metadata or image URL)
    if response.headers.get('content-type') == 'application/json':
        response_json = response.json()
        st.write("Response JSON:", response_json)  # Debugging info
        if 'generated_image_url' in response_json:
            return response_json['generated_image_url']  # Return URL if available
    
    return response.content  # Assume raw image data otherwise

# Google Gemini API setup

def generate_blog_with_groq(blog_title, keywords, num_words,api_key):
    
    client = Groq(api_key=api_key)
    
    prompt = (
        f"Generate a comprehensive, engaging blog post relevant to the given title \"{blog_title}\" "
        f"and keywords \"{keywords}\", making sure to incorporate these words in the blog. "
        f"The blog should be approximately {num_words} words in length, suitable for an online audience. "
        f"Ensure the content is original, informative, and maintains tone throughout."
    )
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",  # Use Groq's available model (replace with actual model if different)
    )
    
    # Extract the response text from the completion object
    return chat_completion.choices[0].message.content

# Streamlit App Configuration

st.title("BlogMate: Your AI Co-Writer for Seamless Blogging")
st.subheader("Empower your creativity with AI-driven insights, personalized content suggestions, and smart editing tools, designed to make blog writing effortless and engaging.")

with st.sidebar:
    st.title("Input Your Blog Details")
    st.subheader("Enter details of Blog you want to generate")
    
    blog_title = st.text_input("Blog title")
    keywords = st.text_area("Enter keywords (comma separated)")
    num_words = st.slider("No of words", min_value=250, max_value=2000, step=250)
    num_images = st.number_input("No of Images", min_value=1, max_value=5, step=1)
    submit_button = st.button("Generate Blog and Image")

if submit_button:
    if blog_title and keywords and huggingface_api_key and groq_api_key:
        # Generate Image First
        st.title("Generated Image:")
        image_input = f"{blog_title}"  # Using blog title to generate related image
        image_bytes = query_image_generation({"inputs": image_input},huggingface_api_key)
        
        if image_bytes:
            try:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Generated Image", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {e}")
        else:
            st.error("Image generation failed.")
        
        # Generate Blog Content
        blog_content = generate_blog_with_groq(blog_title, keywords, num_words,groq_api_key)

        # Display the blog content after image
        st.title("Your Blog Post:")
        st.write(blog_content)
