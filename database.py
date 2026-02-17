from datetime import datetime
from models import Article, Avis

# Base de données simulée (en production, utiliser SQLAlchemy + PostgreSQL)
articles_db = [
    {
        "id": 1,
        "titre": "Laptop Dell XPS 13",
        "description": "Ordinateur portable haute performance",
        "prix": 1200.00,
        "stock": 15,
        "categorie": "Électronique",
        "date_ajout": datetime.now()
    },
    {
        "id": 2,
        "titre": "Casque Sony WH-1000XM4",
        "description": "Casque sans fil avec réduction de bruit",
        "prix": 350.00,
        "stock": 25,
        "categorie": "Audio",
        "date_ajout": datetime.now()
    },
    {
        "id": 3,
        "titre": "Clavier Mécanique Corsair",
        "description": "Clavier RGB haute performance",
        "prix": 150.00,
        "stock": 30,
        "categorie": "Accessoires",
        "date_ajout": datetime.now()
    }
]

avis_db = [
    {
        "id": 1,
        "article_id": 1,
        "utilisateur": "Ahmed",
        "note": 5,
        "commentaire": "Excellent produit, vraiment recommandé!",
        "date_creation": datetime.now()
    },
    {
        "id": 2,
        "article_id": 1,
        "utilisateur": "Fatima",
        "note": 4,
        "commentaire": "Bon produit mais un peu cher",
        "date_creation": datetime.now()
    },
    {
        "id": 3,
        "article_id": 2,
        "utilisateur": "Hassan",
        "note": 5,
        "commentaire": "Qualité du son incroyable!",
        "date_creation": datetime.now()
    }
]

# Fonctions CRUD pour les articles
def get_all_articles():
    return articles_db

def get_article_by_id(article_id: int):
    return next((a for a in articles_db if a["id"] == article_id), None)

def create_article(article_data: dict):
    new_id = max([a["id"] for a in articles_db]) + 1 if articles_db else 1
    new_article = {
        "id": new_id,
        **article_data,
        "date_ajout": datetime.now()
    }
    articles_db.append(new_article)
    return new_article

def update_article(article_id: int, article_data: dict):
    article = get_article_by_id(article_id)
    if article:
        article.update({k: v for k, v in article_data.items() if v is not None})
        return article
    return None

def delete_article(article_id: int):
    global articles_db
    articles_db = [a for a in articles_db if a["id"] != article_id]
    return True

# Fonctions CRUD pour les avis
def get_avis_by_article(article_id: int):
    return [a for a in avis_db if a["article_id"] == article_id]

def create_avis(avis_data: dict):
    new_id = max([a["id"] for a in avis_db]) + 1 if avis_db else 1
    new_avis = {
        "id": new_id,
        **avis_data,
        "date_creation": datetime.now()
    }
    avis_db.append(new_avis)
    return new_avis

def get_avis_statistics(article_id: int):
    """Calcule les statistiques des avis"""
    avis_list = get_avis_by_article(article_id)
    if not avis_list:
        return {"nombre_avis": 0, "note_moyenne": 0}
    
    notes = [a["note"] for a in avis_list]
    note_moyenne = sum(notes) / len(notes)
    return {
        "nombre_avis": len(avis_list),
        "note_moyenne": round(note_moyenne, 2),
        "note_min": min(notes),
        "note_max": max(notes)
    }