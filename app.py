import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv # Optional

load_dotenv() # Optional: Load environment variables from .env file

app = Flask(__name__)

genai.configure(api_key="AIzaSyCwrZHQgXwSL_O2_xFXJ0eU_ZpEM1AAcBo")


# Initialize the Generative Model
# Choose a model that suits your needs, e.g., 'gemini-1.5-flash' or 'gemini-pro'
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    model = None # Ensure model is None if initialization fails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_article', methods=['POST'])
def generate_article_route():
    if not model:
        return jsonify({"error": "Gemini model not initialized. Check API key and configuration."}), 500

    data = request.get_json()
    keyword_or_title = data.get('keyword')

    if not keyword_or_title:
        return jsonify({"error": "Keyword or title is required."}), 400

    # --- Comprehensive SEO Prompt Engineering ---
    prompt = f"""
    Generate a comprehensive, engaging, and SEO-optimized article based on the keyword/title: "{keyword_or_title}".
    The article must be structured for maximum SEO effectiveness and readability.

    Please include the following elements:

    1.  Optimized Title Tag (approx. 50-60 characters): A compelling title that includes the primary keyword "{keyword_or_title}" and is likely to attract clicks.
    2.  Meta Description (approx. 150-160 characters): A concise and engaging summary that includes "{keyword_or_title}" and encourages users to read the article.
    3.  Article Body:
         H1 Heading: Derived from or identical to "{keyword_or_title}".
         Introduction: An engaging opening (2-3 paragraphs) that hooks the reader and naturally incorporates "{keyword_or_title}" and related LSI keywords.
         H2 Subheadings: At least 3-5 relevant H2 subheadings that break down the topic logically. These should also try to incorporate variations of the main keyword or LSI keywords.
         Content under H2s: Well-written, informative, and unique content for each H2 section. Aim for a total word count of at least 800-1200 words for the entire article body (excluding title and meta).
         Keyword Integration: Naturally weave "{keyword_or_title}" and relevant LSI keywords throughout the article. Avoid keyword stuffing.
         Readability: Use short sentences, paragraphs, bullet points, and bold text for emphasis where appropriate to enhance readability.
         Internal/External Link Placeholders (Conceptual): Suggest 1-2 conceptual placeholders for internal links (e.g., "[Link to our related service page]") and 1 external link to a high-authority (non-competing) resource (e.g., "[Link to a relevant Wikipedia article or industry study]").
         Call to Action (Optional): A subtle call to action in the conclusion if appropriate for the topic.
         Conclusion: A strong concluding paragraph summarizing the key takeaways.
    4.  Suggested LSI Keywords: A list of 5-7 Latent Semantic Indexing (LSI) keywords relevant to "{keyword_or_title}" that were used or could be incorporated.
    5.  FAQ Section (Optional): 2-3 frequently asked questions related to "{keyword_or_title}" with brief answers.

    Output Format:
    Please structure your response clearly, perhaps using Markdown-like formatting for headings, lists, etc., so it's easy to parse and display.
    For example:

    ```text
    Title Tag: [Generated Title Tag Here]

    Meta Description: [Generated Meta Description Here]

    ---
    Article Body:

    # [Generated H1 Heading Here]

    [Introduction text...]

    ## [Generated H2 Subheading 1]
    [Content for subheading 1...]

    ## [Generated H2 Subheading 2]
    [Content for subheading 2...]
    (and so on)

    [Conceptual Internal Link Placeholder: ...]
    [Conceptual External Link Placeholder: ...]

    [Conclusion text...]

    ---
    Suggested LSI Keywords:
     Keyword 1
     Keyword 2
    ...

    ---
    FAQ Section:
    Q: [Question 1]?
    A: [Answer 1].

    Q: [Question 2]?
    A: [Answer 2].
    ```
    Ensure the content is original, valuable, and written in a professional yet accessible tone.
    Focus on user intent and providing comprehensive information related to "{keyword_or_title}".
    """

    try:
        generation_config = genai.types.GenerationConfig(
            # temperature=0.7, # Adjust for creativity vs. factualness
            # max_output_tokens=4096 # Adjust based on expected article length
        )
        response = model.generate_content(prompt, generation_config=generation_config)

        # Assuming the response contains the structured article as text
        # You might need to parse this if Gemini provides a more structured JSON,
        # but text is common for complex formatted content.
        generated_text = response.text

        # Basic parsing attempt (you might need more sophisticated parsing)
        article_parts = {"raw_text": generated_text}
        try:
            title_tag = generated_text.split("Title Tag:")[1].split("Meta Description:")[0].strip()
            meta_description = generated_text.split("Meta Description:")[1].split("---")[0].strip()
            article_body_section = generated_text.split("---")[1].split("---")[0] # Rough split
            # Further parsing for H1, H2s, etc. would be needed here if you want to separate them in the backend.
            # For simplicity, we'll pass the bulk.
            article_parts["title_tag"] = title_tag
            article_parts["meta_description"] = meta_description
            article_parts["article_body_html"] = article_body_section # Or convert markdown to HTML here

        except IndexError:
            # Fallback if parsing fails, send the raw text
            print("Warning: Could not parse all parts of the generated article. Sending raw text.")


        return jsonify(article_parts)

    except Exception as e:
        app.logger.error(f"Error generating article: {e}")
        return jsonify({"error": f"Failed to generate article. {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False for production
