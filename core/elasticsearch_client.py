from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

def log_event(index, data):
    es.index(index=index, document=data)
