import io
import dotenv
import os
import streamlit as st
from google import genai
from google.genai import types
import json

from helpers import my_logger

dotenv.load_dotenv()

GEMINI_API_KEY = dotenv.get_key(".env", "GEMINI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    if "GEMINI_API_KEY" in st.session_state:
        GEMINI_API_KEY = st.session_state.GEMINI_API_KEY
    else:
        st.set_page_config(page_title="File Analyser", layout="wide")
        st.title("PII remover and analyser")
        st.page_link(
            "https://github.com/pii-remover-analyser",
            label="GitHub Repo",
        )

        st.sidebar.warning("Gemini API Key Required")
        api_key_input = st.sidebar.text_input(
            "Enter your Gemini API Key:",
            type="password",
            help="Get your API key from Google AI Studio",
        )

        if api_key_input:
            st.session_state.GEMINI_API_KEY = api_key_input
            GEMINI_API_KEY = api_key_input
            st.sidebar.success("API Key saved!")
            st.rerun()
        else:
            st.error("Please enter your Gemini API Key in the sidebar to continue.")
            st.stop()

if not GEMINI_API_KEY:
    st.error("Gemini API Key is required to proceed.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)


prompt = """You are a security consultant. Analyse and provide insights in a few lines. Don't add any additional text."""

prompt_for_image = "The heading should be the key device or software in the image. The description should be a brief summary of the security aspects depicted in the image."

prompt_for_output = """Generate a JSON object based on a security analysis.
The JSON object must have the following structure:
1.  A top-level key named "file_description". Its value must be a JSON object containing:
    - A key "heading" with a string value.
    - A key "description" with a string value.
2.  A top-level key named "key_findings". Its value must be an array of three to four strings, where each string is a distinct security finding, it can be advantages, disadvantages or general info.

Here is the exact format to follow:
{
  "file_description": {
    "heading": "",
    "description": ""
  },
  "key_findings": [
  ]
}"""
if_multiple_occurrences = "If a text appears across multiple images without any symantic meaning consider it to be brand name and ignore it."


# Analyze direct image input
def analyze_image_with_gemini(image):
    try:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        data = buf.getvalue()
        # my_file = client.files.upload(file=buf)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                prompt_for_image,
                prompt_for_output,
                genai.types.Part.from_bytes(data=data, mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        # my_logger.info(f"Image analysis result:\n{response.text}")
        return response.text
    except Exception as e:
        my_logger.error(f"Error analyzing image with gemini: {e}")
        return json.dumps({"error": str(e)})


# Analyze dataframe content
def analyze_dataframe_with_gemini(df):
    try:
        content = (
            f"The following data was found in the excel file:{df.head().to_string()} "
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                content,
                prompt_for_output,
                "There could be some inconsistency in the data, or it could contain NaN values. Please ignore those.",
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        # my_logger.info(f"DataFrame analysis result:\n{response}")
        return response.text
    except Exception as e:
        my_logger.error(f"Error analyzing dataframe with gemini: {e}")
        return json.dumps({"error": str(e)})


# Analyze embedded image in pptx
def analyze_embedded_image_with_gemini(image):
    try:
        # my_logger.info(f"Analyzing embedded image with Gemini...")
        # my_logger.info(f"Image type: {type(image)}")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        data = buf.getvalue()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=data, mime_type="image/png"),
            ],
            config=genai.types.GenerateContentConfig(
                thinking_config=genai.types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        # my_logger.info(f"Embedded image analysis result:\n{response.text}")
        return response.text
    except Exception as e:
        my_logger.error(f"Error analyzing embedded image with gemini: {e}")
        return json.dumps({"error": str(e)})


# Analyze pptx content
def analyze_ppt_with_gemini(text, tables, images):
    try:
        content = f"The following text:{text}, tables:{tables},and images:{images} were found in the pptx file."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, content, prompt_for_output, if_multiple_occurrences],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        # my_logger.info(f"PPTX analysis result:\n{response}")
        return response.text
    except Exception as e:
        my_logger.error(f"Error analyzing pptx content with gemini: {e}")
        return json.dumps({"error": str(e)})


# Analyze pdf content
def analyze_pdf_with_gemini(text, images):
    try:
        content = f"The following text:{text}, and images:{images} were found in the pdf file."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, content, prompt_for_output],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        # my_logger.info(f"PDF analysis result:\n{response.text}")
        return response.text
    except Exception as e:
        my_logger.error(f"Error analyzing pdf content with gemini: {e}")
        return json.dumps({"error": str(e)})
