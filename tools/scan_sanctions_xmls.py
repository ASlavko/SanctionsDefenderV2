"""
Scan sanctions XML files in data/sanctions/ and report element names, namespaces,
and counts/examples for fields mentioned in the plan.
"""
import os
import xml.etree.ElementTree as ET

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'sanctions')
FILES = ["EU.xml", "UK.xml", "US_SDN.xml", "US_NON_SDN.xml"]

# Candidate tags/fields we expect from the plan (namespace-agnostic)
TARGETS = [
    'fileGenerationDate', 'Entity', 'Entity_EU_ReferenceNumber', 'Entity_ReferenceNumber',
    'Entity_SubjectType', 'NameAlias_WholeName', 'Entity_UnitedNationId',
    'Entity_Regulation_PublicationUrl', 'NameAlias_Gender', 'Address_CountryIso2Code',
    'DateGenerated', 'UniqueID', 'Name1', 'Name2', 'Name3', 'Name4', 'Name5', 'Name6',
    'UKStatementofReasons', 'ns1:Publish_Date', 'Publish_Date', 'uid', 'sdnType', 'program',
    'dateOfBirth', 'lastName', 'firstName', 'lastName1', 'lastName2', 'firstName1', 'firstName2'
]

# normalize tag (strip namespace)
def local_name(tag):
    if tag is None:
        return ''
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def scan_file(path):
    print('\n' + '='*80)
    print(f"Scanning: {path}")
    try:
        # parse with iterparse to avoid building huge trees
        events = ("start",)
        it = ET.iterparse(path, events=events)
        # get root
        event, root = next(it)
        print(f"Root tag: {root.tag} -> local: {local_name(root.tag)}")
        # collect namespace hints from root.attrib
        # naive namespace extraction from tags
        ns = set()
        counts = {}
        examples = {}
        for t in TARGETS:
            counts[t] = 0
            examples[t] = []

        # We'll iterate through file and record local names
        # For performance, limit sample examples per tag
        SAMPLE_LIMIT = 3
        for event, elem in it:
            ln = local_name(elem.tag)
            # record namespace-like prefix if present
            if elem.tag.startswith('{'):
                ns_uri = elem.tag.split('}')[0].lstrip('{')
                ns.add(ns_uri)
            # count matches for lowercase comparisons
            low = ln.lower()
            for target in TARGETS:
                if target.lower() == low or target.lower().endswith(low) or low.endswith(target.lower()):
                    counts[target] += 1
                    if len(examples[target]) < SAMPLE_LIMIT:
                        text = (elem.text or '').strip()[:200]
                        parent = elem.getparent() if hasattr(elem, 'getparent') else None
                        examples[target].append({'path_tag': ln, 'text_preview': text})
            # clear element to save memory
            elem.clear()
        # Print summary
        print(f"Detected namespaces (sample): {list(ns)[:5]}")
        print('Field counts:')
        for t in TARGETS:
            if counts[t]:
                print(f" - {t}: {counts[t]} occurrences")
                for ex in examples[t]:
                    print(f"    sample -> tag: {ex['path_tag']}, text_preview: {ex['text_preview']}")
    except Exception as e:
        print(f"Error scanning {path}: {e}")


if __name__ == '__main__':
    for f in FILES:
        p = os.path.join(DATA_DIR, f)
        if os.path.exists(p):
            scan_file(p)
        else:
            print(f"File not found: {p}")
