from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.wikipedia_service import WikipediaService
from app.services.impact_calculator import ImpactCalculator

router = APIRouter()
logger = structlog.get_logger()

class AnalysisRequest(BaseModel):
    page_url: str

async def run_analysis(page_url: str, db_session: AsyncSession):
    """Helper function to run the service and close its resources."""
    impact_calculator = ImpactCalculator()
    service = WikipediaService(db_session, impact_calculator)
    try:
        await service.analyze_wikipedia_page(page_url)
    except Exception as e:
        logger.error("Analysis task failed", error=e, url=page_url)
    finally:
        await service.close()

@router.post("/analyze", status_code=202)
async def analyze_wiki_page(
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts a Wikipedia page URL and queues it for analysis in the background.
    接收一个维基百科页面URL，并将其放入后台队列等待分析。
    """
    logger.info("Received request to analyze page", url=analysis_request.page_url)
    
    background_tasks.add_task(run_analysis, analysis_request.page_url, db)
    
    return {"message": "Analysis has been successfully queued.", "url": analysis_request.page_url} 