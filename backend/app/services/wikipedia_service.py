import httpx
import asyncio
import structlog
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, unquote
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dateutil.parser import isoparse

from app.core.config import settings
from app.models.contributor import Contributor
from app.models.analysis_session import AnalysisSession
from app.services.impact_calculator import ImpactCalculator, EditAnalysis

logger = structlog.get_logger()

class WikipediaService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.http_client = httpx.AsyncClient(
            base_url=settings.WIKIPEDIA_API_URL,
            timeout=30.0,
            headers={"User-Agent": f"WikiImpactAnalyzer/{settings.VERSION}"},
            follow_redirects=True,
        )
        self.impact_calculator = ImpactCalculator()

    def _extract_title_and_lang_from_url(self, url: str) -> Optional[Tuple[str, str]]:
        try:
            parsed_url = urlparse(url)
            hostname_parts = parsed_url.netloc.split('.')
            if len(hostname_parts) < 3 or "wikipedia.org" not in parsed_url.netloc:
                return None
            lang = hostname_parts[0]
            path_parts = parsed_url.path.split('/')
            if len(path_parts) > 2 and path_parts[1] == 'wiki':
                title = unquote(path_parts[2]).replace('_', ' ')
                return title, lang
            return None
        except Exception as e:
            logger.error("Failed to parse Wikipedia URL", url=url, error=e)
            return None

    async def _fetch_all_revisions(self, title: str) -> List[Dict[str, Any]]:
        revisions = []
        params = {
            "action": "query", "format": "json", "prop": "revisions",
            "titles": title, "rvprop": "ids|timestamp|user|userid|size|comment|tags|sizediff",
            "rvlimit": "max",
        }
        logger.info("Fetching revisions for page", title=title)
        while True:
            try:
                response = await self.http_client.get("/", params=params)
                response.raise_for_status()
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                page_id = next(iter(pages))
                if page_id == "-1":
                    return []
                page_revisions = pages[page_id].get("revisions", [])
                revisions.extend(page_revisions)
                if "continue" not in data:
                    break
                params["rvcontinue"] = data["continue"]["rvcontinue"]
            except Exception as e:
                logger.error("Error during revision fetching", error=str(e))
                break
        logger.info("Fetched total revisions", count=len(revisions), title=title)
        return revisions

    def _convert_to_edit_analysis(self, revision: Dict[str, Any]) -> EditAnalysis:
        size_diff = revision.get("sizediff", 0)
        return EditAnalysis(
            edit_id=revision.get("revid", 0),
            contributor_id=revision.get("userid", 0),
            page_id=0,
            timestamp=isoparse(revision.get("timestamp", "1970-01-01T00:00:00Z")),
            size_change=size_diff,
            is_new_page="new" in revision.get("tags", []),
            is_revert="revert" in revision.get("tags", []),
            is_minor="minor" in revision.get("tags", []),
            comment=revision.get("comment", ""),
            content_added=max(0, size_diff),
            content_removed=max(0, -size_diff),
            text_complexity_score=0.5,
            semantic_significance=0.5,
        )

    async def _get_or_create_contributor(self, user_info: Dict[str, Any], lang: str) -> Optional[Contributor]:
        username = user_info.get("user")
        user_id = user_info.get("userid")
        if not username or user_id == 0:
            return None
        result = await self.db_session.execute(select(Contributor).where(Contributor.wikipedia_user_id == user_id))
        contributor = result.scalar_one_or_none()
        if contributor:
            return contributor
        
        new_contributor = Contributor(
            wikipedia_user_id=user_id, wikipedia_username=username,
            display_name=username, primary_language=lang,
        )
        self.db_session.add(new_contributor)
        await self.db_session.commit()
        await self.db_session.refresh(new_contributor)
        logger.info("Created new contributor", username=username, id=new_contributor.id)
        return new_contributor

    async def analyze_page_by_url(self, page_url: str):
        parse_result = self._extract_title_and_lang_from_url(page_url)
        if not parse_result:
            raise ValueError("Invalid Wikipedia URL")
        title, lang = parse_result

        # Create analysis session
        analysis_session = AnalysisSession(
            page_url=page_url,
            page_title=title,
            page_language=lang,
            analysis_status="processing"
        )
        self.db_session.add(analysis_session)
        await self.db_session.commit()
        await self.db_session.refresh(analysis_session)

        try:
            revisions = await self._fetch_all_revisions(title)
            if not revisions:
                analysis_session.analysis_status = "completed"
                analysis_session.total_revisions_analyzed = 0
                analysis_session.total_contributors_found = 0
                await self.db_session.commit()
                return analysis_session.id

            revisions_by_user: Dict[int, List[Dict[str, Any]]] = {}
            for rev in revisions:
                user_id = rev.get("userid")
                if user_id:
                    revisions_by_user.setdefault(user_id, []).append(rev)
            
            for user_id, user_revs in revisions_by_user.items():
                user_info = {"user": user_revs[0].get("user"), "userid": user_id}
                contributor = await self._get_or_create_contributor(user_info, lang)
                if not contributor:
                    continue

                converted_revs = [self._convert_to_edit_analysis(rev) for rev in user_revs]
                metrics = await self.impact_calculator.calculate_comprehensive_impact(
                    contributor, converted_revs, {}
                )
                
                contributor.overall_impact_score = metrics.overall_impact_score
                contributor.additive_contribution_score = metrics.additive_score
                contributor.maintenance_contribution_score = metrics.maintenance_score
                contributor.discussion_impact_score = metrics.discussion_impact_score
                contributor.quality_score = metrics.quality_score
                contributor.analysis_session_id = analysis_session.id
                self.db_session.add(contributor)

            analysis_session.analysis_status = "completed"
            analysis_session.total_revisions_analyzed = len(revisions)
            analysis_session.total_contributors_found = len(revisions_by_user)
            await self.db_session.commit()
            logger.info(f"Analysis complete for {title}.")
            return analysis_session.id
        except Exception as e:
            logger.error(f"Error during page analysis: {e}")
            analysis_session.analysis_status = "failed"
            await self.db_session.commit()
            raise

    async def close(self):
        await self.http_client.aclose() 