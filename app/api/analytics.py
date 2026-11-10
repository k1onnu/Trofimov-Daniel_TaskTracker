import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task, TaskPriority, TaskStatus

router = APIRouter(prefix="/analytics", tags=["analytics"])

STATUS_ORDER = [status.value for status in TaskStatus]
PRIORITY_ORDER = [priority.value for priority in TaskPriority]

STATUS_COLORS = {
    "new": "#4C72B0",          # blue
    "in_progress": "#DD8452",  # orange
    "done": "#55A868",         # green
    "cancelled": "#C44E52",    # red
}

PRIORITY_COLORS = {
    "low": "#55A868",          # green
    "medium": "#DD8452",       # orange
    "high": "#C44E52",         # red
}


def _load_tasks_df(db: Session) -> pd.DataFrame:
    stmt = select(
        Task.id,
        Task.title,
        Task.status,
        Task.priority,
        Task.assignee_id,
        Task.created_at,
    )
    rows = db.execute(stmt).all()
    df = pd.DataFrame(
        rows,
        columns=["id", "title", "status", "priority", "assignee_id", "created_at"],
    )
    if not df.empty:
        df["status"] = df["status"].map(lambda v: v.value if hasattr(v, "value") else v)
        df["priority"] = df["priority"].map(lambda v: v.value if hasattr(v, "value") else v)
    return df


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    df = _load_tasks_df(db)
    if df.empty:
        return {
            "total": 0,
            "by_status": {},
            "by_priority": {},
            "by_assignee": {},
        }
    return {
        "total": int(len(df)),
        "by_status": df["status"].value_counts().to_dict(),
        "by_priority": df["priority"].value_counts().to_dict(),
        "by_assignee": {
            (str(int(k)) if pd.notna(k) else "unassigned"): int(v)
            for k, v in df["assignee_id"].value_counts(dropna=False).items()
        },
    }


@router.get("/chart")
def analytics_chart(db: Session = Depends(get_db)):
    df = _load_tasks_df(db)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    if df.empty:
        for ax in axes:
            ax.text(0.5, 0.5, "No tasks yet", ha="center", va="center")
            ax.set_axis_off()
    else:
        status_counts = df["status"].value_counts().reindex(STATUS_ORDER).dropna()
        status_colors = [STATUS_COLORS.get(s, "#4C72B0") for s in status_counts.index]
        status_counts.plot(
            kind="bar", ax=axes[0], color=status_colors, title="Tasks by status"
        )

        priority_counts = df["priority"].value_counts().reindex(PRIORITY_ORDER).dropna()
        priority_colors = [
            PRIORITY_COLORS.get(p, "#DD8452") for p in priority_counts.index
        ]
        priority_counts.plot(
            kind="bar", ax=axes[1], color=priority_colors, title="Tasks by priority"
        )

        for ax, counts in ((axes[0], status_counts), (axes[1], priority_counts)):
            ax.set_xlabel("")
            ax.set_ylabel("Count")
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            ax.set_axisbelow(True)

            max_len = max((len(str(s)) for s in counts.index), default=0)
            if max_len > 8:
                ax.tick_params(axis="x", rotation=45)
                for label in ax.get_xticklabels():
                    label.set_ha("right")
            else:
                ax.tick_params(axis="x", rotation=0)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")