import os
from flask import Flask, request
import requests
from dotenv import load_dotenv
from markupsafe import escape
from bs4 import BeautifulSoup
import markdown
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

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "The contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/digest")
def digest():
    url = request.args.get('url', '')
    summary = summarize(url)
    return markdown.markdown(summary)