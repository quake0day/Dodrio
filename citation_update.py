import os
import sqlite3
import difflib
from scholar import ClusterScholarQuery, ScholarQuerier, ScholarSettings, txt, SearchScholarQuery
from time import sleep
import random
def update_citation(id, citation, conn):
    cur = conn.cursor()
    query = "update entries set cite="+str(citation)+" where id="+str(id)
    cur.execute(query)
    conn.commit()

def update_clusterID(id, cluster_ID, conn):
    cur = conn.cursor()
    query = "update entries set cluster="+cluster_ID+" where id="+str(id)
    cur.execute(query)
    conn.commit()

def getCitationByID(cluster_ID):
    querier = ScholarQuerier()
    query = ClusterScholarQuery(cluster=cluster_ID)
    query.set_num_page_results(1)
    querier.send_query(query)
    citations = querier.articles[0].attrs['num_citations'][0]
    return citations

def getCitationURLByID(cluster_ID):
    querier = ScholarQuerier()
    query = ClusterScholarQuery(cluster=cluster_ID)
    query.set_num_page_results(1)
    querier.send_query(query)
    url_citations = querier.articles[0].attrs['url_citations'][0]
    return url_citations

def getCitationByTitle(paper_title):
    querier = ScholarQuerier()
    query = SearchScholarQuery()
    query.set_author("Si Chen")
    query.set_phrase(paper_title)
    query.set_num_page_results(1)
    print query
    querier.send_query(query)
    citations = 0
    txt(querier, True)
    try:
        citations = querier.articles[0].attrs['num_citations'][0]
    except:
        pass
    #url_citations = querier.articles[0].attrs['url_citations'][0]
    return citations

def getClusterIDByTitle(paper_title):
    querier = ScholarQuerier()
    query = SearchScholarQuery()
    query.set_author("Si Chen")
    query.set_phrase(paper_title)
    query.set_num_page_results(1)
    querier.send_query(query)
    clusterID = None
    try:
        clusterID = querier.articles[0].attrs['cluster_id']
    except:
        pass
    #url_citations = querier.articles[0].attrs['url_citations'][0]
    return clusterID

def getCitationURLByTitle(paper_title):
    querier = ScholarQuerier()
    query = SearchScholarQuery()
    query.set_author("Si Chen")
    query.set_phrase(paper_title)
    query.set_num_page_results(1)
    querier.send_query(query)
    url_citations = querier.articles[0].attrs['url_citations'][0]
    return url_citations

if __name__ == "__main__":
    db_filename = '/var/www/Dodrio/db/information.db'
    #db_filename = './db/information.db'
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
    for database_item in data:
        if i != random_id:
            pass
        else:
            print database_item
            cluster_ID = data[database_item][2]
            citation = 0
            if cluster_ID == None:
                # query cluster ID
                cluster_ID = getClusterIDByTitle(database_item)
                sleep(1)
                if cluster_ID != None:
                    update_clusterID(data[database_item][1], cluster_ID, conn)
                sleep(1)
                citation = getCitationByTitle(database_item)
            else:
                citation = getCitationByID(int(cluster_ID))
                sleep(1)
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


