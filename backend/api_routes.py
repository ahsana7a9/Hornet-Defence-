@router.get("/logs")
def get_logs():
    from core.elasticsearch_client import es

    res = es.search(index="threats", query={"match_all": {}})
    return res["hits"]["hits"]
