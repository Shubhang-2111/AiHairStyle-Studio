from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from io import BytesIO
import stripe
import os
from gradio_client import Client, file
import logging
from mangum import Mangum  # Mangum is used to wrap FastAPI for serverless functions (e.g., Vercel)

# Stripe API Keys (replace with your test secret key)
stripe.api_key = "sk_test_51QdPo2R33uCDdxxk2RBi1HhBGbhWcC1w7B7dW0RqM1GVHnq7TfYDqvdmtcBqgXriuGoddpsPGCJqmXeHf9K5rJZ700uAXy1but"

# Initialize FastAPI
app = FastAPI(root_path="/api")

# Initialize Gradio Client
client = Client("AIRI-Institute/HairFastGAN")

# Temporary folder for uploaded files
os.makedirs("temp", exist_ok=True)

# To store generated image paths
generated_images = {}

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def save_upload_file(uploaded_file: UploadFile):
    try:
        return BytesIO(uploaded_file.file.read())
    except Exception as e:
        logging.error(f"Error saving uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail="File saving failed.")

# API Endpoint for processing hair style transfer
@app.post("/process_hair_style")
async def process_hair_style(
    source: UploadFile = File(...), 
    style: UploadFile = File(...), 
    color: UploadFile = File(None)
):
    try:
        logging.debug("Received files: source=%s, style=%s, color=%s", source.filename, style.filename, color.filename if color else "None")

        # Save the uploaded files
        source_path = save_upload_file(source, "temp")
        style_path = save_upload_file(style, "temp")
        color_path = save_upload_file(color, "temp") if color else None

        # Resize the source image using /resize_inner API
        resized_source_path = resize_image(source_path, "/resize_inner")
        if not resized_source_path:
            logging.error("Failed to resize source image")
            return {"error": "Failed to resize the source image."}

        # Resize the style image using /resize_inner_1 API (if provided)
        resized_style_path = resize_image(style_path, "/resize_inner_1")
        if not resized_style_path:
            logging.error("Failed to resize style image")
            return {"error": "Failed to resize the style image."}

        # Resize the color image using /resize_inner_2 API (if provided)
        resized_color_path = resize_image(color_path, "/resize_inner_2") if color_path else None

        # Call the swap_hair API with the resized images
        result = client.predict(
            face=file(resized_source_path),
            shape=file(resized_style_path),
            color=file(resized_color_path) if resized_color_path else None,
            blending="Article",
            poisson_iters=0,
            poisson_erosion=15,
            api_name="/swap_hair"
        )
        logging.debug("Swap hair result: %s", result)

        # Process the result from swap_hair API
        if isinstance(result, tuple) and len(result) == 2:
            image_response, _ = result
            if isinstance(image_response, dict) and image_response.get("visible"):
                result_image_path = image_response.get("value")
                if result_image_path:
                    # Save the generated image and return the session ID for payment
                    session_id = create_payment_session(result_image_path)
                    return {"session_id": session_id}
            else:
                logging.error("Failed to generate the image.")
                return {"error": "Failed to generate the image."}
        else:
            logging.error("Unexpected API response format.")
            return {"error": "Unexpected API response format."}
    except Exception as e:
        logging.error("Error during image processing: %s", str(e))
        return {"error": f"An unexpected error occurred: {e}"}


# Resize image helper function
def resize_image(file_path, api_name):
    result = client.predict(
        img=file(file_path),
        align=["Face", "Shape", "Color"],
        api_name=api_name
    )
    if isinstance(result, str):
        return result
    return None


# Stripe Payment Route
@app.post("/create_payment_session")
def create_payment_session(image_path: str):
    try:
        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Hair Style Image',
                    },
                    'unit_amount': 500,  # $5.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="https://ai-hair-style-studio-6sqw.vercel.app/api/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://ai-hair-style-studio-6sqw.vercel.app/api/cancel",
        )

        # Store the generated image path to be accessed later
        generated_images[session['id']] = image_path

        logging.debug("Stripe session created: %s", session['id'])
        logging.debug("********************************: %s", session['url'])
        # Return the Stripe checkout URL
        return {"session_id": session['id'], "checkout_url": session['url']}
    except Exception as e:
        logging.error("Error creating payment session: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Dictionary to store the image paths against session IDs (use your actual implementation)
@app.get("/success")
def success(session_id: str):
    image_path = generated_images.get(session_id)
    
    if image_path:
        # Serve an HTML page with the image and download option
        return f"""
        <html>
        <head>
            <title>Success</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .container {{
                    text-align: center;
                    background-color: #ffffff;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    width: 80%;
                    max-width: 800px;
                }}
                h1 {{
                    color: #4CAF50;
                    font-size: 2.5em;
                    margin-bottom: 20px;
                }}
                p {{
                    font-size: 1.2em;
                    margin-bottom: 30px;
                    color: #555;
                }}
                .image-container {{
                    max-width: 80%;
                    margin: 0 auto;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                a {{
                    text-decoration: none;
                }}
                button {{
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    font-size: 1.1em;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    margin-top: 20px;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
                .description {{
                    font-size: 1.2em;
                    margin-top: 20px;
                    color: #444;
                    text-align: center;
                    font-weight: 500;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Image Styled Successfully!</h1>
                <p>Your image has been successfully styled. You can now view and download it!</p>
                <div class="image-container">
                    <img src="/view-image?session_id={session_id}" alt="Styled Image">
                </div>
                <div class="description">
                    <p>Click below to download your styled image and share it with friends!</p>
                </div>
                <a href="/download-image?session_id={session_id}" download="styled_image.png">
                    <button>Download Image</button>
                </a>
            </div>
        </body>
        </html>
        """
    else:
        logging.error("Image not found for session_id %s", session_id)
        raise HTTPException(status_code=404, detail="Image not found or payment not completed.")


# Route to serve the image for viewing
@app.get("/view-image")
def view_image(session_id: str):
    image_path = generated_images.get(session_id)
    
    if image_path:
        return FileResponse(image_path, media_type="image/png")
    else:
        logging.error("Image not found for session_id %s", session_id)
        raise HTTPException(status_code=404, detail="Image not found.")


# Route to handle image download
@app.get("/download-image")
def download_image(session_id: str):
    image_path = generated_images.get(session_id)
    
    if image_path:
        return FileResponse(image_path, media_type="image/png", filename="styled_image.png")
    else:
        logging.error("Image not found for session_id %s", session_id)
        raise HTTPException(status_code=404, detail="Image not found.")


# Wrap the FastAPI app for serverless use with Mangum
handler = Mangum(app)
