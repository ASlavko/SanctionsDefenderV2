import os
import json
import xml.etree.ElementTree as ET


def local_name(tag):
    if tag is None:
        return ''
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def parse_eu_to_jsonl(xml_path, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ctx = ET.iterparse(xml_path, events=('start', 'end'))
    _, root = next(ctx)
    generation_date = root.attrib.get('generationDate') or root.attrib.get('generationdate')

    with open(out_path, 'w', encoding='utf-8') as out_f:
        for event, elem in ctx:
            if event == 'end' and local_name(elem.tag) == 'sanctionEntity':
                try:
                    rec = {}
                    rec['sanction_source'] = 'EU'
                    rec['id'] = None
                    rec['unique_sanction_id'] = elem.attrib.get('euReferenceNumber') or elem.attrib.get('euReferencenumber')
                    rec['unitedNationId'] = elem.attrib.get('unitedNationId') or elem.attrib.get('unitednationid')
                    rec['logicalId'] = elem.attrib.get('logicalId')
                    rec['last_updated_on_source'] = generation_date

                    # subjectType
                    subject_type = None
                    for ch in elem:
                        if local_name(ch.tag) == 'subjectType':
                            subject_type = ch.attrib.get('code') or ch.attrib.get('Code')
                            break
                    rec['entity_type'] = 'individual' if (subject_type and subject_type.lower().startswith('person')) else 'company'

                    # names / aliases
                    aliases = []
                    main_name = None
                    for ch in elem:
                        if local_name(ch.tag) == 'nameAlias':
                            whole = ch.attrib.get('wholeName') or (ch.attrib.get('firstName','') + ' ' + ch.attrib.get('lastName','')).strip()
                            if whole:
                                aliases.append(whole)
                                if (ch.attrib.get('strong','false').lower() == 'true' or main_name is None):
                                    main_name = whole
                            # gender attribute on nameAlias
                            if 'gender' in ch.attrib and ch.attrib.get('gender'):
                                # prefer gender from strong nameAlias
                                rec['gender'] = ch.attrib.get('gender')
                    rec['main_name'] = main_name
                    rec['aliases'] = aliases

                    # regulation/program/url
                    programme = None
                    puburl = None
                    for ch in elem:
                        if local_name(ch.tag) == 'regulation':
                            programme = ch.attrib.get('programme') or ch.attrib.get('program')
                            for g in ch:
                                if local_name(g.tag) == 'publicationUrl':
                                    puburl = (g.text or '').strip()
                                    break
                            break

                    # remark
                    remark = None
                    for ch in elem:
                        if local_name(ch.tag) == 'remark':
                            remark = (ch.text or '').strip()
                            break

                    # country, birthdate
                    country = None
                    dob = None
                    # look for citizenship or birthdate children
                    for ch in elem:
                        lname = local_name(ch.tag)
                        if lname == 'citizenship':
                            country = ch.attrib.get('countryIso2Code') or ch.attrib.get('countryDescription')
                            if country:
                                break
                        if lname == 'birthdate':
                            # EU birthdate element has attribute 'birthdate' or year/month/day
                            dob = ch.attrib.get('birthdate') or ch.attrib.get('year')
                            # if we get a year only, keep it
                            if dob:
                                # continue searching for country too
                                pass

                    rec['details'] = {'program': programme, 'url': puburl}
                    if remark:
                        rec['details']['remark'] = remark

                    rec['country'] = country
                    rec['date_of_birth'] = dob
                    # rec['gender'] may have been set from nameAlias above; default to None
                    if 'gender' not in rec:
                        rec['gender'] = None

                    # id composition
                    if rec['unique_sanction_id']:
                        rec['id'] = f"EU_{rec['unique_sanction_id']}"
                    else:
                        rec['id'] = f"EU_{rec.get('logicalId') or 'unknown'}"

                    out_f.write(json.dumps(rec, ensure_ascii=False) + '\n')

                except Exception as e:
                    # best-effort: log error to file
                    out_f.write(json.dumps({'error': str(e)}) + '\n')
                finally:
                    elem.clear()
                    # also clear parents to free memory
                    while elem.getprevious() is not None if hasattr(elem, 'getprevious') else False:
                        try:
                            prev = elem.getprevious()
                            prev.clear()
                        except Exception:
                            break
    return out_path


if __name__ == '__main__':
    import sys
    xml = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data', 'sanctions', 'EU.xml')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'data', 'parsed', 'EU.jsonl')
    print('Parsing', xml, '->', out)
    parse_eu_to_jsonl(xml, out)
    print('Done')