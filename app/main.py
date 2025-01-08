from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import stripe
import shutil
import os
from gradio_client import Client, file
import logging

# Stripe API Keys (replace with your test secret key)
stripe.api_key = "sk_test_51QdPo2R33uCDdxxk2RBi1HhBGbhWcC1w7B7dW0RqM1GVHnq7TfYDqvdmtcBqgXriuGoddpsPGCJqmXeHf9K5rJZ700uAXy1but"

# Initialize FastAPI
app = FastAPI()

# Initialize Gradio Client
client = Client("AIRI-Institute/HairFastGAN")

# Temporary folder for uploaded files
os.makedirs("temp", exist_ok=True)

# To store generated image paths
generated_images = {}

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/process_hair_style")
async def process_hair_style(
    source: UploadFile = File(...),
    style: UploadFile = File(...),
    color: UploadFile = File(None)
):
    # Save uploaded files
    source_path = save_upload_file(source, "temp")
    style_path = save_upload_file(style, "temp")
    color_path = save_upload_file(color, "temp") if color else None

    # Call swap_hair API
    result = client.predict(
        face=file(source_path),
        shape=file(style_path),
        color=file(color_path) if color_path else None,
        blending="Article",
        poisson_iters=0,
        poisson_erosion=15,
        api_name="/swap_hair"
    )

    # If result contains the image, create payment session
    if isinstance(result, tuple) and len(result) == 2:
        image_response, _ = result
        if image_response.get("visible"):
            result_image_path = image_response.get("value")
            session_id = create_payment_session(result_image_path)
            return {"session_id": session_id}
    return {"error": "Failed to generate image."}

# Utility for saving uploaded files
def save_upload_file(uploaded_file: UploadFile, save_dir: str):
    save_path = os.path.join(save_dir, uploaded_file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return save_path

# Stripe Payment Route
@app.post("/create_payment_session")
def create_payment_session(image_path: str):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Hair Style Image'},
                    'unit_amount': 500,  # $5.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/cancel",
        )
        generated_images[session['id']] = image_path
        return {"session_id": session['id'], "checkout_url": session['url']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Success page
@app.get("/success", response_class=HTMLResponse)
def success(session_id: str):
    image_path = generated_images.get(session_id)
    if image_path:
        return f"""
        <html>
        <body>
            <h1>Image Styled Successfully!</h1>
            <img src="/view-image?session_id={session_id}" />
            <a href="/download-image?session_id={session_id}">Download Image</a>
        </body>
        </html>
        """
    raise HTTPException(status_code=404, detail="Image not found.")

@app.get("/view-image")
def view_image(session_id: str):
    image_path = generated_images.get(session_id)
    return FileResponse(image_path, media_type="image/png") if image_path else HTTPException(404)

@app.get("/download-image")
def download_image(session_id: str):
    image_path = generated_images.get(session_id)
    return FileResponse(image_path, media_type="image/png", filename="styled_image.png") if image_path else HTTPException(404)
