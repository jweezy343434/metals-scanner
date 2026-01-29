"""
FastAPI application for metals arbitrage scanner
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import sys
from pathlib import Path

from app.database import (
    init_db,
    get_db,
    Listing,
    SpotPrice,
    RateLimitTracker,
    APICallLog
)
from app.config import settings
from app.schemas import (
    ListingResponse,
    SpotPriceResponse,
    ScanResult,
    DealsSummary,
    HealthCheck,
    RateLimitStatus,
    DealsQuery,
    ScanRequest,
    ErrorResponse,
    MetalType
)
from app.exceptions import (
    APIRateLimitError,
    APIConnectionError,
    MetalsScannerException
)
from app.scrapers import EbayScraper
from app.price_api import metals_api_client
from app.rate_limiter import rate_limiter
from app.scheduler import start_scheduler, stop_scheduler, get_scheduler_status

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/metals_scanner.log')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Metals Arbitrage Scanner",
    description="Production-ready metals arbitrage scanner with rate limiting and caching",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(APIRateLimitError)
async def rate_limit_handler(request, exc: APIRateLimitError):
    """Handle rate limit errors with 429 status"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": str(exc),
            "api_name": exc.api_name,
            "limit": exc.limit,
            "retry_after": exc.reset_at
        }
    )


@app.exception_handler(APIConnectionError)
async def api_connection_handler(request, exc: APIConnectionError):
    """Handle API connection errors with 503 status"""
    return JSONResponse(
        status_code=503,
        content={
            "error": "External API unavailable",
            "detail": str(exc),
            "api_name": exc.api_name
        }
    )


