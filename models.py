from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Modèle pour un Avis
class AvisBase(BaseModel):
    utilisateur: str
    note: int  # 1-5
    commentaire: str

class Avis(AvisBase):
    id: int
    article_id: int
    date_creation: datetime

# Modèle pour un Article
class ArticleBase(BaseModel):
    titre: str
    description: str
    prix: float
    stock: int
    categorie: str

class Article(ArticleBase):
    id: int
    date_ajout: datetime
    avis: Optional[List[Avis]] = []

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None
    stock: Optional[int] = None
    categorie: Optional[str] = None