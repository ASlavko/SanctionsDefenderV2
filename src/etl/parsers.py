from typing import List, Dict, Generator
import xml.etree.ElementTree as ET
import json

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

class BaseParser:
    def parse(self, file_path: str) -> Generator[Dict, None, None]:
        raise NotImplementedError

class EUParser(BaseParser):
    def parse(self, file_path: str) -> Generator[Dict, None, None]:
        ctx = ET.iterparse(file_path, events=('start', 'end'))
        _, root = next(ctx)
        
        for event, elem in ctx:
            if event == 'end' and local_name(elem.tag) == 'sanctionEntity':
                try:
                    rec = {}
                    
                    # ID
                    unique_id = elem.attrib.get('euReferenceNumber') or elem.attrib.get('euReferencenumber')
                    logical_id = elem.attrib.get('logicalId')
                    if unique_id:
                        rec['id'] = f"EU_{unique_id}"
                    else:
                        rec['id'] = f"EU_{logical_id or 'unknown'}"

                    # Names
                    aliases = []
                    main_name = None
                    for ch in elem:
                        if local_name(ch.tag) == 'nameAlias':
                            whole = ch.attrib.get('wholeName') or (ch.attrib.get('firstName','') + ' ' + ch.attrib.get('lastName','')).strip()
                            if whole:
                                aliases.append(whole)
                                if (ch.attrib.get('strong','false').lower() == 'true' or main_name is None):
                                    main_name = whole
                    
                    rec['original_name'] = main_name
                    rec['alias_names'] = json.dumps(aliases) # Store as JSON string for DB Text column

                    # Program
                    programme = None
                    for ch in elem:
                        if local_name(ch.tag) == 'regulation':
                            programme = ch.attrib.get('programme') or ch.attrib.get('program')
                            break
                    rec['program'] = programme

                    # Nationality / Country
                    country = None
                    dob = None
                    for ch in elem:
                        lname = local_name(ch.tag)
                        if lname == 'citizenship':
                            country = ch.attrib.get('countryIso2Code') or ch.attrib.get('countryDescription')
                            if country:
                                break
                    rec['nationality'] = country

                    # Birth Date
                    for ch in elem:
                        lname = local_name(ch.tag)
                        if lname == 'birthdate':
                            dob = ch.attrib.get('birthdate') or ch.attrib.get('year')
                            if dob:
                                break
                    rec['birth_date'] = dob

                    # Entity Type
                    # Look for child element <subjectType>
                    st_code = None
                    for ch in elem:
                        if local_name(ch.tag) == 'subjectType':
                            st_code = ch.attrib.get('classificationCode') or ch.attrib.get('code')
                            break
                    
                    if st_code:
                        st_code = st_code.upper().strip()
                        if st_code == 'P':
                            rec['entity_type'] = 'Individual'
                        elif st_code == 'E':
                            rec['entity_type'] = 'Entity'
                        else:
                            rec['entity_type'] = st_code.capitalize()
                    else:
                        rec['entity_type'] = 'Unknown'

                    # Gender & URL & Others
                    rec['gender'] = None
                    rec['url'] = None
                    rec['un_id'] = elem.attrib.get('unitedNationId')
                    rec['remark'] = None
                    rec['function'] = None
                    
                    # Remark
                    for ch in elem:
                        if local_name(ch.tag) == 'remark':
                            rec['remark'] = (ch.text or '').strip()
                            break

                    # Gender & Function from nameAlias
                    for ch in elem:
                        if local_name(ch.tag) == 'nameAlias':
                            g = ch.attrib.get('gender')
                            if g and not rec['gender']:
                                rec['gender'] = g
                            
                            f = ch.attrib.get('function')
                            if f and not rec['function']:
                                rec['function'] = f
                    
                    # URL is in regulation -> publicationUrl (text)
                    for ch in elem:
                        if local_name(ch.tag) == 'regulation':
                            u = text_of(ch, 'publicationUrl')
                            if u:
                                rec['url'] = u
                                break

                    yield rec

                except Exception as e:
                    print(f"Error parsing EU record: {e}")
                finally:
                    elem.clear()
                    # Clear parents to save memory
                    while elem.getprevious() is not None if hasattr(elem, 'getprevious') else False:
                        try:
                            prev = elem.getprevious()
                            prev.clear()
                        except Exception:
                            break

