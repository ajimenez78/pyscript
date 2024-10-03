import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
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

@app.route("/", methods=['GET', 'POST'])
def digest():
    if request.method == 'POST':
        url = request.form['url']
        summary = summarize(url)
        return markdown.markdown(summary) + '<a href="/">Back</a>'
    else:
        return render_template('index.html')

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
