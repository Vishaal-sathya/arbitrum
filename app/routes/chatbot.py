import google.generativeai as genai
from flask import Blueprint, render_template, request, url_for, flash, session
from flask_login import current_user
from app.forms import ChatBot  # Assuming your WTForm is named ChatBot
from app.extensions import gemini
import gemini_helper

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot', methods=['GET', 'POST'])
def chatbot_page():
    form = ChatBot()
    user_query = ""
    ai_response = ""
    selected_users = []
    if "chat_history" not in session:
        session['chat_history'] = []

    if form.validate_on_submit():
        user_query = form.input.data.strip()

        if gemini_helper.is_fetch_query(user_query):
            if gemini_helper.is_query_semantic(user_query):
                matched_user_ids = gemini_helper.search_similar_users(user_query)
                keywords = gemini_helper.extract_relevant_keywords(user_query)
                print(keywords)
                selected_users = gemini_helper.semantic_search_users(matched_user_ids, keywords)
                
            else:
                query_filters = gemini_helper.extract_structured_filters(user_query)
                selected_users = gemini_helper.get_filtered_users(query_filters)
            
            if len(selected_users) > 0 :
                ai_response = "You can view the candidates selected based on your criteria on the left."
            else:
                ai_response = 'I could not find users mathcing your criteria.'
        else:
            try:
                response = gemini.generate_content(user_query)
                ai_response = response.text
            except Exception as e:
                ai_response = f"⚠️ Error: {str(e)}"
        
        chat_entry = {
            'user': user_query,
            'bot': ai_response
        }
        session['chat_history'].append(chat_entry)
        session.modified = True



    return render_template(
        'bot/chatbot_interface.html',
        user=current_user,
        form=form,
        user_query=user_query,
        ai_response=ai_response,
        chat_history = session.get('chat_history',[]),
        selected_users=selected_users
    )
