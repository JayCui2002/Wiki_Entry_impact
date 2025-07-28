"""
Wikipedia Service for fetching and analyzing Wikipedia page data
Wikipedia服务，用于获取和分析Wikipedia页面数据
"""

import httpx
import asyncio
import structlog
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_session import AnalysisSession
from app.models.contributor import Contributor
from app.services.impact_calculator import ImpactCalculator, EditAnalysis

logger = structlog.get_logger()


class WikipediaService:
    """
    Service for Wikipedia API interactions and analysis session management
    Wikipedia API交互和分析会话管理服务
    """
    
    def __init__(self, db_session: AsyncSession, impact_calculator: ImpactCalculator):
        self.db_session = db_session
        self.impact_calculator = impact_calculator
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={'User-Agent': 'WikiImpactBot/1.0 (Educational Research Tool)'}
        )
        
    def _extract_page_info(self, page_url: str) -> tuple[str, str]:
        """
        Extract title and language from Wikipedia URL
        从Wikipedia URL中提取标题和语言
        """
        try:
            parsed = urlparse(page_url)
            
            # Extract language from subdomain (e.g., en.wikipedia.org)
            domain_parts = parsed.netloc.split('.')
            if len(domain_parts) >= 3 and domain_parts[1] == 'wikipedia':
                lang = domain_parts[0]
            else:
                lang = 'en'  # Default to English
            
            # Extract title from path
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'wiki':
                title = unquote(path_parts[1]).replace('_', ' ')
            else:
                raise ValueError("Invalid Wikipedia URL format")
                
            return title, lang
            
        except Exception as e:
            logger.error(f"Error parsing Wikipedia URL {page_url}: {e}")
            raise ValueError(f"Unable to parse Wikipedia URL: {page_url}")

    async def _fetch_all_revisions(self, title: str, language: str = 'en') -> List[Dict[str, Any]]:
        """
        Fetch all revisions for a Wikipedia page
        获取Wikipedia页面的所有修订版本
        """
        base_url = f"https://{language}.wikipedia.org/w/api.php"
        all_revisions = []
        rvcontinue = None
        
        while True:
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'revisions',
                'titles': title,
                'rvlimit': 500,  # Maximum allowed
                'rvprop': 'timestamp|user|userid|size|comment|flags|sha1',
                'rvdir': 'newer'  # Oldest first
            }
            
            if rvcontinue:
                params['rvcontinue'] = rvcontinue
                
            try:
                response = await self.http_client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                pages = data.get('query', {}).get('pages', {})
                if not pages:
                    break
                    
                page_data = next(iter(pages.values()))
                if 'missing' in page_data:
                    logger.warning(f"Page '{title}' not found")
                    break
                    
                revisions = page_data.get('revisions', [])
                all_revisions.extend(revisions)
                
                # Check for continuation
                if 'continue' in data and 'rvcontinue' in data['continue']:
                    rvcontinue = data['continue']['rvcontinue']
                else:
                    break
                    
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error fetching revisions for {title}: {e}")
                break
                
        logger.info(f"Fetched {len(all_revisions)} revisions for '{title}'")
        return all_revisions

    async def _get_or_create_contributor(self, user_info: Dict[str, Any], language: str) -> Optional[Contributor]:
        """
        Get existing contributor or create new one
        获取现有贡献者或创建新的贡献者
        """
        try:
            from sqlalchemy import select
            
            user_id = user_info.get('userid')
            username = user_info.get('user', 'Anonymous')
            
            if not user_id:
                return None
                
            # Check if contributor already exists
            result = await self.db_session.execute(
                select(Contributor).where(Contributor.wikipedia_user_id == user_id)
            )
            contributor = result.scalar_one_or_none()
            
            if not contributor:
                contributor = Contributor(
                    wikipedia_user_id=user_id,
                    wikipedia_username=username,
                    display_name=username,
                    primary_language=language,
                    overall_impact_score=0.0,
                    is_active=True
                )
                self.db_session.add(contributor)
                await self.db_session.flush()  # Get the ID
                
            return contributor
            
        except Exception as e:
            logger.error(f"Error getting/creating contributor {user_info}: {e}")
            return None

    def _convert_to_edit_analysis(self, revision: Dict[str, Any]) -> EditAnalysis:
        """
        Convert Wikipedia revision to EditAnalysis format
        将Wikipedia修订版本转换为EditAnalysis格式
        """
        return EditAnalysis(
            timestamp=revision.get('timestamp', ''),
            size_change=revision.get('size', 0),
            comment=revision.get('comment', ''),
            is_minor=revision.get('minor', False),
            user_id=revision.get('userid'),
            username=revision.get('user', 'Anonymous')
        )

    async def analyze_wikipedia_page(self, page_url: str) -> int:
        """
        Main method to analyze a Wikipedia page
        分析Wikipedia页面的主要方法
        """
        try:
            title, lang = self._extract_page_info(page_url)
            logger.info(f"Starting analysis for '{title}' in language '{lang}'")
            
        except ValueError as e:
            logger.error(f"Invalid URL format: {e}")
            raise
            
        # Create analysis session
        analysis_session = AnalysisSession(
            page_title=title,
            page_url=page_url,
            page_language=lang,
            analysis_status="processing"
        )
        self.db_session.add(analysis_session)
        await self.db_session.commit()
        await self.db_session.refresh(analysis_session)

        try:
            revisions = await self._fetch_all_revisions(title, lang)
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