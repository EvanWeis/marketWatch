import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "feed.xml")
FEED_NS = "http://www.w3.org/2005/Atom"
FEED_ID = "urn:market-stress-monitor:feed"
FEED_TITLE = "Market Stress Monitor"
FEED_LINK = "https://raw.githubusercontent.com/{user}/{repo}/main/feed.xml"


def _entry_id(run_date: str) -> str:
    return f"urn:market-stress-monitor:entry:{run_date}"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_existing(path: str) -> ET.Element:
    ET.register_namespace("", FEED_NS)
    if not os.path.exists(path):
        feed = ET.Element(f"{{{FEED_NS}}}feed")
        ET.SubElement(feed, f"{{{FEED_NS}}}id").text = FEED_ID
        ET.SubElement(feed, f"{{{FEED_NS}}}title").text = FEED_TITLE
        ET.SubElement(feed, f"{{{FEED_NS}}}updated").text = _now_utc()
        return feed
    tree = ET.parse(path)
    return tree.getroot()


def _trim_entries(feed: ET.Element, max_entries: int) -> None:
    entries = feed.findall(f"{{{FEED_NS}}}entry")
    for entry in entries[max_entries:]:
        feed.remove(entry)


def write(scored: dict, run_date: str, body: str, max_entries: int) -> None:
    feed_path = os.path.abspath(FEED_PATH)
    feed = _load_existing(feed_path)

    now = _now_utc()

    entry = ET.Element(f"{{{FEED_NS}}}entry")
    ET.SubElement(entry, f"{{{FEED_NS}}}id").text = _entry_id(run_date)
    ET.SubElement(entry, f"{{{FEED_NS}}}title").text = (
        f"Score {scored['score']}/4 — {scored['status']} — {run_date}"
    )
    ET.SubElement(entry, f"{{{FEED_NS}}}updated").text = now
    content = ET.SubElement(entry, f"{{{FEED_NS}}}content")
    content.set("type", "text")
    content.text = body

    # Insert new entry at position 0 (most recent first), after non-entry elements
    entries = feed.findall(f"{{{FEED_NS}}}entry")
    if entries:
        insert_pos = list(feed).index(entries[0])
    else:
        insert_pos = len(list(feed))
    feed.insert(insert_pos, entry)

    updated_el = feed.find(f"{{{FEED_NS}}}updated")
    if updated_el is not None:
        updated_el.text = now

    _trim_entries(feed, max_entries)

    ET.register_namespace("", FEED_NS)
    tree = ET.ElementTree(feed)
    ET.indent(tree, space="  ")
    tree.write(feed_path, encoding="unicode", xml_declaration=True)
