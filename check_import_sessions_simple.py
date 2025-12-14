#!/usr/bin/env python3
import firebase_admin
from firebase_admin import firestore

firebase_admin.initialize_app(options={'projectId':'sanction-defender-firebase'})
db = firestore.client()

docs = list(db.collection('import_sessions').stream())
print('count:', len(docs))
for d in docs:
    data = d.to_dict()
    print(f"{d.id}: status={data.get('status')} end={data.get('timestamp_end')} changes={data.get('total_changes')}")
