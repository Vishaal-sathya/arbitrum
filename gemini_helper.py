from app.extensions import gemini
import json
import re
from ast import literal_eval
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_
from app.models import User, Profile, Skills, UserSkills, Projects, Experience
import faiss
import numpy as np
from vector_embedder import embed_text

index = faiss.read_index("user_index.faiss")
user_ids = np.load("user_ids.npy")


def is_fetch_query(query):
    prompt = f"""
    You are an assistant that helps determine whether a query is a general question or is related to fetching data about users/candidates.

    Classify the query as:
    - `fetch`: it involves fetching users/candidates based on certain criteria
    - `general`: general questions that do not involve fetching users/candidates information

    Query:
    "{query}"

    Answer with one word: fetch or general.
    """
    response = gemini.generate_content(prompt)
    classification = response.text.strip().lower()
    print(classification)
    return classification == "fetch"


def is_query_semantic(query: str) -> bool:
    prompt = f"""
    You are an assistant that helps determine whether a query requires semantic understanding.

    Classify the query as:
    - `semantic`: if it involves experiences, projects, or abstract understanding
    - `structured`: if it can be answered using direct filters like name, college, or skills/knowledge

    Query:
    "{query}"

    Answer with one word: semantic or structured.
    """
    response = gemini.generate_content(prompt)
    classification = response.text.strip().lower()
    print(classification)
    return classification == "semantic"


def extract_structured_filters(query: str) -> dict:
    prompt = f"""
    Extract the following filters from the query below:
    - name: person name if mentioned
    - college: college name if mentioned
    - skills: list of technical skills mentioned

    Return the result as a JSON object with these keys: name, college, skills.

    Query:
    "{query}"
    """
    response = gemini.generate_content(prompt)
    raw_response = response.text.strip()
    cleaned_response = re.sub(r"^```json|^```|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()
    print(cleaned_response)
    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        # fallback if Gemini returns badly formatted response

        match = re.search(r"\{.*\}", cleaned_response.text, re.DOTALL)
        return literal_eval(match.group()) if match else {}



def get_filtered_users(filters):
    query = User.query.options(joinedload(User.profile))

    if "name" in filters and filters["name"]:
        query = query.filter(User.username.ilike(f"%{filters['name']}%"))

    if "college" in filters and filters["college"]:
        query = query.join(User.profile).filter(Profile.college.ilike(f"%{filters['college']}%"))

    if "skills" in filters and filters["skills"]:
        for skill in filters["skills"]:
            query = query.join(User.skills).join(UserSkills.skill).filter(Skills.skill.ilike(f"%{skill}%"))

    # To avoid duplicates from joins
    query = query.distinct()

    return query.all()



def search_similar_users(query, top_k=10):
    query_vector = embed_text(query).reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)

    distance_values = distances[0]
    index_values = indices[0]

    # Filter out invalid indices (those set to max float)
    valid_results = [
        (dist, idx)
        for dist, idx in zip(distance_values, index_values)
        if dist < 1e10 and idx < len(user_ids)
    ]

    if not valid_results:
        return []

    # Dynamic threshold: keep users within 1.3x of best distance
    best_distance = valid_results[0][0]
    cutoff_distance = best_distance * 1.3

    matched_user_ids = [
        int(user_ids[idx]) for dist, idx in valid_results if dist <= cutoff_distance
    ]

    print(f"Best distance: {best_distance:.3f} | Cutoff: {cutoff_distance:.3f}")
    print("Matched user IDs:", matched_user_ids)

    return matched_user_ids



def get_user_data(user_ids):
    return User.query.filter(User.id.in_(user_ids)).all()


import re
from ast import literal_eval

def extract_relevant_keywords(query: str) -> list:
    prompt = f"""
    You are an assistant helping identify keywords for semantic and keyword-based matching.

    Given the user's query, return a list of **up to 10 relevant keywords or phrases** that represent the key ideas, domains, and concepts from the query.

    Query: "{query}"

    Return the result as a Python list of lowercase strings.
    Example: ["disaster", "relief", "emergency", "aid"]
    """
    response = gemini.generate_content(prompt)
    raw = response.text.strip()

    # Cleanup for code blocks
    raw = raw.replace("```python", "").replace("```", "").strip()

    try:
        return literal_eval(raw)
    except Exception:
        print("Keyword extraction failed:", raw)

        # Failsafe: extract list using regex
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if match:
            try:
                return literal_eval(match.group())
            except Exception:
                pass

        return []





def is_project_relevant(text, keywords):
    text = text.lower()


    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation

    for keyword in keywords:
        keyword = keyword.lower()
        keyword = re.sub(r'[^\w\s]', '', keyword)  # Clean keyword too

        if keyword in text:
            print(keyword, " in text")
            return True
    print("fail")
    return False


def semantic_search_users(user_ids, keywords):
    filtered_users = []

    users = User.query.options(
        joinedload(User.projects),
        joinedload(User.experiences)
    ).filter(User.id.in_(user_ids)).all()

    for user in users:
        match_found = False
        
        for project in user.projects:
            print(project.title)
            content = f"{project.title} {project.description}"
            if is_project_relevant(content, keywords):
                match_found = True
                break

        if not match_found:
            for exp in user.experiences:
                content = f"{exp.position} {exp.organization_name}"
                if is_project_relevant(content, keywords):
                    match_found = True
                    break

        if match_found:
            filtered_users.append(user)

    return filtered_users
