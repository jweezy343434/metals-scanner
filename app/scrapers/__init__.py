"""
Scrapers package - exports all scraper classes
"""
from app.scrapers.base import BaseScraper
from app.scrapers.ebay import EbayScraper

__all__ = ['BaseScraper', 'EbayScraper']
