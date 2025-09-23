#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update citation counts from Google Scholar data
"""

import sqlite3

def update_citations():
    """Update citation counts in database based on Google Scholar data"""
    
    # Citation data from Google Scholar (as provided by user)
    citation_data = {
        "All your location are belong to us": 183,
        "You Can Hear But You Cannot Steal": 164,
        "Crowd map": 117,
        "CrowdMap": 117,  # Same paper, different case
        "PriWhisper": 95,
        "Enabling Keyless Secure Acoustic Communication": 95,
        "A privacy-preserving medical data sharing scheme based on blockchain": 75,
        "Rise of the indoor crowd": 75,
        "ARSpy": 67,
        "Breaking location-based multi-player augmented reality": 67,
        "TT-SVD": 51,
        "TTSVD": 51,  # Alternative spelling
        "Defending Against Voice Spoofing": 37,
        "Srvoice": 13,
        "SRVoice": 13,  # Alternative case
        "PriWhisper+": 13,
        "Classification model of seed cotton": 9,
        "DuoFS": 8,
        "Network simulation for advanced HF": 8,
        "BORA": 6,
        "The power of indoor crowd": 5,
        "AcousAuth": 4,
        "Securing acoustics-based short-range communication": 3,
        "User-level parallel file system": 2,
        "User‐level parallel file system": 2,  # Alternative dash
        "Authentication": 2,
        "k-Coverage": 2,
        "Securing Augmented Reality Applications": 1,
        "ADA": 1,
        "SHC": 1,
        "COMPUTING INFRASTRUCTURES": 1,
        "Quality of Experience": 1,
        "LipTalk": 1,
        "Movement and deformation": 1,
        "eBPF": 0,
        "EXTENDED BERKELEY PACKET FILTER": 0,
        "Containerizing CS": 0,
        "SIMULATION AND MODELS": 0,
    }
    
    # Connect to database
    conn = sqlite3.connect('db/information_.db')
    cursor = conn.cursor()
    
    # First, set all citations to 0 (for papers not in Scholar)
    cursor.execute("UPDATE entries SET cite = 0")
    
    # Update citations based on title matching
    updated_count = 0
    for title_fragment, citations in citation_data.items():
        # Try to match papers by partial title
        cursor.execute(
            "UPDATE entries SET cite = ? WHERE UPPER(title) LIKE UPPER(?)",
            (citations, f'%{title_fragment}%')
        )
        if cursor.rowcount > 0:
            print(f"Updated '{title_fragment}' with {citations} citations")
            updated_count += cursor.rowcount
    
    # Special updates for specific papers with exact matches
    special_updates = [
        ("UPDATE entries SET cite = 183 WHERE title LIKE '%All Your Location Are Belong to Us%'", []),
        ("UPDATE entries SET cite = 164 WHERE title LIKE '%You Can Hear But You Cannot Steal%'", []),
        ("UPDATE entries SET cite = 117 WHERE title LIKE '%CrowdMap%' OR title LIKE '%Crowd Map%'", []),
        ("UPDATE entries SET cite = 95 WHERE title LIKE '%PriWhisper:%' AND year = 2014", []),
        ("UPDATE entries SET cite = 75 WHERE title LIKE '%Privacy-Preserving Medical%'", []),
        ("UPDATE entries SET cite = 75 WHERE title LIKE '%Rise of the Indoor Crowd%'", []),
        ("UPDATE entries SET cite = 67 WHERE title LIKE '%ARSpy%'", []),
        ("UPDATE entries SET cite = 51 WHERE title LIKE '%TTSVD%' OR title LIKE '%TT-SVD%'", []),
        ("UPDATE entries SET cite = 37 WHERE title LIKE '%Voice Spoofing%' AND title LIKE '%Defending%'", []),
        ("UPDATE entries SET cite = 13 WHERE title LIKE '%SRVoice%'", []),
        ("UPDATE entries SET cite = 13 WHERE title LIKE '%PriWhisper+%'", []),
        ("UPDATE entries SET cite = 9 WHERE title LIKE '%Seed Cotton%'", []),
        ("UPDATE entries SET cite = 8 WHERE title LIKE '%DuoFS%'", []),
        ("UPDATE entries SET cite = 8 WHERE title LIKE '%HF Communications%'", []),
        ("UPDATE entries SET cite = 6 WHERE title LIKE '%BORA%' AND year = 2020", []),
        ("UPDATE entries SET cite = 2 WHERE title LIKE '%User-Level Parallel File System%'", []),
        ("UPDATE entries SET cite = 2 WHERE title LIKE '%k-Coverage%' AND year = 2011", []),
        ("UPDATE entries SET cite = 1 WHERE title LIKE '%ADA%' AND year = 2021", []),
        ("UPDATE entries SET cite = 1 WHERE title LIKE '%SHC%' AND year = 2019", []),
        ("UPDATE entries SET cite = 1 WHERE title LIKE '%Cybersecurity Education%' AND year = 2019", []),
        ("UPDATE entries SET cite = 1 WHERE title LIKE '%Movement and Deformation%' AND year = 2012", []),
        ("UPDATE entries SET cite = 0 WHERE title LIKE '%eBPF%' OR title LIKE '%Extended Berkeley Packet Filter%'", []),
        ("UPDATE entries SET cite = 0 WHERE title LIKE '%Programming Skills%' AND year = 2023", []),
        ("UPDATE entries SET cite = 0 WHERE title LIKE '%Aligning LLMs%' AND year = 2025", []),
        ("UPDATE entries SET cite = 0 WHERE title LIKE '%Future of Teaching%' AND year = 2025", []),
    ]
    
    for query, params in special_updates:
        cursor.execute(query, params)
        if cursor.rowcount > 0:
            updated_count += cursor.rowcount
    
    # Commit changes
    conn.commit()
    
    # Get summary statistics
    cursor.execute("SELECT COUNT(*) FROM entries WHERE cite > 0")
    papers_with_citations = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(cite) FROM entries")
    total_citations = cursor.fetchone()[0]
    
    cursor.execute("SELECT title, cite FROM entries ORDER BY cite DESC LIMIT 5")
    top_papers = cursor.fetchall()
    
    print(f"\nUpdate complete!")
    print(f"Total papers updated: {updated_count}")
    print(f"Papers with citations: {papers_with_citations}")
    print(f"Total citations: {total_citations}")
    print(f"\nTop 5 cited papers:")
    for title, cite in top_papers:
        print(f"  - {title[:60]}... : {cite} citations")
    
    conn.close()

if __name__ == "__main__":
    update_citations()