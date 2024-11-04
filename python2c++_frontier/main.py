import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import markdown
import anthropic

app = Flask(__name__)

load_dotenv()

os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
claude = anthropic.Anthropic()
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

system_message = "You are a computer programmer that can translate python code to C++ in order to improve performance"

def user_prompt_for(python):
    return f"Rewrite this python code to C++. You must search for the maximum performance. \
    Format your response in HTML. This is the Code: \
    \n\n\
    {python}"

def rewrite(python):
    result = claude.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=system_message,
        messages=[{"role": "user", "content": user_prompt_for(python)}],
    )
    with result as stream:
        for text in stream.text_stream:
            yield text


@app.route("/", methods=['GET', 'POST'])
def digest():
    if request.method == 'POST':
        python = request.form['python']
        return rewrite(python)
    else:
        return render_template('index.html')

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
