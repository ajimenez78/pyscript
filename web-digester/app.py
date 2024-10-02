import os
from flask import Flask, request
import requests
from dotenv import load_dotenv
from markupsafe import escape
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

class Website:
    url: str
    title: str
    text: str

    def __init__(self, url):
        self.url = url
        headers = {
            "User-Agent": 'Flask User Agent'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

app = Flask(__name__)

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
openai = OpenAI()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/digest")
def digest():
    url = request.args.get('url', '')
    ed = Website(url)
    return f"<span>Title: {ed.title}</span><span>Content: {ed.text}</span>"