@app.exception_handler(MetalsScannerException)
async def scanner_exception_handler(request, exc: MetalsScannerException):
    """Handle general scanner exceptions"""
    logger.error(f"Scanner exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Scanner error",
            "detail": str(exc)
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Metals Arbitrage Scanner...")

    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Start scheduler
        start_scheduler(perform_scheduled_scan)
        logger.info("Background scheduler started")

        logger.info("Application startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    stop_scheduler()
    logger.info("Shutdown complete")


# Helper functions
def calculate_spread(listing_price: float, weight_oz: float, spot_price: float) -> float:
    """
    Calculate spread percentage
    Positive = good deal (below spot), Negative = above spot
    """
    if not weight_oz or weight_oz <= 0:
        return None

    spot_value = weight_oz * spot_price
    if spot_value <= 0:
        return None

    spread_pct = ((spot_value - listing_price) / spot_value) * 100
    return round(spread_pct, 2)


def perform_scheduled_scan():
    """Background scan function called by scheduler"""
    logger.info("Scheduled scan started")
    try:
        with next(get_db()) as db:
            result = perform_scan(db)
            logger.info(
                f"Scheduled scan completed: {result['listings_found']} listings, "
                f"{result['deals_found']} deals"
            )
    except Exception as e:
        logger.error(f"Scheduled scan failed: {e}")


def perform_scan(db: Session, search_terms: List[str] = None, max_results: int = 100) -> dict:
    """
    Perform a full scan: scrape eBay and calculate spreads
    Returns dict with scan results
    """
    start_time = datetime.utcnow()
    errors = []
    listings_found = 0
    deals_found = 0

    try:
        # Get spot prices
        logger.info("Fetching spot prices...")
        spot_prices = metals_api_client.get_spot_prices(db)

        if not spot_prices.get('gold') or not spot_prices.get('silver'):
            errors.append("Failed to fetch spot prices")
            logger.warning("Spot prices unavailable, using cached values")

        # Scrape eBay
        logger.info("Scraping eBay listings...")
        scraper = EbayScraper()
        listings = scraper.scrape(search_terms=search_terms, max_results=max_results, db=db)
        listings_found = len(listings)

        # Process listings
        for listing_data in listings:
            try:
                # Check if listing already exists
                existing = db.query(Listing).filter(
                    Listing.external_id == listing_data['external_id']
                ).first()

                if existing:
                    # Update existing listing
                    existing.price = listing_data['price']
                    existing.fetched_at = datetime.utcnow()
                else:
                    # Create new listing
                    existing = Listing(**listing_data)
                    db.add(existing)

                # Calculate spread if weight is available
                metal_type = listing_data['metal_type']
                weight_oz = listing_data.get('weight_oz')

                if weight_oz and spot_prices.get(metal_type):
                    spread = calculate_spread(
                        listing_data['price'],
                        weight_oz,
                        spot_prices[metal_type]
                    )
                    existing.spread_percentage = spread

                    if spread and spread > 0:
                        deals_found += 1

                db.commit()

            except Exception as e:
                logger.error(f"Failed to process listing: {e}")
                errors.append(f"Listing processing error: {str(e)}")
                db.rollback()

    except APIRateLimitError as e:
        errors.append(f"Rate limit exceeded: {str(e)}")
        logger.error(f"Scan failed - rate limit: {e}")
    except APIConnectionError as e:
        errors.append(f"API connection failed: {str(e)}")
        logger.error(f"Scan failed - connection: {e}")
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        logger.error(f"Scan failed: {e}")

    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()

    return {
        "success": len(errors) == 0,
        "listings_found": listings_found,
        "deals_found": deals_found,
        "errors": errors,
        "started_at": start_time,
        "completed_at": end_time,
        "duration_seconds": round(duration, 2)
    }


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard"""
    html_file = Path("/app/app/static/index.html")
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text())
    else:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/api/listings", response_model=List[ListingResponse])
async def get_listings(
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all listings with computed spreads"""
    listings = db.query(Listing).order_by(
        desc(Listing.spread_percentage)
    ).limit(limit).all()

    return listings


@app.get("/api/deals", response_model=List[ListingResponse])
async def get_deals(
    threshold: float = Query(default=0.0, ge=0.0, le=100.0),
    metal_type: Optional[str] = Query(default=None),
    min_weight: Optional[float] = Query(default=None, ge=0.0),
    max_results: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Filter listings by spread threshold and other criteria"""
    query = db.query(Listing).filter(
        Listing.spread_percentage >= threshold,
        Listing.weight_oz.isnot(None)
    )

    # Filter by metal type
    if metal_type and metal_type.lower() != 'all':
        query = query.filter(Listing.metal_type == metal_type.lower())

    # Filter by minimum weight
    if min_weight:
        query = query.filter(Listing.weight_oz >= min_weight)

    # Order by spread (best deals first)
    deals = query.order_by(desc(Listing.spread_percentage)).limit(max_results).all()

    return deals


@app.post("/api/scan", response_model=ScanResult)
async def trigger_scan(
    request: ScanRequest = ScanRequest(),
    db: Session = Depends(get_db)
):
    """Trigger a manual scan"""
    logger.info("Manual scan triggered via API")

    # Convert metal types to search terms
    search_terms = []
    for metal in request.metal_types:
        if metal == MetalType.GOLD:
            search_terms.extend(["gold bullion", "gold eagle"])
        elif metal == MetalType.SILVER:
            search_terms.extend(["silver bullion", "silver eagle"])

    result = perform_scan(
        db,
        search_terms=search_terms if search_terms else None,
        max_results=request.max_results_per_search
    )

    return ScanResult(**result)


@app.get("/api/spot-prices", response_model=List[SpotPriceResponse])
async def get_spot_prices(db: Session = Depends(get_db)):
    """Get current spot prices with age information"""
    prices = []
    now = datetime.utcnow()

    for metal_type in ['gold', 'silver']:
        latest = db.query(SpotPrice).filter(
            SpotPrice.metal_type == metal_type
        ).order_by(desc(SpotPrice.fetched_at)).first()

        if latest:
            age_minutes = int((now - latest.fetched_at).total_seconds() / 60)
            prices.append(
                SpotPriceResponse(
                    metal_type=latest.metal_type,
                    price_per_oz=latest.price_per_oz,
                    fetched_at=latest.fetched_at,
                    age_minutes=age_minutes
                )
            )

    return prices


@app.get("/api/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """System health check"""
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    # Get last scan time
    last_listing = db.query(Listing).order_by(desc(Listing.fetched_at)).first()
    last_scan = last_listing.fetched_at if last_listing else None

    # Get rate limit status
    ebay_status = rate_limiter.get_status("ebay", db)
    metals_status = rate_limiter.get_status("metals-api", db)

    return HealthCheck(
        status="healthy" if db_status == "ok" else "unhealthy",
        database=db_status,
        last_scan=last_scan,
        ebay_rate_limit_remaining=ebay_status['calls_remaining'] if ebay_status else None,
        metals_api_rate_limit_remaining=metals_status['calls_remaining'] if metals_status else None,
        timestamp=datetime.utcnow()
    )


@app.get("/api/rate-limits", response_model=List[RateLimitStatus])
async def get_rate_limits(db: Session = Depends(get_db)):
    """Get current API quota status"""
    statuses = rate_limiter.get_all_statuses(db)
    return [RateLimitStatus(**s) for s in statuses if s]


@app.get("/api/deals-summary", response_model=DealsSummary)
async def get_deals_summary(
    threshold: float = Query(default=0.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db)
):
    """Get statistics about current deals"""
    # Total deals above threshold
    total_deals = db.query(Listing).filter(
        Listing.spread_percentage >= threshold,
        Listing.weight_oz.isnot(None)
    ).count()

    # Gold deals
    gold_deals = db.query(Listing).filter(
        Listing.metal_type == 'gold',
        Listing.spread_percentage >= threshold,
        Listing.weight_oz.isnot(None)
    ).count()

    # Silver deals
    silver_deals = db.query(Listing).filter(
        Listing.metal_type == 'silver',
        Listing.spread_percentage >= threshold,
        Listing.weight_oz.isnot(None)
    ).count()

    # Best spread
    best_deal = db.query(Listing).filter(
        Listing.spread_percentage >= threshold,
        Listing.weight_oz.isnot(None)
    ).order_by(desc(Listing.spread_percentage)).first()

    # Average spread
    avg_spread = db.query(func.avg(Listing.spread_percentage)).filter(
        Listing.spread_percentage >= threshold,
        Listing.weight_oz.isnot(None)
    ).scalar()

    # Calculate potential savings
    spot_prices = metals_api_client.get_cached_prices_only(db)
    total_savings = 0.0

    if spot_prices.get('gold') and spot_prices.get('silver'):
        deals = db.query(Listing).filter(
            Listing.spread_percentage >= threshold,
            Listing.weight_oz.isnot(None)
        ).all()

        for deal in deals:
            spot_price = spot_prices.get(deal.metal_type)
            if spot_price and deal.weight_oz:
                spot_value = deal.weight_oz * spot_price
                savings = spot_value - deal.price
                if savings > 0:
                    total_savings += savings

    return DealsSummary(
        total_deals=total_deals,
        gold_deals=gold_deals,
        silver_deals=silver_deals,
        best_spread_percentage=best_deal.spread_percentage if best_deal else None,
        average_spread_percentage=round(avg_spread, 2) if avg_spread else None,
        total_potential_savings=round(total_savings, 2) if total_savings > 0 else None
    )


@app.get("/api/scheduler-status")
async def get_scheduler_status_endpoint():
    """Get background scheduler status"""
    return get_scheduler_status()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
