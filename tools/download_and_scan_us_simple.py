"""
Download the simpler OFAC SDN/CONSOLIDATED XMLs and perform a small scan
(report root tag, namespace, and counts for core elements to compare
against the enhanced (complex) files).
"""
import os
import requests
import xml.etree.ElementTree as ET

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
OUT_DIR = os.path.join(BASE_DIR, 'data', 'sanctions')
os.makedirs(OUT_DIR, exist_ok=True)

URLS = {
    'US_SDN_SIMPLE': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.XML',
    'US_NON_SDN_SIMPLE': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONSOLIDATED.XML',
}

TARGETS = ['entity', 'name', 'identityId', 'entityType', 'sdnType', 'program', 'formattedFullName', 'formattedLastName', 'formattedFirstName', 'publicationInfo', 'dataAsOf']

def download(name, url):
    path = os.path.join(OUT_DIR, name + '.xml')
    print(f"Downloading {name} -> {path}")
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Saved {path}")
        return path
    except Exception as e:
        print(f"Failed to download {name}: {e}")
        return None


def local_name(tag):
    if tag is None:
        return ''
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def scan(path):
    print('\n' + '-'*60)
    print(f"Scanning {path}")
    try:
        it = ET.iterparse(path, events=('start',))
        event, root = next(it)
        print(f"Root tag: {root.tag} -> local: {local_name(root.tag)}")
        ns = set()
        counts = {t:0 for t in TARGETS}
        sample = {t:[] for t in TARGETS}
        for event, elem in it:
            ln = local_name(elem.tag).lower()
            if elem.tag.startswith('{'):
                ns.add(elem.tag.split('}')[0].lstrip('{'))
            for t in TARGETS:
                if t.lower() == ln:
                    counts[t] += 1
                    if len(sample[t]) < 3:
                        sample[t].append((ln, (elem.text or '').strip()[:120]))
            elem.clear()
        print(f"Detected namespaces (sample): {list(ns)[:4]}")
        print('Field counts (non-zero):')
        for t in TARGETS:
            if counts[t]:
                print(f" - {t}: {counts[t]}")
                for s in sample[t]:
                    print(f"    sample -> tag: {s[0]}, text_preview: {s[1]}")
    except Exception as e:
        print(f"Error scanning {path}: {e}")


if __name__ == '__main__':
    paths = []
    for name, url in URLS.items():
        p = download(name, url)
        if p:
            paths.append(p)
    for p in paths:
        scan(p)
