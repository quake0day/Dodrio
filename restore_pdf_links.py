#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to restore PDF and slide links based on files in static/paper/ and static/slides/
"""

import sqlite3
import os

def update_pdf_links():
    """Update database with PDF links based on existing files"""
    
    # Connect to database
    conn = sqlite3.connect('db/information_.db')
    cursor = conn.cursor()
    
    # Mapping of PDF filenames to paper keywords/patterns
    pdf_mappings = {
        # 2020-2025 papers
        'BORA_SC20.pdf': ('BORA', 2020),
        '21_IOT_2020.pdf': ('IoT', 2021),
        'CPE-21-0475.R3_Proof_hi.pdf': ('eBPF', 2022),
        
        # Privacy/Security papers
        'A_Privacy-Preserving_Medical_Data_Sharing_Scheme_Based_on_Blockchain.pdf': ('Privacy-Preserving Medical', 2022),
        'secure.pdf': ('Secure', None),
        
        # Voice/Acoustic papers
        '08395349.pdf': ('SRVoice', 2018),
        '07979966.pdf': ('Voice Spoofing', 2018),
        '08374505.pdf': ('PriWhisper+', 2018),
        '07164887.pdf': ('Acoustic', 2016),
        '06849232.pdf': ('PriWhisper', 2014),
        
        # Indoor/Crowd papers
        '06849220.pdf': ('Indoor Crowd', 2015),
        '06849233.pdf': ('CrowdMap', 2015),
        
        # Storage/File System papers
        'shang_ICPADS_2018.pdf': ('DuoFS', 2018),
        '19_TMC_Temple_jcshang_2020.pdf': ('SHC', 2019),
        
        # ICDCS 2017
        'ICDCS2017_Si.pdf': ('You Can Hear', 2017),
        
        # Location/Social Network
        '06704727.pdf': ('Location', 2014),
        
        # HF Communications
        '06419904.pdf': ('HF Communications', 2012),
        
        # Older papers
        '06273185.pdf': ('Seed Cotton', 2012),
        'Yuan2012_Chapter_ResearchOnTheK-CoverageLocalWi.pdf': ('k-Coverage', 2011),
        
        # Other papers
        'pap104s2.pdf': ('ADA', 2021),
        '08567538.pdf': ('ARSpy', 2022),
        '08855430.pdf': ('TTSVD', 2021),
        '2809695.2809702.pdf': ('Cybersecurity Education', 2019),
        '2632951.2632953.pdf': ('Parallel File System', 2023),
        'pacise22.pdf': ('Programming Skills', 2023),
        '3447080.fm.pdf': (None, None),  # Need to check content
    }
    
    # Slides mappings
    slides_mappings = {
        'Sensys15.pdf': ('Indoor Crowd', 2015),
        'badgerctf.pdf': ('Cybersecurity', None),
        'QCars_Liu_Si_Zhen.pdf': (None, None),
        'ICDCS17.pdf': ('You Can Hear', 2017),
    }
    
    # Update PDF links
    updated = 0
    for filename, (keyword, year) in pdf_mappings.items():
        if keyword:
            query = "UPDATE entries SET urlpdf = ? WHERE title LIKE ? "
            params = [f'/static/paper/{filename}', f'%{keyword}%']
            
            if year:
                query += " AND year = ?"
                params.append(year)
            
            cursor.execute(query, params)
            if cursor.rowcount > 0:
                print(f"Updated PDF link for '{keyword}' ({year}): {filename}")
                updated += cursor.rowcount
    
    # Update Slides links
    for filename, (keyword, year) in slides_mappings.items():
        if keyword:
            query = "UPDATE entries SET urlslides = ? WHERE title LIKE ? "
            params = [f'/static/slides/{filename}', f'%{keyword}%']
            
            if year:
                query += " AND year = ?"
                params.append(year)
            
            cursor.execute(query, params)
            if cursor.rowcount > 0:
                print(f"Updated slides link for '{keyword}' ({year}): {filename}")
                updated += cursor.rowcount
    
    # Special cases - update by exact title or other criteria
    special_updates = [
        ("UPDATE entries SET urlpdf = '/static/paper/08567538.pdf' WHERE title LIKE '%ARSpy%'", []),
        ("UPDATE entries SET urlpdf = '/static/paper/ICDCS2017_Si.pdf', urlslides = '/static/slides/ICDCS17.pdf' WHERE title LIKE '%You Can Hear%'", []),
        ("UPDATE entries SET urlslides = '/static/slides/Sensys15.pdf' WHERE title LIKE '%Indoor Crowd%' OR title LIKE '%CrowdMap%'", []),
    ]
    
    for query, params in special_updates:
        cursor.execute(query, params)
        if cursor.rowcount > 0:
            updated += cursor.rowcount
    
    # Commit changes
    conn.commit()
    
    # Show current status
    cursor.execute("SELECT COUNT(*) FROM entries WHERE urlpdf IS NOT NULL AND LENGTH(urlpdf) > 0")
    pdf_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM entries WHERE urlslides IS NOT NULL AND LENGTH(urlslides) > 0")
    slides_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM entries WHERE urlpaper IS NOT NULL AND LENGTH(urlpaper) > 0")
    paper_count = cursor.fetchone()[0]
    
    print(f"\nDatabase status:")
    print(f"- Papers with PDF links: {pdf_count}")
    print(f"- Papers with slides: {slides_count}")
    print(f"- Papers with external links: {paper_count}")
    print(f"- Total updates made: {updated}")
    
    conn.close()

if __name__ == "__main__":
    update_pdf_links()