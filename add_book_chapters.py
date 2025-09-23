#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('db/information_.db')
cursor = conn.cursor()

# Book chapter entries
book_chapters = [
    {
        'title': 'Network Security Empowered by Artificial Intelligence (Chapter: Securing Augmented Reality Applications)',
        'author': 'Si Chen',
        'confname': 'Book Chapter, Network Security Empowered by Artificial Intelligence, Springer',
        'year': 2024,
        'type': 4,  # Book type
        'urlpaper': 'https://www.google.com/books/edition/Network_Security_Empowered_by_Artificial/cWkQEQAAQBAJ?hl=en&gbpv=1&printsec=frontcover',
        'cite': 0,
        'urlcite': 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C39&q=Network+Security+Empowered+by+Artificial+Intelligence+Si+Chen',
        'urlslides': '',
        'place': '',
        'text': '',
        'video': '',
        'cluster': ''
    },
    {
        'title': 'Encyclopedia of Wireless Networks (Section: Security, Privacy, and Trust)',
        'author': 'Si Chen',
        'confname': 'Book Chapter, Encyclopedia of Wireless Networks, Springer',
        'year': 2017,
        'type': 4,  # Book type
        'urlpaper': 'https://www.springer.com/us/book/9783319782638',
        'cite': 0,
        'urlcite': 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C39&q=Encyclopedia+of+Wireless+Networks+Si+Chen',
        'urlslides': '',
        'place': '',
        'text': '',
        'video': '',
        'cluster': ''
    }
]

# Insert book chapters
for chapter in book_chapters:
    # Check if entry already exists
    cursor.execute("SELECT id FROM entries WHERE title = ?", (chapter['title'],))
    if cursor.fetchone() is None:
        # Insert new entry
        cursor.execute("""
            INSERT INTO entries (title, author, confname, year, type, urlpaper, cite, 
                                urlcite, urlslides, place, text, video, cluster)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (chapter['title'], chapter['author'], chapter['confname'], chapter['year'],
              chapter['type'], chapter['urlpaper'], chapter['cite'], chapter['urlcite'],
              chapter['urlslides'], chapter['place'], chapter['text'],
              chapter['video'], chapter['cluster']))
        print(f"Added: {chapter['title']}")
    else:
        # Update existing entry
        cursor.execute("""
            UPDATE entries 
            SET author=?, confname=?, year=?, type=?, urlpaper=?, urlcite=?, cite=?
            WHERE title=?
        """, (chapter['author'], chapter['confname'], chapter['year'], chapter['type'],
              chapter['urlpaper'], chapter['urlcite'], chapter['cite'], chapter['title']))
        print(f"Updated: {chapter['title']}")

# Commit changes
conn.commit()

# Show current book chapters
cursor.execute("SELECT id, title, year FROM entries WHERE type = 4 ORDER BY year DESC")
books = cursor.fetchall()
print(f"\nTotal book chapters in database: {len(books)}")
for book in books:
    print(f"  ID {book[0]}: {book[2]} - {book[1][:80]}...")

conn.close()
print("\nBook chapters successfully added to database!")