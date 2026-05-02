"""Collection API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api", tags=["collection"])


class CollectRequest(BaseModel):
    """Request to collect a single item."""
    url: str
    platform: str = "bilibili"
    quality: str = "fast"
    style: Optional[str] = None


class BatchCollectRequest(BaseModel):
    """Request to collect multiple items."""
    urls: List[str]
    platform: str = "bilibili"
    quality: str = "fast"


class ImportRequest(BaseModel):
    """Request to import local files."""
    directory: str
    recursive: bool = True
    update_existing: bool = True


@router.post("/collect")
async def collect_item(request: CollectRequest):
    """Collect a single item (video/article)."""
    from Athena.Aegis.core.service import create_service
    
    try:
        service = create_service()
        
        result = service.collect_video(
            video_url=request.url,
            platform=request.platform,
            quality=request.quality,
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect/batch")
async def batch_collect(request: BatchCollectRequest):
    """Collect multiple items."""
    from Athena.Aegis.core.service import create_service
    
    try:
        service = create_service()
        
        results = service.batch_collect(
            video_urls=request.urls,
            platform=request.platform,
            quality=request.quality,
        )
        
        return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_files(request: ImportRequest):
    """Import local markdown files."""
    from Athena.Aegis.core.service import create_service
    
    try:
        service = create_service()
        
        result = service.import_local(
            directory=request.directory,
            recursive=request.recursive,
        )
        
        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get collection status."""
    from Athena.Aegis.core.service import create_service
    
    try:
        service = create_service()
        return service.get_status()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending(platform: Optional[str] = None):
    """Get pending items."""
    from Athena.Aegis.core.service import create_service
    
    try:
        service = create_service()
        pending = service.get_pending(platform)
        
        return [
            {
                "platform": p.platform,
                "item_id": p.item_id,
                "url": p.url,
                "title": p.title,
                "status": p.status,
            }
            for p in pending
        ]
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))