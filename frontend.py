import gradio as gr
import requests
import time
import webbrowser
from PIL import Image
import json

def swap_hair(source, style, color=None):
    loading_message = "Processing your request... Please wait."
    yield loading_message, ""
    
    files = {"source": open(source, "rb"), "style": open(style, "rb")}
    if color:
        files["color"] = open(color, "rb")

    try:
        response = requests.post("https://ai-hair-style-studio.vercel.app/api/process_hair_style", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"Response JSON: {result}")

            if 'session_id' in result and 'checkout_url' in result['session_id']:
                checkout_url = result['session_id']['checkout_url']
                webbrowser.open(checkout_url, new=2)
                yield "Request processed! Redirecting you to Stripe...", f"Click here to complete your payment: <a href='{checkout_url}' target='_blank'>{checkout_url}</a>"
            else:
                yield "Error: 'checkout_url' not found in the response.", ""
        else:
            yield f"Error: Request failed with status code {response.status_code}", ""
    except Exception as e:
        yield f"An error occurred: {str(e)}", ""

# Updated CSS with separate background colors for containers and improved text visibility
custom_css = """
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    body {
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        background: linear-gradient(to right, #e0f7fa, #ffccbc);
        color: #333;
    }
    header {
        background-color: #ff7043;
        color: white;
        padding: 20px 0;
        text-align: center;
        font-size: 2.5em;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        border-bottom: 5px solid #ff5722;
        animation: fadeIn 2s ease;  /* Adding fade-in animation */
    }
    header img {
        height: 70px; /* Adjust the height as needed */
        width: auto;  /* Automatically adjust the width to maintain aspect ratio */
        display: inline-block; /* Ensure the logo is inline with the header text */
        vertical-align: middle; /* Align the logo with the text vertically */
        margin-right: 15px; /* Add space between the logo and the header text */
    }

    header h1 {
        display: inline-block;
        margin: 0;
        font-size: 2.5em;
        animation: fadeIn 2s ease-in-out;  /* Adding fade-in for logo */
    }
    header p {
        font-size: 1.2em;
        margin-top: 5px;
        font-weight: 300;
        color: #fbe9e7;
        animation: fadeIn 3s ease-in-out;  /* Adding fade-in for subtitle */
    }
    .gradio-container {
        width: 85%;
        margin: 40px auto;
        background: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #ffffff 50%, #ffe0b2 50%);
    }
    .animated-text {
        font-size: 36px;
        color: #2f2f2f;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 600;
        animation: fadeIn 3s ease-in-out;  /* Adding fade-in animation for text */
        background: linear-gradient(90deg, #ff7043, #ff5722);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .dark-welcome-container {
        background-color: #333;
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        animation: fadeIn 2s ease;
    }
    .dark-welcome-text {
        font-size: 20px;
        color: #ffccbc; /* Dark orange for contrast */
        margin-bottom: 15px;
        text-align: center;
        font-weight: 600;
    }
    .gr-markdown {
        font-size: 20px;
        color: #ff7043;
        margin-bottom: 30px;
        text-align: center;
    }
    .input-section {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 25px;
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .input-section .gradio-input {
        flex: 1;
    }
    .gradio-button {
        background: linear-gradient(45deg, #ff7043, #ff5722);
        color: white;
        padding: 14px 30px;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        cursor: pointer;
        transition: background 0.3s ease, transform 0.2s ease;
    }
    .gradio-button:hover {
        background: linear-gradient(45deg, #ff5722, #e64a19);
        transform: scale(1.05);
    }
    .gradio-output {
        margin-top: 25px;
        background-color: #ffe0b2;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .output-container {
        display: flex;
        justify-content: center;
        gap: 25px;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .output-container img {
        max-width: 100%;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    
    footer {
        background-color: #333;
        color: white;
        padding: 40px;
        text-align: center;
        border-top: 5px solid #ff5722;
        font-size: 16px;
    }
    footer a {
        color: #ffccbc;
        text-decoration: none;
        font-weight: bold;
    }
    footer a:hover {
        text-decoration: underline;
    }
    footer .social-icons {
        margin-top: 20px;
        display: flex;
        justify-content: center; /* Center the icons horizontally */
        gap: 15px;
    }
    footer .social-icons img {
        height: 30px;
        margin: 0 15px;
        vertical-align: middle;
        transition: transform 0.3s ease;
    }
    footer .social-icons img:hover {
        transform: scale(1.2);
    }
    @media (max-width: 768px) {
        .input-section {
            flex-direction: column;
        }
        .gradio-container {
            padding: 20px;
        }
        footer .social-icons img {
            height: 25px;
            margin: 0 10px;
        }
    }
</style>
"""

header_html = """
<header>
    <p>Transform your hairstyle with AI. Upload an image, choose your style, and let AI do the magic!</p>
</header>
"""

footer_html = """
<footer>
    <p>© 2025 AiHairStyleStudio. All rights reserved.</p>
    <div class="social-icons">
        <a href="https://www.facebook.com/aihairstylestudio" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" alt="Facebook"></a>
        <a href="https://www.instagram.com/aihairstylestudio" target="_blank"><img src="https://img.icons8.com/fluency/48/000000/instagram-new.png" alt="Instagram"></a>
        <a href="https://www.tiktok.com/@aihairstylestudio" target="_blank"><img src="https://img.icons8.com/color/48/000000/tiktok--v1.png" alt="TikTok"></a>
        <a href="https://www.youtube.com/@AIHairstyleStudio" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" alt="YouTube"></a>
        <a href="https://uk.pinterest.com/aihairstylestudio/" target="_blank"><img src="https://img.icons8.com/color/48/000000/pinterest--v1.png" alt="Pinterest"></a>
    </div>
    <p><a href="https://aihairsytlestudio.com">Visit our Website</a></p>
</footer>
"""

dark_welcome_html = """
<div class="dark-welcome-container">
    <h2 class="dark-welcome-text">Welcome to AiHairStyleStudio</h2>
    <p class="dark-welcome-text">Use cutting-edge AI to swap hairstyles between images. Upload your own images to get started.</p>
</div>
"""

# Gradio UI with updated header, footer, and layout
iface = gr.Blocks(css=custom_css)

with iface:
    gr.HTML(f"""
    <head>
        <title>AiHairStyleStudio</title>  <!-- Set the tab name -->
        <link rel="icon" href="{"logo.webp"}" type="image/x-icon">  <!-- Set the favicon -->
    </head>
    """)
    gr.HTML(header_html)  # Add header
    gr.HTML(dark_welcome_html)  # Add dark welcome container
    with gr.Column():
        with gr.Row(variant="panel", elem_id="input-section"):
            source_image = gr.Image(type="filepath", label="Source Image", elem_id="input-source")
            style_image = gr.Image(type="filepath", label="Style Image", elem_id="input-style")
            color_image = gr.Image(type="filepath", label="Color Image (Optional)", elem_id="input-color")
        
        submit_btn = gr.Button("Submit", elem_id="submit-button")
        
        status_output = gr.Textbox(type="text", label="Status", elem_id="output-status", interactive=False)
        link_output = gr.HTML(label="Stripe Payment Link", elem_id="output-link")

        submit_btn.click(fn=swap_hair, inputs=[source_image, style_image, color_image], outputs=[status_output, link_output])

    gr.HTML(footer_html)  # Add footer

iface.launch(share=True)
