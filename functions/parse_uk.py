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
        if local_name(ch.tag).lower() == child_name.lower():
            return (ch.text or '').strip()
    return None


def first_text_in(elem, names):
    for name in names:
        val = text_of(elem, name)
        if val:
            return val
    return None


def parse_uk_to_jsonl(xml_path, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ctx = ET.iterparse(xml_path, events=('start', 'end'))
    _, root = next(ctx)

    # top-level DateGenerated
    file_date = None
    for ch in root:
        if local_name(ch.tag).lower() == 'dategenerated':
            file_date = (ch.text or '').strip()
            break

    with open(out_path, 'w', encoding='utf-8') as out_f:
        for event, elem in ctx:
            if event == 'end' and local_name(elem.tag).lower() == 'designation':
                try:
                    rec = {}
                    rec['sanction_source'] = 'UK'

                    unique_id = text_of(elem, 'UniqueID') or text_of(elem, 'UniqueId')
                    rec['unique_sanction_id'] = unique_id
                    rec['id'] = f"UK_{unique_id}" if unique_id else None

                    # entity type
                    ent = text_of(elem, 'IndividualEntityShip') or text_of(elem, 'IndividualEntity')
                    if ent:
                        rec['entity_type'] = 'company' if ent.strip().lower().startswith('entity') else 'individual'
                    else:
                        rec['entity_type'] = 'company'

                    # Names: prefer Name with NameType == Primary, extract Name6 if present
                    main_name = None
                    aliases = []
                    names_parent = None
                    for ch in elem:
                        if local_name(ch.tag).lower() == 'names':
                            names_parent = ch
                            break
                    if names_parent is not None:
                        for name_node in names_parent:
                            # For each <Name>
                            name_type = None
                            parts = {}
                            for nf in name_node:
                                ln = local_name(nf.tag).lower()
                                if ln == 'nametype':
                                    name_type = (nf.text or '').strip()
                                else:
                                    parts[ln] = (nf.text or '').strip()
                            # prefer Name6 for full-name (UK often stores full string in Name6)
                            full = parts.get('name6') or ' '.join([parts.get(f'name{i}', '') for i in range(1,7)]).strip()
                            if full:
                                aliases.append(full)
                                if (name_type and name_type.lower() == 'primary') or main_name is None:
                                    main_name = full

                    rec['main_name'] = main_name
                    # dedupe aliases, keep order
                    seen = set()
                    deduped = []
                    for a in aliases:
                        if a and a not in seen:
                            deduped.append(a)
                            seen.add(a)
                    rec['aliases'] = deduped

                    # UK program / regime
                    rec['details'] = {}
                    regime = text_of(elem, 'RegimeName')
                    if regime:
                        rec['details']['program'] = regime
                    # UK statement of reasons
                    reason = text_of(elem, 'UKStatementofReasons') or text_of(elem, 'UKStatementOfReasons')
                    if reason:
                        rec['details']['remark'] = reason
                    # file generation date
                    if file_date:
                        rec['details']['publish_date'] = file_date

                    # country: first Address/AddressCountry
                    country = None
                    for ch in elem:
                        if local_name(ch.tag).lower() == 'addresses':
                            for addr in ch:
                                c = text_of(addr, 'AddressCountry')
                                if c:
                                    country = c
                                    break
                            if country:
                                break
                    rec['country'] = country

                    # gender: find <Gender> element anywhere under designation
                    gender = None
                    for sub in elem.iter():
                        if local_name(sub.tag).lower() == 'gender' and (sub.text or '').strip():
                            gender = (sub.text or '').strip()
                            break
                    rec['gender'] = gender

                    # date of birth: look for <DateOfBirth> or <DateDesignated> (unlikely) or children under Name like DateOfBirth
                    dob = None
                    # try direct DateOfBirth
                    dob = text_of(elem, 'DateOfBirth') or text_of(elem, 'DOB')
                    if not dob:
                        # search deeper
                        for sub in elem.iter():
                            if local_name(sub.tag).lower() in ('dateofbirth', 'dateofbirthitem') and (sub.text or '').strip():
                                dob = (sub.text or '').strip()
                                break
                    rec['date_of_birth'] = dob

                    out_f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                except Exception as e:
                    out_f.write(json.dumps({'error': str(e)}) + '\n')
                finally:
                    elem.clear()
    return out_path


if __name__ == '__main__':
    import sys
    xml = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data', 'sanctions', 'UK.xml')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'data', 'parsed', 'UK.jsonl')
    print('Parsing', xml, '->', out)
    parse_uk_to_jsonl(xml, out)
    print('Done')
