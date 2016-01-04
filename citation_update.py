from scrape_publication import scrape_paper
from scrape_author import scrape_author
import os
import sqlite3
import difflib

def update_citation(id, citation, conn):
	cur = conn.cursor()
	query = "update entries set cite="+str(citation)+" where id="+str(id)
	cur.execute(query)
	conn.commit()

if __name__ == "__main__":
	db_filename = './db/information.db'
	paper_data = scrape_author("https://scholar.google.com/citations?user=DDLTYpAAAAAJ&hl=en")
	#citation = scrape_paper(paper[1])
	conn = sqlite3.connect(db_filename)
	cursor = conn.cursor()
	cursor.execute("""
		select id, title, cite from entries
		""")
	data = {}
	for row in cursor.fetchall():
		id_, title, cite = row
		data[title] = [cite, id_]
	#print data


	for paper in paper_data:
		for database_item in data:
			if difflib.SequenceMatcher(None, database_item, paper[0]).ratio() > 0.8:
				citation = scrape_paper(paper[1])
				if int(data[database_item][0]) != int(citation):
					update_citation(data[database_item][1], citation, conn)
				else:
					#print paper[0], data[database_item][0], citation
					pass