class UKParser(BaseParser):
    def parse(self, file_path: str) -> Generator[Dict, None, None]:
        ctx = ET.iterparse(file_path, events=('start', 'end'))
        _, root = next(ctx)

        for event, elem in ctx:
            if event == 'end' and local_name(elem.tag).lower() == 'designation':
                try:
                    rec = {}
                    
                    # ID
                    unique_id = text_of(elem, 'UniqueID') or text_of(elem, 'UniqueId')
                    if not unique_id:
                        continue
                    rec['id'] = f"UK_{unique_id}"

                    # Names
                    main_name = None
                    aliases = []
                    names_parent = None
                    for ch in elem:
                        if local_name(ch.tag).lower() == 'names':
                            names_parent = ch
                            break
                    
                    if names_parent is not None:
                        for name_node in names_parent:
                            name_type = None
                            parts = {}
                            for nf in name_node:
                                ln = local_name(nf.tag).lower()
                                if ln == 'nametype':
                                    name_type = (nf.text or '').strip()
                                else:
                                    parts[ln] = (nf.text or '').strip()
                            
                            full = parts.get('name6') or ' '.join([parts.get(f'name{i}', '') for i in range(1,7)]).strip()
                            if full:
                                aliases.append(full)
                                if (name_type and name_type.lower() == 'primary') or main_name is None:
                                    main_name = full
                    
                    rec['original_name'] = main_name
                    
                    # Dedupe aliases
                    seen = set()
                    deduped = []
                    for a in aliases:
                        if a and a not in seen:
                            deduped.append(a)
                            seen.add(a)
                    rec['alias_names'] = json.dumps(deduped)

                    # Program
                    rec['program'] = text_of(elem, 'RegimeName')

                    # Country
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
                    rec['nationality'] = country

                    # DOB
                    dob = text_of(elem, 'DateOfBirth') or text_of(elem, 'DOB')
                    if not dob:
                        for sub in elem.iter():
                            if local_name(sub.tag).lower() in ('dateofbirth', 'dateofbirthitem') and (sub.text or '').strip():
                                dob = (sub.text or '').strip()
                                break
                    rec['birth_date'] = dob

                    # Entity Type
                    raw_type = text_of(elem, 'IndividualEntityShip')
                    if raw_type:
                        raw_type = raw_type.strip()
                        if raw_type.lower() == 'ship':
                            rec['entity_type'] = 'Vessel'
                        elif raw_type.lower() == 'person':
                            rec['entity_type'] = 'Individual'
                        elif raw_type.lower() == 'enterprise':
                            rec['entity_type'] = 'Entity'
                        else:
                            rec['entity_type'] = raw_type
                    else:
                        rec['entity_type'] = 'Unknown'

                    # Gender
                    rec['gender'] = None
                    for ch in elem:
                        if local_name(ch.tag).lower() == 'individualdetails':
                            for d in ch:
                                if local_name(d.tag).lower() == 'gender':
                                    rec['gender'] = (d.text or '').strip()
                                    break
                    
                    # URL (Not standard in UK XML, usually constructed or missing)
                    rec['url'] = None
                    
                    # UN ID
                    rec['un_id'] = text_of(elem, 'UNReferenceNumber')
                    
                    # Remark
                    rec['remark'] = text_of(elem, 'OtherInformation')
                    
                    # Function (Titles)
                    titles = []
                    for ch in elem:
                        if local_name(ch.tag).lower() == 'titles':
                            for t in ch:
                                if local_name(t.tag).lower() == 'title':
                                    val = (t.text or '').strip()
                                    if val:
                                        titles.append(val)
                    rec['function'] = ", ".join(titles) if titles else None

                    yield rec

                except Exception as e:
                    print(f"Error parsing UK record: {e}")
                finally:
                    elem.clear()

