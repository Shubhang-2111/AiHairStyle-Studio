# AiHairStyleStudio

AiHairStyleStudio is a FastAPI-based application that allows users to upload images and apply hair style transfer using Gradio. The app also integrates Stripe for payments.

## Project Setup

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app locally:

    ```bash
    uvicorn app.main:app --reload
    ```

3. To deploy, run:

    ```bash
    flyctl deploy
    ```

## Stripe Integration

- Set up your Stripe API keys in `main.py`.
- The app allows users to make payments and download styled images after successful payment.
