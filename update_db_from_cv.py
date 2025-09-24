#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to parse CV_V2.tex and update the publications database
"""

import re
import sqlite3
import os

def parse_cv_publications(cv_file):
    """Parse the CV LaTeX file and extract publication information"""
    
    with open(cv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    publications = []
    
    # Remove newlines for easier parsing
    content = content.replace('\n', ' ')
    
    # Find all \publication commands - using a more robust regex
    # Pattern matches \publication{authors}{title}{venue}  or with additional 4th argument
    pattern = r'\\publication\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    
    matches = re.findall(pattern, content)
    
    for match in matches:
        authors = match[0].strip()
        title = match[1].strip()
        venue = match[2].strip()
        
        # Look for any text after the venue closing brace (additional info)
        additional = ""
        
        # Clean up LaTeX formatting
        authors = re.sub(r'\\textbf\{([^}]*)\}', r'\1', authors)
        title = re.sub(r'\\textbf\{([^}]*)\}', r'\1', title)
        venue = re.sub(r'\\textbf\{([^}]*)\}', r'\1', venue)
        venue = re.sub(r'\\textit\{([^}]*)\}', r'\1', venue)
        
        # Extract year from venue
        year_match = re.search(r'20\d{2}', venue)
        year = int(year_match.group()) if year_match else 2024
        
        # Determine if it's a journal (type=2) or conference (type=1)
        pub_type = 2 if any(x in venue for x in ['Journal', 'Magazine', 'Transactions', 'Concurrency and Computation', 'IEEE Internet of Things']) else 1
        
        # Extract location if it's a conference
        location_patterns = [
            r', ([^,]+), 20\d{2}',  # Location, Year
            r', ([^,]+), [A-Z][a-z]+ \d+-?\d*, 20\d{2}',  # Location, Date, Year
        ]
        location = ""
        for pat in location_patterns:
            location_match = re.search(pat, venue)
            if location_match:
                location = location_match.group(1)
                break
        
        # Check for special mentions in the following text
        # Look for text after this publication until the next \publication or end
        pub_pos = content.find('\\publication{' + authors[:30])
        if pub_pos != -1:
            next_pub = content.find('\\publication{', pub_pos + 10)
            if next_pub == -1:
                next_pub = len(content)
            additional_text = content[pub_pos:next_pub]
            
            # Check for special mentions
            best_paper = "Best Paper Award" in additional_text or "Best Student Paper Award" in additional_text
            high_citations = "Citations" in additional_text and "100" in additional_text
            acceptance_ratio_match = re.search(r'Acceptance ratio.*?=.*?(\d+\.?\d*)', additional_text)
            media_coverage = "Media coverage" in additional_text
            
            # Initial citation count (will be updated later)
            citations = 100 if high_citations else 0
            
            additional = ""
            if best_paper:
                additional += "Best Paper Award. "
            if acceptance_ratio_match:
                additional += f"Acceptance ratio = {acceptance_ratio_match.group(1)}%. "
            if media_coverage:
                additional += "Media coverage: Scientific American, Phys.org, CBS, etc. "
        else:
            best_paper = False
            citations = 0
            additional = ""
        
        publications.append({
            'type': pub_type,
            'title': title,
            'authors': authors,
            'venue': venue,
            'year': year,
            'location': location,
            'citations': citations,
            'best_paper': best_paper,
            'additional': additional
        })
    
    return publications

def update_database(publications):
    """Update the database with new publications"""
    
    # Connect to database
    db_path = 'db/information_.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, save existing URLs
    cursor.execute("SELECT title, urlpaper, urlslides, urlpdf FROM entries WHERE urlpaper != '' OR urlslides != '' OR urlpdf != ''")
    existing_urls = {row[0]: {'urlpaper': row[1], 'urlslides': row[2], 'urlpdf': row[3]} for row in cursor.fetchall()}
    
    # Clear existing entries to replace with updated data
    cursor.execute("DELETE FROM entries")
    
    # Insert publications
    for pub in publications:
        # Prepare data - preserve existing URLs if available
        existing = existing_urls.get(pub['title'], {})
        urlpaper = existing.get('urlpaper', "")
        urlslides = existing.get('urlslides', "")
        urlpdf = existing.get('urlpdf', "")
        urlcite = f"http://scholar.google.com/scholar?q={pub['title'].replace(' ', '+')}"
        video = ""
        cluster = ""
        
        # Insert into database
        cursor.execute("""
            INSERT INTO entries (type, title, author, confname, urlpaper, urlslides, 
                               urlcite, cite, place, year, text, video, cluster, urlpdf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pub['type'],
            pub['title'],
            pub['authors'],
            pub['venue'],
            urlpaper,
            urlslides,
            urlcite,
            pub['citations'],
            pub['location'],
            pub['year'],
            pub['additional'],
            video,
            cluster,
            urlpdf
        ))
    
    # Commit changes
    conn.commit()
    
    # Get count of new entries
    cursor.execute("SELECT COUNT(*) FROM entries")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    return total_count

def main():
    """Main function"""
    
    print("Parsing CV_V2.tex...")
    publications = parse_cv_publications('CV_V2.tex')
    
    print(f"Found {len(publications)} publications")
    print("\nSample publications:")
    for pub in publications[:5]:
        print(f"- {pub['title'][:60]}... ({pub['year']})")
        print(f"  Authors: {pub['authors'][:60]}...")
        print(f"  Type: {'Journal' if pub['type'] == 2 else 'Conference'}")
        print()
    
    print("\nUpdating database...")
    total = update_database(publications)
    
    print(f"Database updated successfully! Total entries: {total}")
    
    # Print statistics
    conf_count = sum(1 for p in publications if p['type'] == 1)
    journal_count = sum(1 for p in publications if p['type'] == 2)
    
    print(f"\nStatistics:")
    print(f"- Conference papers: {conf_count}")
    print(f"- Journal articles: {journal_count}")
    if publications:
        print(f"- Years covered: {min(p['year'] for p in publications)} - {max(p['year'] for p in publications)}")

if __name__ == "__main__":
    main()