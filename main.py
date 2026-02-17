from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import List, Optional
from models import Article, ArticleCreate, ArticleUpdate, Avis, AvisBase
from database import (
    get_all_articles, get_article_by_id, create_article,
    update_article, delete_article, get_avis_by_article,
    create_avis, get_avis_statistics
)

app = FastAPI(
    title="Articles API",
    description="API pour gérer les articles et leurs avis",
    version="1.0.0"
)

# Ajouter CORS middleware pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration de l'API externe des avis
AVIS_API_URL = "https://api-avis.example.com"  # À remplacer par votre URL réelle

# ==================== ROUTES ARTICLES ====================

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Bienvenue sur l'API Articles",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/api/articles", response_model=List[Article], tags=["Articles"])
def list_articles(skip: int = 0, limit: int = 10):
    """Récupère la liste de tous les articles"""
    articles = get_all_articles()
    return articles[skip:skip + limit]

@app.get("/api/articles/{article_id}", response_model=Article, tags=["Articles"])
def get_article(article_id: int):
    """Récupère un article spécifique avec ses avis"""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    
    # Récupérer les avis pour cet article
    avis_list = get_avis_by_article(article_id)
    article["avis"] = avis_list
    
    return article

@app.post("/api/articles", response_model=Article, tags=["Articles"], status_code=status.HTTP_201_CREATED)
def create_new_article(article: ArticleCreate):
    """Crée un nouvel article"""
    article_data = article.dict()
    new_article = create_article(article_data)
    return new_article

@app.put("/api/articles/{article_id}", response_model=Article, tags=["Articles"])
def update_existing_article(article_id: int, article_update: ArticleUpdate):
    """Met à jour un article existant"""
    article = update_article(article_id, article_update.dict(exclude_unset=True))
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    return article

@app.delete("/api/articles/{article_id}", tags=["Articles"])
def remove_article(article_id: int):
    """Supprime un article"""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    delete_article(article_id)
    return {"message": f"Article {article_id} supprimé avec succès"}

# ==================== ROUTES AVIS ====================

@app.get("/api/articles/{article_id}/avis", response_model=List[Avis], tags=["Avis"])
def get_article_reviews(article_id: int):
    """Récupère tous les avis pour un article"""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    
    avis_list = get_avis_by_article(article_id)
    return avis_list

@app.post("/api/articles/{article_id}/avis", response_model=Avis, tags=["Avis"], status_code=status.HTTP_201_CREATED)
def add_review(article_id: int, avis: AvisBase):
    """Ajoute un nouvel avis à un article"""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    
    # Validation de la note
    if avis.note < 1 or avis.note > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La note doit être entre 1 et 5"
        )
    
    avis_data = avis.dict()
    avis_data["article_id"] = article_id
    new_avis = create_avis(avis_data)
    return new_avis

@app.get("/api/articles/{article_id}/avis/statistiques", tags=["Avis"])
def get_review_statistics(article_id: int):
    """Récupère les statistiques des avis pour un article"""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    
    stats = get_avis_statistics(article_id)
    return stats

# ==================== INTÉGRATION API EXTERNE ====================

@app.get("/api/articles/{article_id}/avis-externes", tags=["Avis Externes"])
async def get_external_reviews(article_id: int):
    """Récupère les avis d'une API externe (exemple)"""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article avec l'ID {article_id} non trouvé"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            # Exemple d'appel à une API externe
            response = await client.get(
                f"{AVIS_API_URL}/reviews/{article_id}",
                timeout=5.0
            )
            response.raise_for_status()
            external_reviews = response.json()
            return {
                "article_id": article_id,
                "avis_internes": get_avis_by_article(article_id),
                "avis_externes": external_reviews
            }
    except httpx.HTTPError as e:
        return {
            "article_id": article_id,
            "avis_internes": get_avis_by_article(article_id),
            "avis_externes": [],
            "erreur": f"Impossible de récupérer les avis externes: {str(e)}"
        }

# ==================== RECHERCHE ET FILTRAGE ====================

@app.get("/api/articles/search", tags=["Articles"])
def search_articles(
    titre: Optional[str] = None,
    categorie: Optional[str] = None,
    prix_min: Optional[float] = None,
    prix_max: Optional[float] = None
):
    """Recherche et filtre les articles"""
    articles = get_all_articles()
    
    if titre:
        articles = [a for a in articles if titre.lower() in a["titre"].lower()]
    
    if categorie:
        articles = [a for a in articles if a["categorie"].lower() == categorie.lower()]
    
    if prix_min:
        articles = [a for a in articles if a["prix"] >= prix_min]
    
    if prix_max:
        articles = [a for a in articles if a["prix"] <= prix_max]
    
    return articles

# ==================== HEALTH CHECK ====================

@app.get("/health", tags=["Health"])
def health_check():
    """Vérification de l'état de l'API"""
    return {"status": "OK", "message": "API Articles en ligne"}