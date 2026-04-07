import logging
import os

logger = logging.getLogger(__name__)

_es = None
_checked = False
_in_memory_logs = []

def get_es():
    global _es, _checked
    if _checked:
        return _es
    _checked = True

    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    try:
        from elasticsearch import Elasticsearch
        client = Elasticsearch(
            es_url,
            request_timeout=2,
            retry_on_timeout=False,
            max_retries=0,
        )
        if client.ping():
            _es = client
            logger.info("[Elasticsearch] Connected successfully")
        else:
            raise ConnectionError("Ping returned False")
    except Exception as e:
        logger.warning(f"[Elasticsearch] Not available ({e}) — using in-memory fallback")
        _es = None

    return _es

def log_event(index: str, data: dict):
    es = get_es()
    if es:
        try:
            es.index(index=index, document=data)
            return
        except Exception as e:
            logger.warning(f"[Elasticsearch] log_event failed: {e}")
    _in_memory_logs.append({"index": index, "data": data})
    if len(_in_memory_logs) > 500:
        _in_memory_logs.pop(0)

def search_events(index: str, size: int = 50) -> list:
    es = get_es()
    if es:
        try:
            res = es.search(index=index, query={"match_all": {}}, size=size)
            return [hit["_source"] for hit in res["hits"]["hits"]]
        except Exception as e:
            logger.warning(f"[Elasticsearch] search_events failed: {e}")
    return [entry["data"] for entry in _in_memory_logs if entry["index"] == index][-size:]
