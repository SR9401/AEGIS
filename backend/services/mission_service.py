from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import or_, asc, desc
from models.mission import Mission, Status
from models.user import User

def _parse_iso_datetime(date_val: Any) -> Optional[datetime]:
    """Parse une string ISO (accepte le suffixe 'Z') ou normalise un datetime.
    Retourne un datetime timezone-aware en UTC ou None si date_val is None.
    Lève ValueError si format invalide.
    """
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        # si naïf, considérer comme UTC pour le dev; sinon convertir en UTC
        if date_val.tzinfo is None:
            return date_val.replace(tzinfo=timezone.utc)
        return date_val.astimezone(timezone.utc)
    if isinstance(date_val, str):
        s = date_val.strip()
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            raise ValueError("invalid_date")
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    raise ValueError("invalid_date")

def _normalize_status(raw_status: Any) -> Status:
    """Normalise une valeur status (Status | str) en Status enum.
    Lève ValueError si invalide.
    """
    if raw_status is None:
        return Status.PLANNED
    if isinstance(raw_status, Status):
        return raw_status
    if isinstance(raw_status, str):
        s = raw_status.strip()
        name_up = s.upper()
        if name_up in Status.__members__:
            return Status[name_up]
        for member in Status:
            if member.value == s:
                return member
    raise ValueError("invalid_status")

def create_mission(session, payload: Dict[str, Any], created_by: str, *, verify_creator: bool = False) -> Mission:
    """
    Crée une mission et l'ajoute à la session (flush mais pas commit).
    - session: SQLAlchemy Session (ex: g.db)
    - payload: dict reçu (title, description, status, date, lat, lon...)
    - created_by: id de l'utilisateur créateur (string/uuid)
    - verify_creator: si True, vérifie que created_by existe en base (raise ValueError si absent)
    Retourne l'objet Mission (persisté dans la transaction courante).
    Lève ValueError pour validations (title manquant, date invalide, etc).
    """
    title = payload.get("title")
    if not title or not str(title).strip():
        raise ValueError("title_required")
    title = str(title).strip()
    description = payload.get("description")
    raw_status = payload.get("status")
    status_enum = _normalize_status(raw_status)
    parsed_date = _parse_iso_datetime(payload.get("date"))
    lat = payload.get("lat")
    lon = payload.get("lon")
    if lat is None or lon is None:
        raise ValueError("lat_lon_required")
    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        raise ValueError("lat_lon_invalid")
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        raise ValueError("lat_lon_out_of_range")

    if verify_creator:
        user = session.query(User).filter_by(id=created_by).first()
        if not user:
            raise ValueError("creator_not_found")

    m = Mission(
        title=title,
        description=description,
        status=status_enum,
        date=parsed_date,
        lat=lat,
        lon=lon,
        created_by=created_by,
    )
    session.add(m)
    session.flush()
    return m

def get_missions(session, mission_id):
    return session.query(Mission).filter_by(id=mission_id).first()
def delete_mission(session, mission_id, soft=True):

    m = session.query(Mission).filter_by(id=mission_id).first()
    if not m:
        return False
    if soft and hasattr(m, "is_deleted"):
        m.is_deleted = True
    else:
        session.delete(m)
        session.flush()
    return True

