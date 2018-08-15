import os
import sqlite3
import difflib
from scholar import ClusterScholarQuery, ScholarQuerier, ScholarSettings, txt, SearchScholarQuery
from time import sleep
import random
def sleeping(t=10):
    sleep(t)

ERROR = object()

def sanitize_characters(string, replace_invalid_with=ERROR):
    try:
        string.encode("utf-8")
        if "\0" in string:
            raise UnicodeEncodeError
        yield string
    except UnicodeEncodeError:
        for character in string:
            point = ord(character)
            
            if point == 0:
                if replace_invalid_with is ERROR:
                    raise ValueError("SQLite identifier contains NUL character.")
                else:
                    yield replace_invalid_with
            elif 0xD800 <= point <= 0xDBFF:
                if replace_invalid_with is ERROR:
                    raise ValueError("SQLite identifier contains high-surrogate character.")
                else:
                    yield replace_invalid_with
            elif 0xDC00 <= point <= 0xDFFF:
                if replace_invalid_with is ERROR:
                    raise ValueError("SQLite identifier contains low-surrogate character.")
                else:
                    yield replace_invalid_with
            # elif (0xE000 <= point <= 0xF8FF or
            #       0xF0000 <= point <= 0xFFFFD or
            #       0x100000 <= point <= 0x10FFFD):
            #     if replace_invalid_with is ERROR:
            #         raise ValueError("SQLite identifier contains private user character.")
            #     else:
            #         yield replace_invalid_with
            # elif 0xFDD0 <= point <= 0xFDEF or (point % 0x10000) in (0xFFFE, 0xFFFF):
            #     if replace_invalid_with is ERROR:
            #         raise ValueError("SQLite identifier contains non-character character.")
            #     else:
            #         yield replace_invalid_with
            else:
                yield character

def quote_identifier(identifier, replace_invalid_with=ERROR):
    sanitized = "".join(sanitize_characters(identifier, replace_invalid_with))
    return "\"" + sanitized.replace("\"", "\"\"") + "\""


def update_citation(id, citation, conn):
    cur = conn.cursor()
    query = "update entries set cite="+str(citation)+" where id="+str(id)
    cur.execute(query)
    conn.commit()

def update_url_citation(id, url_citation, conn):
    cur = conn.cursor()
    url_citation = quote_identifier(url_citation)
    query = "update entries set urlcite="+str(url_citation)+" where id="+str(id)
    cur.execute(query)
    conn.commit()

def update_clusterID(id, cluster_ID, conn):
    cur = conn.cursor()
    query = "update entries set cluster=\""+cluster_ID+"\" where id="+str(id)
    print query
    cur.execute(query)
    conn.commit()

def getResult(query):
    querier = ScholarQuerier()
    citations = 0
    url_citations = ""
    clusterID = ""
    try:
        querier.send_query(query)
        print querier.articles[0].attrs['cluster_id']
        citations = querier.articles[0].attrs['num_citations'][0]
        url_citations = querier.articles[0].attrs['url_citations'][0]
        clusterID = querier.articles[0].attrs['cluster_id'][0]
    except:
        pass
    return citations, url_citations, clusterID

def setCitationByID(cluster_ID):
    query = ClusterScholarQuery(cluster=cluster_ID)
    query.set_num_page_results(1)
    #querier.send_query(query)
    #citations = querier.articles[0].attrs['num_citations'][0]
    return query

def setCitationByTitle(paper_title):
    query = SearchScholarQuery()
    query.set_author("Si Chen")
    query.set_phrase(paper_title)
    query.set_num_page_results(1)
    #querier.send_query(query)
    #citations = 0
    return query

if __name__ == "__main__":
    #db_filename = '/var/www/Dodrio/db/information.db'
    db_filename = './db/information.db'
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("""
    	select id, title, cite, cluster from entries
    	""")
    data = {}
    for row in cursor.fetchall():
    	id_, title, cite, cluster = row
    	data[title] = [cite, id_, cluster]
    #txt(querier, True)
    random_id = random.randint(0, len(data))
    print "TRY:{}".format(random_id)
    i = 0
    random_id = 9
    for database_item in data:
        if i != random_id:
            pass
        else:
            print database_item
            cluster_ID = data[database_item][2]
            citation = 0
            if cluster_ID == None:
                # query cluster ID
                query = setCitationByTitle(database_item)
                citation, url_citation, cluster_ID = getResult(query)
                print citation, url_citation, str(cluster_ID)
                sleeping()                    
                if cluster_ID != "" and cluster_ID != None:
                    update_clusterID(data[database_item][1], cluster_ID, conn)
                else:
                    pass
            else:
                query = setCitationByID(int(cluster_ID))
                citation, url_citation, cluster_ID = getResult(query)
                print citation, url_citation, cluster_ID
                sleeping()
            if url_citation != None:
                update_url_citation(data[database_item][1], url_citation, conn)
            old_citation = data[database_item][0] 
            if old_citation < citation:
                print "Citiation Change! From {} to {}".format(old_citation, citation)
                update_citation(data[database_item][1], citation, conn)
            else:
                pass
        i += 1

    #     citation = getCitationByTitle(paper[1])
    #     print citation
    #     if int(data[database_item][0]) < int(citation):
    #         update_citation(data[database_item][1], citation, conn)
    #     else:
    #         #print paper[0], data[database_item][0], citation
    #         pass


