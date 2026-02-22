from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.db.models import DecisionAudit
import csv
import io
import pandas as pd

router = APIRouter()

@router.get("/audit/export/csv")
def export_audit_csv(db: Session = Depends(get_db)):
    audits = db.query(DecisionAudit).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "decision_id", "action", "old_value", "new_value", "user_id", "timestamp", "comment"])
    for a in audits:
        writer.writerow([
            a.id, a.decision_id, a.action, a.old_value, a.new_value, a.user_id, a.timestamp, a.comment
        ])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit_log.csv"})

@router.get("/audit/export/excel")
def export_audit_excel(db: Session = Depends(get_db)):
    audits = db.query(DecisionAudit).all()
    data = [
        {
            "id": a.id,
            "decision_id": a.decision_id,
            "action": a.action,
            "old_value": a.old_value,
            "new_value": a.new_value,
            "user_id": a.user_id,
            "timestamp": a.timestamp,
            "comment": a.comment
        }
        for a in audits
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=audit_log.xlsx"})
