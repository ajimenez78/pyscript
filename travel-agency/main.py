import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import markdown
from markupsafe import Markup
from openai import OpenAI
import anthropic

app = Flask(__name__)

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
openai = OpenAI()

os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
claude = anthropic.Anthropic()

system_prompt = "Eres un agente de viajes. Recibirás peticiones de información acerca de \
    destinos turísticos. Debes proporcionar una pequeña descripción del destino, así como \
    sugerencias acerca de actividades que realizar, gastronomía, lugares de interés que \
    visitar por la zona y sitios cercanos de visita recomendada. \
    Responde usando Markdown."

image_generation_prompt = "Una imagen que represente unas vacaciones en {destination}, \
    mostrando puntos turísticos y cosas únicas en {destination}, en un estilo de cómic."

user_prompt = "Me gustaría viajar a {destination}. ¿Qué información me puedes dar?"

def recommend(destination):
    response = claude.messages.create(
        model = "claude-3-5-sonnet-20240620",
        max_tokens=2000,
        system=system_prompt,
        messages = [
            {"role": "user", "content": user_prompt.format(destination=destination)}
        ]
    )
    return response.content[0].text

def generate_image(destination):
    image_response = openai.images.generate(
            model="dall-e-3",
            prompt=image_generation_prompt.format(destination=destination),
            size="1792x1024",
            n=1
        )
    return image_response.data[0].url


@app.route("/", methods=['GET', 'POST'])
def digest():
    if request.method == 'POST':
        destination = request.form['destination']
        summary = recommend(destination)
        image_url = generate_image(destination)
        summary_content = Markup(markdown.markdown(summary))
        return render_template('recommendation.html', destination=destination, destination_image=image_url, destination_description=summary_content)
    else:
        return render_template('index.html')

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
