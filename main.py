import base64
import os

import anthropic
import gradio as gr
from ratelimit import RateLimitException, limits

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

js = """<script src="https://replit.com/public/js/replit-badge-v2.js" theme="dark" position="bottom-right"></script>"""


def image_to_base64(image_path):
  """Convert the image to base64."""
  with open(image_path, "rb") as image_file:
    image_data = image_file.read()
    return base64.b64encode(image_data).decode("utf-8")


def get_media_type(image_name):
  """Get the media type of the uploaded image based on its file extension."""
  if image_name.lower().endswith(".jpg") or image_name.lower().endswith(
      ".jpeg"):
    return "image/jpeg"
  elif image_name.lower().endswith(".png"):
    return "image/png"
  else:
    raise ValueError(f"Unsupported image format: {image_name}")


# Limit to 5 calls every 30m
@limits(calls=5, period=1800)
def image_to_text(b64_img, media_type):
  prompt = """
  The following image may contain text. There may be multiple parts of the image where text is present, possibly in different sizes and fonts return ALL TEXT. Un-obstruct text if it is covered by something, to make it readable. Interpret the text in the image as written and return ALL TEXT found, even smaller text, starting with the ★ symbol. Do not return any output other than the text that's in the image. If no text can be found, return "No text found. Examples: ★NO PARKING violators may be towed at the owner's expense, ★No text found.
  """

  message = client.messages.create(model="claude-3-sonnet-20240229",
                                   max_tokens=1000,
                                   messages=[{
                                       "role":
                                       "user",
                                       "content": [{
                                           "type": "image",
                                           "source": {
                                               "type": "base64",
                                               "media_type": media_type,
                                               "data": b64_img,
                                           },
                                       }, {
                                           "type": "text",
                                           "text": prompt
                                       }],
                                   }])

  return message.content[0].text.split('★')[1]


def app(img):

  # Convert the image to a format that can be processed

  b64 = image_to_base64(img)
  media_type = get_media_type(img)

  try:
    msg = image_to_text(b64, media_type)
  except RateLimitException:
    msg = "Rate limit exceeded. Please try again later."

  return msg


with gr.Blocks(title="Image2Text", head=js) as demo:

  with gr.Row():
    gr.Markdown("""
    # 🚀 Image2Text
    
    This is an image to text demo built and deployed on [Replit](https://repl.it?utm_medium=repl&utm_source=matt&utm_campaign=templates) with [Anthropic](https://anthropic.com). The entire demo was built in under 30 minutes using a combination of Replit's ModelFarm, Gradio, and Anthropic's Python SDK. Upload or paste an image below to get started.
    
    """)

  gr.Interface(
      fn=app,
      inputs=gr.Image(type="filepath",
                      label="👨‍🎨 Add your image",
                      sources=['upload', 'clipboard']),
      outputs="text",
  )
demo.launch(favicon_path="assets/favicon.png")
