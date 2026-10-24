import json

from .analysis import top


def build_report(stats, path, skip_invalid):
    """создается json-отчет, записывается в файл для отчета"""
    report = {
        "total": stats["total"],
        "levels": dict(stats["st_level"]), 
        # dict чтобы словари были в разных местах в памяти
        "sources": {
            src: inf["total"] 
            for src, inf in stats["st_source"].items()
        },
        "top_error_sources": top(stats),
        "first_timestamp": stats["first_timestamp"].isoformat()

        if stats["first_timestamp"] else None,
        "last_timestamp": stats["last_timestamp"].isoformat()
        if stats["last_timestamp"] else None,
        "skipped": stats["skip"],
    }

    if not skip_invalid: # проверка, куда выводить: в консоль или в файл
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))