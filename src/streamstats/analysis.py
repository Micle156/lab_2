def update_stat(event, stats):
    """обновление статистики для новой строки"""

    stats["total"] += 1
    stats["st_level"][event["level"]] += 1

    if event["source"] in stats["st_source"]:
        stats["st_source"][event["source"]]["total"] += 1
        if event["level"] in ("ERROR", "CRITICAL"):
            stats["st_source"][event["source"]]["error"] += 1
    else:
        if event["level"] in ("ERROR", "CRITICAL"):
            stats["st_source"][event["source"]] = {
                "total": 1,
                "error": 1
            }
        else:
            stats["st_source"][event["source"]] = {
                "total": 1,
                "error": 0
            }

    time_in_event = event["timestamp"]
    if stats["first_timestamp"] is None \
            or stats["first_timestamp"] > time_in_event:
        stats["first_timestamp"] = time_in_event

    if stats["last_timestamp"] is None \
            or stats["last_timestamp"] < time_in_event:
        stats["last_timestamp"] = time_in_event
    return stats

    
def top(stats):
    """
    вычисление топ-5 ресурсов с уровнем ERROR и CRITICAL,
    их вывод в порядке возрастания и по алфавиту
    """

    err = [(source_key, source_item["error"]) 
           for source_key, source_item
           in stats["st_source"].items()
           if source_item["error"] > 0]

    return sorted(err, key=lambda k: (k[1], k[0]))[:5]