#!/usr/bin/env python3
"""
Weekly citation updater using Google Scholar scraping + Claude API for parsing.
Designed for cron: 0 3 * * 0 (every Sunday 3am UTC)
"""

import sqlite3
import json
import os
import sys
import time
import random
import logging
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'db', 'information_.db')
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
LOG_PATH = os.path.join(SCRIPT_DIR, 'citation_update.log')
SCHOLAR_PROFILE = 'DDLTYpAAAAAJ'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)


def fetch_url(url, retries=3):
    """Fetch URL with retry and random delay."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(3, 8))
            req = Request(url, headers=headers)
            resp = urlopen(req, timeout=30)
            return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            log.warning("Fetch attempt %d failed for %s: %s", attempt + 1, url[:80], e)
            if attempt < retries - 1:
                time.sleep(random.uniform(10, 20))
    return None


def fetch_scholar_profile():
    """Fetch Google Scholar profile page(s) to get all papers with citations."""
    all_html = []
    # Scholar shows 20 per page by default; use cstart for pagination
    for start in range(0, 200, 20):
        url = (
            'https://scholar.google.com/citations?user={}&hl=en'
            '&cstart={}&pagesize=20&sortby=pubdate'
        ).format(SCHOLAR_PROFILE, start)
        log.info("Fetching scholar page cstart=%d", start)
        html = fetch_url(url)
        if html is None:
            log.error("Failed to fetch scholar page at cstart=%d", start)
            break
        all_html.append(html)
        # If page has no more entries, stop
        if 'gsc_a_e' in html or html.count('gsc_a_tr') <= 1:
            # Check if there are actual results
            if 'There are no articles' in html or html.count('class="gsc_a_tr"') == 0:
                break
    return '\n<!-- PAGE_BREAK -->\n'.join(all_html)


def call_claude(prompt, max_tokens=4096):
    """Call Claude API using urllib (no SDK dependency)."""
    url = 'https://api.anthropic.com/v1/messages'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
    }
    body = json.dumps({
        'model': 'claude-haiku-4-5-20251001',
        'max_tokens': max_tokens,
        'messages': [{'role': 'user', 'content': prompt}]
    }).encode('utf-8')

    req = Request(url, data=body, headers=headers, method='POST')
    try:
        resp = urlopen(req, timeout=60)
        data = json.loads(resp.read().decode('utf-8'))
        return data['content'][0]['text']
    except Exception as e:
        log.error("Claude API call failed: %s", e)
        return None


def extract_scholar_rows(html):
    """Extract paper rows from Scholar HTML using simple string parsing."""
    rows = []
    # Split by table row markers
    parts = html.split('class="gsc_a_tr"')
    for part in parts[1:]:  # Skip first chunk (before first row)
        title = ''
        citations = 0
        # Extract title: inside <a class="gsc_a_at">...</a>
        at_start = part.find('class="gsc_a_at"')
        if at_start >= 0:
            tag_end = part.find('>', at_start)
            close_tag = part.find('</a>', tag_end)
            if tag_end >= 0 and close_tag >= 0:
                title = part[tag_end + 1:close_tag].strip()
        # Extract citation count: inside <a class="gsc_a_ac gs_ibl">NUMBER</a>
        ac_start = part.find('class="gsc_a_ac')
        if ac_start >= 0:
            tag_end = part.find('>', ac_start)
            close_tag = part.find('</a>', tag_end)
            if tag_end >= 0 and close_tag >= 0:
                cite_str = part[tag_end + 1:close_tag].strip()
                if cite_str.isdigit():
                    citations = int(cite_str)
        if title:
            rows.append('{} ||| {}'.format(title, citations))
    return rows


def parse_citations_with_ai(html):
    """Use Claude to extract paper titles and citation counts from Scholar HTML."""
    # Pre-extract rows to minimize tokens sent to Claude
    raw_rows = extract_scholar_rows(html)
    if not raw_rows:
        log.error("No rows extracted from Scholar HTML")
        return None

    log.info("Pre-extracted %d rows from HTML", len(raw_rows))

    rows_text = '\n'.join(raw_rows)
    prompt = (
        "I have pre-extracted paper data from Google Scholar in the format:\n"
        "TITLE ||| CITATION_COUNT\n\n"
        "Clean up the titles (decode HTML entities) and return a JSON array.\n"
        "Each element: {\"title\": \"clean title\", \"citations\": number}\n\n"
        "Return ONLY the JSON array, nothing else.\n\n"
        "Data:\n" + rows_text
    )

    log.info("Calling Claude API to parse citations...")
    result = call_claude(prompt)
    if result is None:
        return None

    # Extract JSON from response
    try:
        # Find JSON array in response
        start = result.find('[')
        end = result.rfind(']') + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except json.JSONDecodeError as e:
        log.error("Failed to parse Claude response as JSON: %s", e)

    return None


def update_database(citation_data):
    """Update SQLite database with new citation counts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all papers from DB
    cursor.execute("SELECT id, title FROM entries")
    db_papers = cursor.fetchall()

    updated = 0
    matched_db_ids = set()  # Track already-matched DB entries

    for paper in citation_data:
        scholar_title = paper['title'].strip().lower()
        citations = int(paper['citations'])

        best_match_id = None
        best_match_title = ''
        best_score = 0

        for db_id, db_title in db_papers:
            if db_id in matched_db_ids:
                continue
            db_title_lower = db_title.strip().lower()

            score = 0
            # Exact match
            if scholar_title == db_title_lower:
                score = 100
            # Scholar title contains DB title or vice versa
            elif scholar_title in db_title_lower or db_title_lower in scholar_title:
                score = 80
            # First 40 chars match (handles truncation)
            elif len(scholar_title) > 40 and scholar_title[:40] == db_title_lower[:40]:
                score = 70
            # Significant word overlap
            else:
                s_words = set(scholar_title.split())
                d_words = set(db_title_lower.split())
                if len(s_words) > 3 and len(d_words) > 3:
                    overlap = len(s_words & d_words) / max(len(s_words), len(d_words))
                    if overlap > 0.7:
                        score = int(overlap * 60)

            if score > best_score:
                best_score = score
                best_match_id = db_id
                best_match_title = db_title

        if best_match_id and best_score >= 50:
            cursor.execute("UPDATE entries SET cite = ? WHERE id = ?", (citations, best_match_id))
            if cursor.rowcount > 0:
                log.info("Updated [%d] %s -> %d citations (score=%d)", best_match_id, best_match_title[:50], citations, best_score)
                matched_db_ids.add(best_match_id)
                updated += 1

    conn.commit()

    # Summary
    cursor.execute("SELECT SUM(cite) FROM entries")
    total = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM entries WHERE cite > 0")
    with_citations = cursor.fetchone()[0]

    log.info("=== Update Summary ===")
    log.info("Papers updated: %d / %d", updated, len(db_papers))
    log.info("Papers with citations: %d", with_citations)
    log.info("Total citations: %d", total)

    conn.close()
    return updated, total


def main():
    log.info("=" * 50)
    log.info("Citation update started at %s", datetime.now().isoformat())

    if not API_KEY:
        log.error("ANTHROPIC_API_KEY not set. Exiting.")
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        log.error("Database not found at %s", DB_PATH)
        sys.exit(1)

    # Step 1: Fetch Google Scholar profile
    html = fetch_scholar_profile()
    if not html:
        log.error("Failed to fetch any Scholar data. Exiting.")
        sys.exit(1)
    log.info("Fetched %d bytes of Scholar HTML", len(html))

    # Step 2: Use Claude to parse citations
    citation_data = parse_citations_with_ai(html)
    if not citation_data:
        log.error("Failed to parse citations with AI. Exiting.")
        sys.exit(1)
    log.info("Parsed %d papers from Scholar", len(citation_data))

    # Step 3: Update database
    updated, total = update_database(citation_data)
    log.info("Done. %d papers updated, %d total citations.", updated, total)


if __name__ == '__main__':
    main()
