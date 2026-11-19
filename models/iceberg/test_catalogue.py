"""The archive result parser must take USNIC CSV issues and nothing else.

    prenv/bin/python -m pytest models/iceberg/test_catalogue.py -q
"""

from catalogue import _archive_links

# Two rows in the shape USNIC served on 2026-11-19, plus two that must be ignored.
PAGE = """
<a href="/File/DownloadArchive?prd=13411132026" id="Antarctic_Icebergs_CSV">AntarcticIcebergs_20261113.csv</a>
<a href="/File/DownloadArchive?prd=13411062026" id="Antarctic_Icebergs_CSV">AntarcticIcebergs_20261106.csv</a>
<a href="/File/DownloadArchive?prd=1" id="x">../../etc/passwd</a>
<a href="https://example.com/evil" id="x">AntarcticIcebergs_20261030.csv</a>
"""


def test_archive_links_keeps_only_usnic_csv_issues():
    assert _archive_links(PAGE) == [
        ("AntarcticIcebergs_20261113.csv",
         "https://usicecenter.gov/File/DownloadArchive?prd=13411132026"),
        ("AntarcticIcebergs_20261106.csv",
         "https://usicecenter.gov/File/DownloadArchive?prd=13411062026"),
    ]
