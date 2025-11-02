

import os
import logging
from flask import Flask, request, render_template_string
import openai

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Provider selection
PROVIDERS = ['azure', 'openai', 'github']

def get_provider():
    provider = request.args.get('provider', 'azure').lower()
    if provider not in PROVIDERS:
        logging.warning(f"Invalid provider '{provider}' requested. Defaulting to 'azure'.")
        provider = 'azure'
    return provider

def call_model(prompt, provider):
  try:
    if provider == 'azure':
      return f"[Azure OpenAI] Response to: {prompt}"
    elif provider == 'openai':
      # Actual OpenAI API call (openai>=1.0.0)
      openai_api_key = os.getenv('OPENAI_API_KEY')
      if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment.")
      client = openai.OpenAI(api_key=openai_api_key)
      response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
      )
      return response.choices[0].message.content
    elif provider == 'github':
      return f"[GitHub Models] Response to: {prompt}"
    else:
      raise ValueError("Unknown provider")
  except Exception as e:
    logging.error(f"Error calling model: {e}")
    return f"Error: {str(e)}"

app = Flask(__name__)

HTML_FORM = '''
<html>
<head><title>GenAI Assignment</title></head>
<body>
  <h2>Generative AI Prompt Assignment</h2>
  <form method="post">
    <label>Prompt:</label><br>
    <textarea name="prompt" rows="4" cols="50">{{ prompt }}</textarea><br><br>
    <label>Provider:</label>
    <select name="provider">
      {% for p in providers %}
        <option value="{{ p }}" {% if p == provider %}selected{% endif %}>{{ p.title() }}</option>
      {% endfor %}
    </select><br><br>
    <input type="submit" value="Submit">
  </form>
  {% if response %}
    <h3>Response:</h3>
    <pre>{{ response }}</pre>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def assignment():
    prompt = ''
    response = ''
    provider = request.args.get('provider', 'azure')
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        provider = request.form.get('provider', 'azure')
        logging.info(f"Prompt received: {prompt} | Provider: {provider}")
        response = call_model(prompt, provider)
    return render_template_string(HTML_FORM, prompt=prompt, response=response, provider=provider, providers=PROVIDERS)

if __name__ == '__main__':
    app.run(debug=True)