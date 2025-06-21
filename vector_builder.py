import faiss
import numpy as np
from app.models import User, UserSkills
from app.extensions import db
from sqlalchemy.orm import joinedload
from vector_embedder import embed_text



def build_user_corpus(user):
    username = user.username
    user_id = user.id
    college = user.profile.college if user.profile else "Unknown College"

    skills = ', '.join([user_skill.skill.skill for user_skill in user.skills])

    projects = '. '.join(
        [f"{project.title}: {project.description}" for project in user.projects]
    )

    experiences = '. '.join(
        [f"{exp.position} at {exp.organization_name}" for exp in user.experiences]
    )

    content = (
        f"User ID: {user_id}. Name: {username}. "
        f"College: {college}. Skills: {skills}. "
        f"Projects: {projects}. Experiences: {experiences}."
    )

    if not (projects.strip() or experiences.strip() or skills.strip()):
        return None
    
    return content

def build_vector_db():
    users = User.query.options(
        joinedload(User.profile),
        joinedload(User.skills).joinedload(UserSkills.skill),  # This is the fix
        joinedload(User.experiences),
        joinedload(User.projects)
    ).all()

    user_vectors = []
    id_map = []

    for user in users:
        content = build_user_corpus(user)
        
        if content != None:
            vector = embed_text(content)
            user_vectors.append(vector)
            id_map.append(user.id)

    # Convert to NumPy array
    index_array = np.vstack(user_vectors)

    # Create FAISS index
    dim = index_array.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(index_array)

    # Save index and ID map
    faiss.write_index(index, "user_index.faiss")
    with open("user_ids.npy", "wb") as f:
        np.save(f, np.array(id_map))

    print(f"Vector DB built for {len(users)} users.")