class USParser(BaseParser):
    def parse(self, file_path: str) -> Generator[Dict, None, None]:
        ctx = ET.iterparse(file_path, events=('start', 'end'))
        _, root = next(ctx)

        for event, elem in ctx:
            if event == 'end' and local_name(elem.tag) == 'sdnEntry':
                try:
                    rec = {}
                    
                    # ID
                    uid = text_of(elem, 'uid') or text_of(elem, 'id')
                    if not uid:
                        continue
                    rec['id'] = f"US_{uid}"

                    # Name
                    main_name = text_of(elem, 'lastName') or text_of(elem, 'name')
                    rec['original_name'] = main_name

                    # Aliases
                    aliases = []
                    for ch in elem:
                        if local_name(ch.tag) == 'akaList' or local_name(ch.tag) == 'aka':
                            for aka in ch:
                                if local_name(aka.tag) == 'aka' or local_name(aka.tag) == 'alias':
                                    a_name = text_of(aka, 'lastName') or text_of(aka, 'name')
                                    if a_name:
                                        aliases.append(a_name)
                                else:
                                    a_name = text_of(ch, 'lastName')
                                    if a_name:
                                        aliases.append(a_name)
                    rec['alias_names'] = json.dumps(aliases)

                    # Programs
                    programs = []
                    for ch in elem:
                        if local_name(ch.tag) == 'programList' or local_name(ch.tag) == 'programs':
                            for p in ch:
                                if local_name(p.tag) == 'program':
                                    if (p.text or '').strip():
                                        programs.append((p.text or '').strip())
                    rec['program'] = ", ".join(programs) if programs else None

                    # Country
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
                    rec['nationality'] = country

                    # DOB
                    dob = None
                    # Try idList for gender/dob
                    for ch in elem:
                        if local_name(ch.tag) == 'idList' or local_name(ch.tag) == 'idlist':
                            for idn in ch:
                                itype = text_of(idn, 'idType')
                                inum = text_of(idn, 'idNumber')
                                if itype and ('date' in itype.lower() or 'birth' in itype.lower()):
                                    if inum:
                                        dob = inum
                    
                    if not dob:
                        for ch in elem:
                            if local_name(ch.tag) == 'dateOfBirthList' or local_name(ch.tag) == 'dateofbirthlist':
                                for item in ch:
                                    if local_name(item.tag) == 'dateOfBirthItem' or local_name(item.tag) == 'dateofbirthitem':
                                        db = text_of(item, 'dateOfBirth')
                                        if db:
                                            dob = db
                                            break
                    rec['birth_date'] = dob

                    # Entity Type
                    raw_type = text_of(elem, 'sdnType')
                    if raw_type:
                        raw_type = raw_type.strip()
                        if raw_type.lower() == 'ship':
                            rec['entity_type'] = 'Vessel'
                        else:
                            rec['entity_type'] = raw_type
                    else:
                        rec['entity_type'] = 'Unknown'

                    # Gender
                    rec['gender'] = None
                    # Check idList for Gender
                    for ch in elem:
                        if local_name(ch.tag).lower() == 'idlist':
                            for idn in ch:
                                itype = text_of(idn, 'idType')
                                if itype and 'gender' in itype.lower():
                                    rec['gender'] = text_of(idn, 'idNumber')
                                    break
                    
                    # URL (Not in XML)
                    rec['url'] = None
                    
                    # UN ID (Not in US XML usually)
                    rec['un_id'] = None
                    
                    # Remark
                    rec['remark'] = text_of(elem, 'remarks')
                    
                    # Function (Title)
                    rec['function'] = text_of(elem, 'title')

                    yield rec

                except Exception as e:
                    print(f"Error parsing US record: {e}")
                finally:
                    elem.clear()
