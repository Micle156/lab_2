import json

from streamstats.__main__ import main

"""корректные тесты"""

def test_cli_1(tmp_path):
    src = tmp_path / "v.csv"

    src.write_text(
        "timestamp,level,source,message\n"
        "2003-07-04T10:11:12+00:00,INFO,src1,\n"
        "1999-12-12T11:11:50+00:00,ERROR,src2,MESSAGE\n",
        encoding="utf-8"
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "csv",
        "--output", str(out)
    ])

    assert code == 0

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total"] == 2

def test_cli_2(tmp_path):
    src = tmp_path / "v.csv"
    src.write_text(
        "timestamp,level,source,message\n",
        encoding="utf-8"
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "csv",
        "--output", str(out)
    ])

    assert code == 0

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total"] == 0

    assert report["last_timestamp"] is None
    assert report["first_timestamp"] is None

def test_cli_3(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.jsonl"

    a.write_text(
        "timestamp,level,source,message\n"
        "2003-07-04T10:11:12+00:00,INFO,src1,\n"
        "2020-01-01T00:00:10+00:00,ERROR,src2,MESSAGE\n",
        encoding="utf-8"
    )

    b.write_text(
        '{"timestamp":"2026-10-06T10:00:00+00:00",'
        '"level":"ERROR","source":"src1","message":"ok"}\n'
        '{"timestamp":"2026-10-06T10:01:00+00:00",'
        '"level":"ERROR","source":"src2","message":""}\n',
        encoding="utf-8",
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(a), str(b),
        "--format", "csv", "jsonl",
        "--output", str(out)
    ])

    assert code == 0

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total"] == 4
    assert report["top_error_sources"] == [["src1", 1], ["src2", 2]]

def test_cli_4(tmp_path, ):
    src = tmp_path / "v.csv"
    src.write_text(
        "timestamp,level,source,message\n",
        encoding="utf-8"
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "csv",
        "--output", str(out)
    ])

    assert code == 0

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total"] == 0

"""некорректные тесты"""

def test_cli_5(tmp_path, caplog):
    src = tmp_path / "v.csv"

    src.write_text(
        "timestamp,level,source,message\n"
        "2003-07-04T10:11:12+00:00,INFO,src1,\n"
        "not_date,ERROR,src2,MESSAGE\n",
        encoding="utf-8"
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "csv",
        "--output", str(out)
    ])
    assert code == 2

    assert "line 3" in caplog.text

def test_cli_6(tmp_path, caplog):
    src = tmp_path / "v.csv"

    src.write_text(
        "timestamp,level,source,message\n"
        "2003-07-04T10:11:12+00:00,INFO,src1,\n"
        "2003-07-04T10:11:13+00:00,ERROR,src2,MESSAGE\n"
        "2003-08-11T11:11:11+00:00,TRACE,src3,сообщение\n",
        encoding="utf-8"
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "csv",
        "--output", str(out)
    ])
    assert code == 2

    assert "line 4" in caplog.text

def test_cli_7(tmp_path, caplog):
    src = tmp_path / "v.csv"

    src.write_text(
        "timestamp,level,source,message\n"
        "2003-07-04T10:11:12+00:00,INFO,src1\n"
        "2003-07-04T10:11:13+00:00,ERROR,src2,MESSAGE\n"
        "2003-08-11T11:11:11+00:00,INFO,src3,сообщение\n",
        encoding="utf-8"
    )

    out = tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "csv",
        "--output", str(out)
    ])
    assert code == 2

    assert "line 2" in caplog.text

"""тесты со --skip_valid"""

def test_cli_8(tmp_path, capsys):
    src = tmp_path / "v.jsonl"
    src.write_text(
        '{"timestamp":"2026-11-06T10:00:00+00:00",'
        '"level":"уровень","source":"src1","message":"ok"}\n'
        '{"timestamp":"2026-10-07T10:00:00+00:00",'
        '"level":"ERROR","source":"src2","message":"ok"}\n'
        '{"timestamp":"2026-10-06T10:01:00+00:00",'
        '"level":"ERROR","source":"src3","message":""}\n',
        encoding="utf-8",
    )

    tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "jsonl",
        "--skip-invalid"
    ])

    assert code == 0

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert report["total"] == 2
    assert report["skipped"] == 1

def test_cli_9(tmp_path, capsys, caplog):
    src = tmp_path / "v.jsonl"
    src.write_text(
        '{"timestamp":"2026-11-06T10:00:00+",'
        '"level":"CRITICAL","source":"src1","message":"ok"}\n'
        '{"timestamp":"2026-10-07T10:00:00+00:00",'
        '"level":"ERROR","source":"src2","message":"ok"}\n'
        '{"timestamp":"2026-10-06T10:01:00+00:00",'
        '"level":"ERROR","source":"src3","message":""}\n',
        encoding="utf-8",
    )

    tmp_path / "r.json"

    code = main([
        "analyze",
        str(src),
        "--format", "jsonl",
        "--skip-invalid"
    ])

    assert code == 0

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert report["total"] == 2
    assert report["skipped"] == 1
    assert report["levels"]["ERROR"] == 2 
    assert "line 1" in caplog.text