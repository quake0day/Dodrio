#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to restore and update official paper URLs
"""

import sqlite3

def update_official_urls():
    """Update database with official paper URLs from backup and new sources"""
    
    # Connect to both databases
    conn = sqlite3.connect('db/information_.db')
    cursor = conn.cursor()
    
    # First, restore URLs from backup
    cursor.execute("ATTACH DATABASE 'db/information_ copy.db' AS backup")
    
    # Restore existing official URLs from backup
    cursor.execute("""
        UPDATE main.entries 
        SET urlpaper = (
            SELECT urlpaper FROM backup.entries 
            WHERE backup.entries.title = main.entries.title 
            AND backup.entries.urlpaper IS NOT NULL 
            AND LENGTH(backup.entries.urlpaper) > 5
        )
        WHERE EXISTS (
            SELECT 1 FROM backup.entries 
            WHERE backup.entries.title = main.entries.title 
            AND backup.entries.urlpaper IS NOT NULL 
            AND LENGTH(backup.entries.urlpaper) > 5
        )
    """)
    
    print(f"Restored {cursor.rowcount} URLs from backup")
    
    # Now add/update with known official URLs
    official_urls = {
        # 2017 papers
        "You Can Hear But You Cannot Steal": "https://ieeexplore.ieee.org/document/7979966/",
        
        # 2015 papers  
        "CrowdMap": "https://ieeexplore.ieee.org/document/7164887",
        "Rise of the Indoor Crowd": "https://dl.acm.org/doi/10.1145/2809695.2809702",
        
        # 2014 papers
        "All Your Location Are Belong to Us": "https://dl.acm.org/doi/10.1145/2594368.2594382",
        "PriWhisper: Enabling Keyless": "https://ieeexplore.ieee.org/document/6704727",
        "The power of indoor crowd": "https://ieeexplore.ieee.org/document/6849233",
        "AcousAuth": "https://ieeexplore.ieee.org/document/6849232",
        "Enabling private and non-intrusive": "https://ieeexplore.ieee.org/document/6849220",
        
        # 2018 papers
        "PriWhisper+": "https://ieeexplore.ieee.org/document/8395349/",
        "Defending Against Voice Spoofing": "https://ieeexplore.ieee.org/document/8567538",
        "DuoFS": "https://ieeexplore.ieee.org/document/8374505/",
        "SRVoice": "https://ieeexplore.ieee.org/document/8644547",
        
        # 2022 papers
        "ARSpy": "https://ieeexplore.ieee.org/document/8855430",
        "A Privacy-Preserving Medical": "https://ieeexplore.ieee.org/document/9606596",
        
        # 2021 papers
        "TTSVD": "https://ieeexplore.ieee.org/document/9355704",
        
        # 2020 papers
        "BORA": "https://dl.acm.org/doi/10.1109/SC41405.2020.00079",
        
        # 2019 papers
        "SHC": "https://ieeexplore.ieee.org/document/8885638",
        
        # 2016 papers
        "Securing Acoustics-Based": "http://www.infocomm-journal.com/jcin/EN/10.11959/j.issn.2096-1081.2016.055",
        
        # 2012 papers
        "Network simulation for advanced HF": "https://digital-library.theiet.org/content/conferences/10.1049/cp.2012.0377",
        "Classification Model of Seed Cotton": "https://ieeexplore.ieee.org/document/6419904",
        "Movement and deformation": "https://ieeexplore.ieee.org/document/6273185",
        
        # 2011 papers
        "Research on the k-Coverage": "https://link.springer.com/chapter/10.1007/978-3-642-27281-3_45",
        
        # 2023 papers
        "User-Level Parallel File System": "https://onlinelibrary.wiley.com/doi/10.1002/cpe.6905",
        
        # 2025 papers (arXiv)
        "Aligning LLMs for the Classroom": "https://arxiv.org/abs/2509.07846",
    }
    
    # Update with official URLs
    updated = 0
    for title_fragment, url in official_urls.items():
        cursor.execute(
            "UPDATE entries SET urlpaper = ? WHERE title LIKE ?",
            (url, f'%{title_fragment}%')
        )
        if cursor.rowcount > 0:
            print(f"Updated URL for '{title_fragment[:30]}...'")
            updated += cursor.rowcount
    
    # Additional specific updates for papers with DOI
    doi_updates = [
        ("UPDATE entries SET urlpaper = 'https://dl.acm.org/doi/10.1145/2809695.2809702' WHERE title LIKE '%Rise of the Indoor Crowd%'", []),
        ("UPDATE entries SET urlpaper = 'https://dl.acm.org/doi/10.1145/2594368.2594382' WHERE title LIKE '%All Your Location%'", []),
        ("UPDATE entries SET urlpaper = 'https://ieeexplore.ieee.org/document/8855430' WHERE title LIKE '%ARSpy%' AND year = 2022", []),
        ("UPDATE entries SET urlpaper = 'https://ieeexplore.ieee.org/document/9606596' WHERE title LIKE '%Privacy-Preserving Medical%'", []),
        ("UPDATE entries SET urlpaper = 'https://ieeexplore.ieee.org/document/9355704' WHERE title LIKE '%TTSVD%' OR title LIKE '%TT-SVD%'", []),
        ("UPDATE entries SET urlpaper = 'https://dl.acm.org/doi/10.1109/SC41405.2020.00079' WHERE title LIKE '%BORA%' AND year = 2020", []),
        ("UPDATE entries SET urlpaper = 'https://ieeexplore.ieee.org/document/8885638' WHERE title LIKE '%SHC%' AND year = 2019", []),
        ("UPDATE entries SET urlpaper = 'https://onlinelibrary.wiley.com/doi/10.1002/cpe.6905' WHERE title LIKE '%User-Level Parallel%' OR title LIKE '%User‐Level Parallel%'", []),
        ("UPDATE entries SET urlpaper = 'https://dl.acm.org/doi/10.1145/3502181.3531472' WHERE title LIKE '%ADA%' AND year = 2021", []),
    ]
    
    for query, params in doi_updates:
        cursor.execute(query, params)
        if cursor.rowcount > 0:
            updated += cursor.rowcount
    
    # Commit all changes
    conn.commit()
    
    # Get summary
    cursor.execute("SELECT COUNT(*) FROM entries WHERE urlpaper IS NOT NULL AND LENGTH(urlpaper) > 5")
    papers_with_urls = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM entries")
    total_papers = cursor.fetchone()[0]
    
    # Show some examples
    cursor.execute("SELECT substr(title, 1, 40), urlpaper FROM entries WHERE urlpaper IS NOT NULL AND urlpaper LIKE 'http%' LIMIT 10")
    examples = cursor.fetchall()
    
    print(f"\n✅ Update complete!")
    print(f"Total papers with official URLs: {papers_with_urls}/{total_papers}")
    print(f"Papers updated in this run: {updated}")
    print(f"\nExample URLs:")
    for title, url in examples:
        print(f"  - {title}...")
        print(f"    URL: {url[:60]}...")
    
    conn.close()

if __name__ == "__main__":
    update_official_urls()