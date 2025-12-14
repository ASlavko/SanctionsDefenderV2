import os
import json
import xml.etree.ElementTree as ET


def local_name(tag):
    if tag is None:
        return ''
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def text_of(parent, child_name):
    for ch in parent:
        if local_name(ch.tag) == child_name:
            return (ch.text or '').strip()
    return None


def parse_us_simple_to_jsonl(xml_path, out_path, source_name):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ctx = ET.iterparse(xml_path, events=('start', 'end'))
    _, root = next(ctx)
    # try to find publish date if present
    pub_date = None
    for ch in root:
        if local_name(ch.tag).lower().startswith('publ'):
            pub_date = text_of(ch, 'Publish_Date') or text_of(ch, 'dataAsOf')
            break

    with open(out_path, 'w', encoding='utf-8') as out_f:
        for event, elem in ctx:
            if event == 'end' and local_name(elem.tag) == 'sdnEntry':
                try:
                    uid = text_of(elem, 'uid') or text_of(elem, 'id')
                    sdn_type = text_of(elem, 'sdnType') or text_of(elem, 'sdnType'.lower())
                    main_name = text_of(elem, 'lastName') or text_of(elem, 'name')
                    # programs
                    programs = []
                    for ch in elem:
                        if local_name(ch.tag) == 'programList' or local_name(ch.tag) == 'programs':
                            for p in ch:
                                if local_name(p.tag) == 'program':
                                    if (p.text or '').strip():
                                        programs.append((p.text or '').strip())
                    # aliases
                    aliases = []
                    for ch in elem:
                        if local_name(ch.tag) == 'akaList' or local_name(ch.tag) == 'aka':
                            # find all aka entries inside
                            for aka in ch:
                                if local_name(aka.tag) == 'aka' or local_name(aka.tag) == 'alias':
                                    a_name = text_of(aka, 'lastName') or text_of(aka, 'name')
                                    if a_name:
                                        aliases.append(a_name)
                                else:
                                    # sometimes inner elements are immediate
                                    a_name = text_of(ch, 'lastName')
                                    if a_name:
                                        aliases.append(a_name)
                    # extract country from addressList if present
                    country = None
                    for ch in elem:
                        if local_name(ch.tag) == 'addressList' or local_name(ch.tag) == 'addresslist':
                            for a in ch:
                                if local_name(a.tag) == 'address':
                                    c = text_of(a, 'country')
                                    if c:
                                        country = c
                                        break
                            if country:
                                break

                    # extract gender from idList entries where idType contains 'gender'
                    gender = None
                    dob = None
                    for ch in elem:
                        if local_name(ch.tag) == 'idList' or local_name(ch.tag) == 'idlist':
                            for idn in ch:
                                itype = text_of(idn, 'idType')
                                inum = text_of(idn, 'idNumber')
                                if itype and 'gender' in itype.lower():
                                    gender = inum
                                if itype and ('date' in itype.lower() or 'birth' in itype.lower()):
                                    # idNumber may contain DOB
                                    if inum:
                                        dob = inum

                    # dateOfBirthList alternative
                    if not dob:
                        for ch in elem:
                            if local_name(ch.tag) == 'dateOfBirthList' or local_name(ch.tag) == 'dateofbirthlist':
                                for item in ch:
                                    if local_name(item.tag) == 'dateOfBirthItem' or local_name(item.tag) == 'dateofbirthitem':
                                        db = text_of(item, 'dateOfBirth')
                                        if db:
                                            dob = db
                                            break
                                    if dob:
                                        break
                                if dob:
                                    break

                    rec = {
                        'sanction_source': source_name,
                        'id': f"{source_name}_{uid}" if uid else None,
                        'unique_sanction_id': uid,
                        'entity_type': 'individual' if (sdn_type and sdn_type.lower().startswith('individual')) else 'company',
                        'main_name': main_name,
                        'aliases': aliases,
                        'country': country,
                        'gender': gender,
                        'date_of_birth': dob,
                        'details': {
                            'programs': programs,
                            'publish_date': pub_date
                        }
                    }
                    out_f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                except Exception as e:
                    out_f.write(json.dumps({'error': str(e)}) + '\n')
                finally:
                    elem.clear()
    return out_path


if __name__ == '__main__':
    import sys
    xml = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data', 'sanctions', 'US_SDN_SIMPLE.xml')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'data', 'parsed', 'US_SDN_SIMPLE.jsonl')
    print('Parsing', xml, '->', out)
    parse_us_simple_to_jsonl(xml, out, 'US_SDN_SIMPLE')
    print('Done')