def update_mission(session, mission_id, patch_dict):

    m = session.query(Mission).filter_by(id=mission_id).first()
    if not m:
        return None
    else:
        allowed = {"title", "description", "status", "date", "lat", "lon"}
        to_apply = {}

        if "title" in patch_dict:
            title = patch_dict["title"]
            if not title or not str(title).strip():
                raise ValueError("title_required")
            title = str(title).strip()
            if len(title) > 255:
                raise ValueError("title_too_long")
            to_apply["title"] = title

        if "description" in patch_dict:
            description = patch_dict["description"]
            if description is not None:
                description = str(description).strip()
            to_apply["description"] = description

        if "status" in patch_dict:
            status = patch_dict["status"]
            if status is None:
                raise ValueError("invalid_status")
            status_enum = _normalize_status(status)
            to_apply["status"] = status_enum

        if "date" in patch_dict:
            date = patch_dict["date"]
            if date is None:
                to_apply["date"] = None
            else:
                try:
                    to_apply["date"] = _parse_iso_datetime(date.strip() if isinstance(date, str) else date)
                except ValueError:
                    raise ValueError("invalid_date")

        if "lat" in patch_dict or "lon" in patch_dict:
            new_lat = patch_dict.get("lat", m.lat)
            new_lon = patch_dict.get("lon", m.lon)
            if new_lat is None or new_lon is None:
                raise ValueError("lat_lon_required")
            try:
                n_lon = float(new_lon)
                n_lat = float(new_lat)
            except Exception:
                raise ValueError("lat_lon_invalid")
            if not (-90.0 <= n_lat <= 90.0) or not (-180.0 <= n_lon <= 180.0):
                raise ValueError("lat_lon_out_of_range")
            to_apply["lat"] = n_lat
            to_apply["lon"] = n_lon
    for k, v in to_apply.items():
        setattr(m, k, v)
    if hasattr(m, "save"):
        m.save()
    session.flush()
    return m

def list_missions(session, params: Optional[Dict[str, Any]] = None):
    """
    Retourne une page de missions filtrées selon `params`.
    params possible:
      - status: 'planned'|'active'|'done' (ou 'PLANNED' etc.)
      - date_from: ISO datetime
      - date_to: ISO datetime
      - created_by: user id
      - q: texte à chercher dans title ou description
      - page: int (>=1)
      - per_page: int
      - sort_by: 'date' | 'created_at' | 'title' (default 'date')
      - sort_dir: 'asc'|'desc' (default 'asc')
    Retour:
      { items: [mission_dict,...], total: int, page: int, per_page: int }
    """
    params = params or {}

    # pagination & tri — sanitation minimale
    try:
        page = max(1, int(params.get("page", 1)))
    except Exception:
        page = 1
    try:
        per_page = int(params.get("per_page", 20))
        per_page = max(1, min(200, per_page))  # limite raisonnable
    except Exception:
        per_page = 20

    sort_by = params.get("sort_by", "date")
    sort_dir = params.get("sort_dir", "asc").lower()
    sort_dir_fn = asc if sort_dir != "desc" else desc

    # début de la requête
    q = session.query(Mission)

    # filtre status
    status_raw = params.get("status")
    if status_raw is not None:
        status_enum = _normalize_status(status_raw)
        q = q.filter(Mission.status == status_enum)

    # filtre dates
    date_from_raw = params.get("date_from")
    date_to_raw = params.get("date_to")
    try:
        if date_from_raw:
            df = _parse_iso_datetime(date_from_raw)
            q = q.filter(Mission.date >= df)
        if date_to_raw:
            dt = _parse_iso_datetime(date_to_raw)
            q = q.filter(Mission.date <= dt)
    except Exception:
        raise ValueError("invalid_date")

    # recherche texte sur title/description
    search = params.get("q")
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(or_(Mission.title.ilike(s), Mission.description.ilike(s)))

    # created_by filter
    created_by = params.get("created_by")
    if created_by:
        q = q.filter(Mission.created_by == created_by)

    # count total (avant pagination)
    try:
        total = q.count()
    except Exception:
        # fallback si count pose problème
        total = len(q.all())

    # tri
    if sort_by == "created_at":
        order_col = Mission.created_at
    elif sort_by == "title":
        order_col = Mission.title
    else:
        order_col = Mission.date

    q = q.order_by(sort_dir_fn(order_col))

    # pagination
    offset = (page - 1) * per_page
    items = q.offset(offset).limit(per_page).all()

    # sérialisation en dict (utilise to_dict du modèle)
    items_serialized = [m.to_dict() for m in items]

    return {
        "items": items_serialized,
        "total": total,
        "page": page,
        "per_page": per_page,
    }