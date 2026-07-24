from fastapi import APIRouter, Depends

from es_app.lexicon.service import LexiconService
from es_app.schemas.word import Word

router = APIRouter(prefix="/lexicon", tags=["lexicon"])


def get_lexicon_service() -> LexiconService:
    raise NotImplementedError  # overridden in main


@router.get("/words", response_model=list[Word])
def list_words(complete_only: bool = False, svc: LexiconService = Depends(get_lexicon_service)):
    return svc.list_words(complete_only=complete_only)
