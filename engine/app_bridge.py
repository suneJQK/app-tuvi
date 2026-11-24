"""Cầu nối cho app di động (chạy trong Pyodide / WebAssembly).

Gom đúng pipeline của ``core/service.py`` trong repo luangiaibysun nhưng KHÔNG
phụ thuộc pydantic / FastAPI / cache, để có thể nạp trực tiếp trong trình duyệt
của điện thoại. Engine an sao (``tuvi_engine``) không bị sửa.

Pipeline:
    lap_la_so -> analyze_chart (Cách Cục) -> normalize_engine_chart
    -> calculate_chart (Đại vận, Tiểu vận, Lưu niên, Lưu nguyệt, Lưu nhật, Lưu thời)
    -> các view: tóm tắt, danh bạ sao, Cách Cục, bảng 10 năm, quan hệ cung.

Entry point duy nhất từ JS: ``tinh_la_so(payload_json) -> json``.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from chart_sanitizer import normalize_engine_chart
from tu_vi_calculator import calculate_chart
from tuvi_engine._engine.AmDuong import ngayThangNam
from tuvi_engine.engine.date_handler import normalize_birth_input
from tuvi_engine.rules.analysis import analyze_chart
from tuvi_engine.star_registry import star_catalog
from tuvi_lap_so_engine import lap_la_so

BRANCH_ORDER = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")
ELEMENT_LABEL = {"K": "Kim", "M": "Mộc", "T": "Thủy", "H": "Hỏa", "O": "Thổ"}
ELEMENT_KEY = {"K": "kim", "M": "moc", "T": "thuy", "H": "hoa", "O": "tho"}
DAC_TINH_LABEL = {"M": "Miếu", "V": "Vượng", "Đ": "Đắc", "B": "Bình", "H": "Hãm"}
TAM_HOP = (("Thân", "Tý", "Thìn"), ("Dần", "Ngọ", "Tuất"), ("Tỵ", "Dậu", "Sửu"), ("Hợi", "Mão", "Mùi"))
NHI_HOP = {"Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Hợi": "Dần", "Mão": "Tuất", "Tuất": "Mão",
           "Thìn": "Dậu", "Dậu": "Thìn", "Tỵ": "Thân", "Thân": "Tỵ", "Ngọ": "Mùi", "Mùi": "Ngọ"}


class EngineError(ValueError):
    """Lỗi nghiệp vụ trả về cho giao diện."""


# ----------------------------------------------------------------- helpers

def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def star_name(star: Any) -> str:
    if isinstance(star, dict):
        return str(star.get("ten") or star.get("name") or star.get("saoTen") or "").strip()
    return str(star or "").strip()


def element_label(raw: Any) -> str:
    key = str(raw or "").strip()
    return ELEMENT_LABEL.get(key, key or "—")


def element_key(raw: Any) -> str:
    return ELEMENT_KEY.get(str(raw or "").strip(), "")


def branch_of(palace: dict[str, Any]) -> str:
    for field in ("dia_chi", "branch", "chi"):
        value = str(palace.get(field) or "").strip()
        if value == "Tị":
            return "Tỵ"
        if value in BRANCH_ORDER:
            return value
    return ""


def palace_by_name(chart: dict[str, Any], name: str) -> dict[str, Any] | None:
    target = str(name or "").strip().casefold()
    for palace in as_list(chart.get("12_cung")):
        if str(palace.get("cung") or "").strip().casefold() == target:
            return palace
    return None


def cung_by_so(chart: dict[str, Any], number: Any) -> dict[str, Any] | None:
    """Cung theo số thứ tự Địa Chi (Tý = 1 … Hợi = 12) — engine trả về số này ở nhiều lớp hạn."""
    try:
        n = int(number)
    except (TypeError, ValueError):
        return None
    for palace in as_list(chart.get("12_cung")):
        if int(palace.get("cung_so") or 0) == n:
            return palace
    return None


CAN_NAMES = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")


def can_chi_of_year(year: int) -> str:
    return f"{CAN_NAMES[(int(year) - 4) % 10]} {BRANCH_ORDER[(int(year) - 4) % 12]}"


def cung_of_year(chart: dict[str, Any], year: int) -> dict[str, Any] | None:
    """Lưu niên năm: Chi của năm xem -> cung có cùng Địa Chi trên lá số (Tý = 2020 … )."""
    return cung_by_so(chart, (int(year) - 4) % 12 + 1)


def all_stars(palace: dict[str, Any]) -> list[dict[str, Any]]:
    out = list(as_list(palace.get("chinh_tinh"))) + list(as_list(palace.get("phu_tinh")))
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for star in out:
        key = star_name(star).casefold()
        if key and key not in seen:
            seen.add(key)
            unique.append(star)
    return unique


def star_kind(loai: Any) -> str:
    """Phân loại theo engine: 1 = chính tinh; < 10 = sao tốt; > 10 = hung tinh (sát/bại/ám/hình…)."""
    try:
        n = int(loai)
    except (TypeError, ValueError):
        return "tot"
    if n == 1:
        return "chinh"
    return "tot" if n < 10 else "hung"


def _star_view(star: Any, group: str) -> dict[str, Any]:
    dac = star.get("dac_tinh") or star.get("saoDacTinh") or ""
    return {
        "ten": star_name(star),
        "nhom": group,
        "kind": star_kind(star.get("loai") or star.get("saoLoai")),
        "ngu_hanh": element_label(star.get("ngu_hanh") or star.get("saoNguHanh")),
        "dac_tinh": DAC_TINH_LABEL.get(str(dac), ""),
    }


# ----------------------------------------------------------- Lưu nguyệt / nhật / thời
# Quy tắc (theo yêu cầu nghiệp vụ, KHÔNG dùng tiết khí của engine gốc):
#   Đấu quân năm sinh: lấy cung Địa Chi năm sinh (âm lịch) làm tháng Giêng, nghịch đếm
#   tới tháng sinh (âm), rồi thuận đếm tới giờ sinh thì dừng -> Đấu quân năm sinh.
#   Các năm sau: Đấu quân thuận bàn, mỗi năm một cung.
#   Lưu nguyệt: tháng Giêng tại Đấu quân, các tháng sau thuận bàn, mỗi tháng một cung.
#   Lưu nhật: mồng 1 tại cung Lưu nguyệt, thuận, mỗi ngày một cung.
#   Lưu thời: tại cung Lưu nhật, thuận, mỗi canh giờ một cung (Tý = cung Lưu nhật).

def solar_to_lunar(d: int, m: int, y: int, tz: float) -> tuple[int, int, int]:
    """Dương lịch -> âm lịch (ngày, tháng, năm) bằng lịch của engine."""
    ld, lm, ly = ngayThangNam(int(d), int(m), int(y), True, float(tz))[:3]
    return int(ld), int(lm), int(ly)


def dau_quan_nam_sinh(lunar_year: int, lunar_month: int, gio_idx: int) -> int:
    """Chỉ số Địa Chi (Tý=0) của Đấu quân năm sinh."""
    base = (int(lunar_year) - 4) % 12          # Địa Chi năm sinh = cung tháng Giêng
    return (base - (int(lunar_month) - 1) + (int(gio_idx) - 1)) % 12


def dau_quan_nam(dau_quan_sinh: int, birth_lunar_year: int, year: int) -> int:
    """Đấu quân năm `year` (âm): thuận bàn một cung mỗi năm kể từ năm sinh."""
    return (dau_quan_sinh + (int(year) - int(birth_lunar_year))) % 12


def _cung_at(chart: dict[str, Any], idx: int) -> dict[str, Any] | None:
    return cung_by_so(chart, (int(idx) % 12) + 1)


def _lunar_month_length(view: date, tz: float, ld: int, lm: int, ly: int) -> int:
    start = view - timedelta(days=ld - 1)   # dương lịch của mồng 1 âm
    count = 0
    for _ in range(31):
        cur = start + timedelta(days=count)
        l_d, l_m, l_y = solar_to_lunar(cur.day, cur.month, cur.year, tz)
        if (l_m, l_y) != (lm, ly):
            break
        count += 1
    return count


def luu_han_theo_quy_tac(
    chart: dict[str, Any],
    birth: dict[str, Any],
    view: date,
    gio_xem: int | None,
    tz: float,
) -> dict[str, Any]:
    """Đấu quân, Lưu nguyệt (12 tháng), Lưu nhật (các ngày tháng xem), Lưu thời (12 giờ)."""
    b_ld, b_lm, b_ly = birth["lunar"]
    gio_idx = birth["gio_idx"]
    dq_sinh = dau_quan_nam_sinh(b_ly, b_lm, gio_idx)

    ld, lm, ly = solar_to_lunar(view.day, view.month, view.year, tz)
    dq = dau_quan_nam(dq_sinh, b_ly, ly)
    month_start = (dq + lm - 1) % 12           # cung của mồng 1 tháng xem
    day_idx = (month_start + ld - 1) % 12      # cung của ngày xem

    def ten(idx: int) -> dict[str, Any]:
        pal = _cung_at(chart, idx)
        return {"cung_ten": pal.get("cung") if pal else None, "dia_chi": BRANCH_ORDER[idx % 12]}

    bang_thang = [{"thang_am": k, **ten((dq + k - 1) % 12)} for k in range(1, 13)]
    n_days = _lunar_month_length(view, tz, ld, lm, ly)
    bang_ngay = []
    for dd in range(1, n_days + 1):
        solar_d = view + timedelta(days=dd - ld)
        bang_ngay.append({"ngay_am": dd, "duong": solar_d.isoformat(),
                          **ten((month_start + dd - 1) % 12)})
    bang_gio = [{"gio": BRANCH_ORDER[h - 1], "gio_so": h, **ten((day_idx + h - 1) % 12)}
                for h in range(1, 13)]

    chosen_thang = {"thang_am": lm, **ten((dq + lm - 1) % 12)}
    nguyet = {
        "nam_am": ly, "thang_am": lm, "cung_ten": chosen_thang["cung_ten"],
        "dia_chi": chosen_thang["dia_chi"], "bang": bang_thang,
        "phuong_phap": "Đấu quân năm xem thuận bàn; tháng Giêng tại Đấu quân, mỗi tháng một cung.",
    }
    nhat = {
        "ngay_am": ld, "thang_am": lm, "duong": view.isoformat(),
        "cung_ten": ten(day_idx)["cung_ten"], "dia_chi": ten(day_idx)["dia_chi"],
        "bang": bang_ngay, "so_ngay_trong_thang": n_days,
        "phuong_phap": "Mồng 1 tại cung Lưu nguyệt, thuận, mỗi ngày một cung.",
    }
    thoi = {
        "gio_so": gio_xem,
        "gio": BRANCH_ORDER[gio_xem - 1] if gio_xem else None,
        "cung_ten": ten((day_idx + gio_xem - 1) % 12)["cung_ten"] if gio_xem else None,
        "bang": bang_gio,
        "phuong_phap": "Tại cung Lưu nhật, thuận, mỗi canh giờ một cung (Tý = cung Lưu nhật).",
    }
    pal_dq = ten(dq)
    dau_quan_info = {
        "nam_am": ly, "cung_ten": pal_dq["cung_ten"], "dia_chi": pal_dq["dia_chi"],
        "dau_quan_sinh_cung_ten": ten(dq_sinh)["cung_ten"], "dau_quan_sinh_dia_chi": ten(dq_sinh)["dia_chi"],
        "phuong_phap": "Đấu quân năm sinh: Địa Chi năm sinh làm tháng Giêng, nghịch đến tháng sinh (âm), "
                       "thuận đến giờ sinh. Các năm sau thuận bàn một cung mỗi năm.",
    }
    return {"dau_quan": dau_quan_info, "luu_nguyet": nguyet, "luu_nhat": nhat, "luu_thoi": thoi}


# ----------------------------------------------------------------- views

def chart_summary(chart: dict[str, Any]) -> dict[str, Any]:
    tb = chart.get("thien_ban") or {}
    palaces = as_list(chart.get("12_cung"))
    menh = palace_by_name(chart, "Mệnh") or {}
    than = next((p for p in palaces if p.get("than_cu")), {})
    counts = {"kim": 0, "moc": 0, "thuy": 0, "hoa": 0, "tho": 0}
    for palace in palaces:
        key = element_key(palace.get("ngu_hanh"))
        if key in counts:
            counts[key] += 1
    return {
        "ten": tb.get("ten") or "—",
        "can_chi_nam": " ".join(x for x in (tb.get("can_nam"), tb.get("chi_nam")) if x) or "—",
        "ban_menh": tb.get("ban_menh") or "—",
        "ten_cuc": tb.get("ten_cuc") or "—",
        "menh_chu": tb.get("menh_chu") or "—",
        "than_chu": tb.get("than_chu") or "—",
        "am_duong_menh": tb.get("am_duong_menh") or "—",
        "sinh_khac": tb.get("sinh_khac") or "—",
        "cung_menh": branch_of(menh) or "—",
        "cung_than": than.get("cung") or "—",
        "so_sao": sum(len(all_stars(p)) for p in palaces),
        "so_cach_cuc": len(as_list((chart.get("cach_cuc_analysis") or {}).get("matched"))),
        "ngu_hanh_cung": counts,
    }


def palace_relations(chart: dict[str, Any], name: str) -> dict[str, Any]:
    """Quan hệ cung suy từ Địa Chi (Tam Hợp / Xung Chiếu / Nhị Hợp / Giáp Cung)."""
    palace = palace_by_name(chart, name)
    if not palace:
        raise EngineError(f"Không tìm thấy cung '{name}'")
    branch = branch_of(palace)
    by_branch = {branch_of(p): p for p in as_list(chart.get("12_cung")) if branch_of(p)}
    index = BRANCH_ORDER.index(branch)
    group = next((g for g in TAM_HOP if branch in g), ())
    opposite = BRANCH_ORDER[(index + 6) % 12]
    neighbours = (BRANCH_ORDER[(index - 1) % 12], BRANCH_ORDER[(index + 1) % 12])

    def pack(branch_name: str, relation: str) -> dict[str, Any] | None:
        target = by_branch.get(branch_name)
        if not target:
            return None
        return {
            "quan_he": relation,
            "cung": target.get("cung"),
            "dia_chi": branch_name,
            "can_chi": target.get("can_chi"),
            "ngu_hanh": element_label(target.get("ngu_hanh")),
            "chinh_tinh": [star_name(s) for s in as_list(target.get("chinh_tinh"))],
        }

    return {
        "cung": palace.get("cung"),
        "dia_chi": branch,
        "tam_hop": [x for x in (pack(b, "Tam Hợp") for b in group if b != branch) if x],
        "xung_chieu": [x for x in [pack(opposite, "Xung Chiếu")] if x],
        "nhi_hop": [x for x in [pack(NHI_HOP.get(branch, ""), "Nhị Hợp")] if x],
        "giap_cung": [x for x in (pack(b, "Giáp Cung") for b in neighbours) if x],
    }


def star_directory(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Danh bạ sao: mỗi sao ở những cung nào."""
    registry = {str(item.get("ten") or "").casefold(): item for item in star_catalog()}
    bucket: dict[str, dict[str, Any]] = {}
    for palace in as_list(chart.get("12_cung")):
        palace_name = palace.get("cung") or f"Cung {palace.get('cung_so') or '?'}"
        branch = branch_of(palace) or "—"
        main_names = {star_name(s).casefold() for s in as_list(palace.get("chinh_tinh"))}
        for star in all_stars(palace):
            name = star_name(star)
            key = name.casefold()
            if not key:
                continue
            item = bucket.setdefault(key, {
                "ten": name,
                "ngu_hanh": element_label(star.get("ngu_hanh") or star.get("saoNguHanh")),
                "phuong_vi": star.get("phuong_vi") or star.get("saoPhuongVi") or "",
                "nhom": "Phụ tinh",
                "cung": [],
                "so_lan": 0,
            })
            item["so_lan"] += 1
            if key in main_names:
                item["nhom"] = "Chính tinh"
            item["cung"].append({
                "cung": palace_name,
                "dia_chi": branch,
                "dac_tinh": DAC_TINH_LABEL.get(str(star.get("dac_tinh") or star.get("saoDacTinh") or ""), ""),
            })
            if not item["phuong_vi"]:
                item["phuong_vi"] = str((registry.get(key) or {}).get("phuong_vi") or "")
    return sorted(bucket.values(), key=lambda x: (x["nhom"] != "Chính tinh", x["ten"]))


def cach_cuc_view(chart: dict[str, Any]) -> dict[str, Any]:
    analysis = chart.get("cach_cuc_analysis") or {}

    def evidence_of(item: dict[str, Any]) -> list[Any]:
        for field in ("matched_branches", "evidence", "breaking_evidence"):
            value = as_list(item.get(field))
            if value:
                return value
        return []

    def normalize(item: dict[str, Any], kind: str) -> dict[str, Any]:
        interpretation = item.get("interpretation")
        text = interpretation if isinstance(interpretation, str) else ""
        if isinstance(interpretation, dict):
            text = " · ".join(str(v) for v in interpretation.values() if isinstance(v, str))[:1200]
        evidence = evidence_of(item)
        return {
            "rule_id": item.get("id") or "—",
            "name": item.get("name") or "Cách Cục",
            "kind": kind,
            "description": item.get("description") or item.get("reason") or "",
            "interpretation": text,
            "evidence": evidence,
        }

    matched = [normalize(x, "cach_cuc") for x in as_list(analysis.get("matched")) if isinstance(x, dict)]
    modifiers = [normalize(x, "modifier") for x in as_list(analysis.get("modifiers")) if isinstance(x, dict)]
    return {"items": matched + modifiers, "matched_count": len(matched), "modifier_count": len(modifiers)}


def van_table(chart: dict[str, Any]) -> dict[str, Any]:
    """Bảng 10 năm: Đại vận, Lưu niên Đại vận, Tiểu vận, Lưu niên năm (lấy từ engine)."""
    van = chart.get("van") or {}
    dai_van = as_list(van.get("luu_nien_dai_van_10_nam"))
    tieu_van = as_list(van.get("tieu_van_10_nam"))
    luu_nien = as_list(van.get("luu_nien_nam_10_nam"))
    dv_block = (van.get("van_10_nam") or {}).get("dai_van") or {}
    rows: list[dict[str, Any]] = []
    for i in range(min(10, max(len(dai_van), len(tieu_van), len(luu_nien)))):
        a = dai_van[i] if i < len(dai_van) else {}
        b = tieu_van[i] if i < len(tieu_van) else {}
        c = luu_nien[i] if i < len(luu_nien) else {}
        year = a.get("nam") or b.get("nam") or c.get("nam")
        # Engine trả cung của Lưu niên năm = None (tra theo Chi kiểu int). Tính lại ở đây
        # từ năm để đảm bảo cùng quy tắc: Chi năm -> cung có cùng Địa Chi.
        palace_c = cung_of_year(chart, int(year)) if year else None
        c = {**c, "cung": (palace_c or {}).get("cung"), "dia_chi": branch_of(palace_c or {}),
             "can_chi": can_chi_of_year(year) if year else None,
             "cung_can_chi": (palace_c or {}).get("can_chi")}
        rows.append({
            "nam": year,
            "tuoi": a.get("tuoi") or b.get("tuoi") or c.get("tuoi"),
            "luu_nien_dai_van": {"cung": a.get("cung"), "dia_chi": a.get("dia_chi"), "can_chi": a.get("can_chi")},
            "tieu_van": {"cung": b.get("cung"), "dia_chi": b.get("dia_chi") or b.get("chi_ten"), "can_chi": b.get("can_chi")},
            "luu_nien_nam": {"cung": c.get("cung"), "dia_chi": c.get("dia_chi"), "can_chi": c.get("can_chi"),
                             "cung_can_chi": c.get("cung_can_chi")},
            "la_nam_dang_xem": bool(a.get("la_nam_dang_xem") or b.get("la_nam_dang_xem") or c.get("la_nam_dang_xem")),
        })
    dang_xet = (van.get("dai_van") or {}).get("dang_xet") or {}
    return {
        "tuoi": van.get("age"),
        "dai_van_hien_tai": {
            "cung_so": dv_block.get("cung_so") or dang_xet.get("cung_so"),
            "cung": dv_block.get("cung") or dang_xet.get("cung"),
            "tuoi_bat_dau": dv_block.get("tuoi_bat_dau") or dang_xet.get("tuoi_bat_dau"),
            "tuoi_ket_thuc": dv_block.get("tuoi_ket_thuc") or dang_xet.get("tuoi_ket_thuc"),
        } if (dv_block.get("cung_so") or dang_xet.get("cung_so")) else None,
        "huong_vong_van": dv_block.get("huong") or dang_xet.get("huong"),
        "rows": rows,
    }


def han_hien_tai(chart: dict[str, Any]) -> dict[str, Any]:
    """Các lớp hạn cho đúng ngày/tháng/giờ đang xem: Lưu nguyệt, Lưu nhật, Lưu thời."""
    van = chart.get("van") or {}

    def pick(key: str) -> dict[str, Any] | None:
        value = van.get(key)
        if not isinstance(value, dict):
            return None
        return {k: v for k, v in value.items() if k != "warning"} | (
            {"warning": value["warning"]} if value.get("warning") else {}
        )

    def named(block: dict[str, Any] | None, *fields: str) -> dict[str, Any] | None:
        """Gắn tên cung cho các trường số (cung_so) mà engine trả về."""
        if block is None:
            return None
        out = dict(block)
        for field in fields:
            pal = cung_by_so(chart, block.get(field))
            out[f"{field}_ten"] = pal.get("cung") if pal else None
            out[f"{field}_dia_chi"] = branch_of(pal) if pal else None
        return out

    year = (chart.get("viewing") or {}).get("year")
    luu_nien = named(van.get("luu_nien") if isinstance(van.get("luu_nien"), dict) else None,
                     "cung_nam", "cung_luu_nien_trong_dai_van")
    if luu_nien is not None:
        palace_year = cung_of_year(chart, int(year)) if year else None
        luu_nien["cung_nam_ten"] = (palace_year or {}).get("cung")
        luu_nien["cung_nam_dia_chi"] = branch_of(palace_year or {})
    return {
        "luu_nien": luu_nien,
        "tieu_van": van.get("tieu_van"),
        "dai_van": (van.get("dai_van") or {}).get("dang_xet") if isinstance(van.get("dai_van"), dict) else None,
        "luu_nien_dai_van": van.get("luu_nien_dai_van") if isinstance(van.get("luu_nien_dai_van"), dict) else None,
    }


# ----------------------------------------------------------------- entry

def tinh_la_so(payload: str) -> str:
    """Lập lá số + vận hạn cho ngày xem. Trả về JSON chuỗi.

    payload keys: ten, ngay, thang, nam, gio_sinh (1..12 hoặc tên Chi), gioi_tinh (Nam/Nữ),
    duong_lich (bool), time_zone (float), nam_xem, thang_xem, ngay_xem, gio_xem (1..12 hoặc null).
    """
    try:
        p = json.loads(payload)
        ngay, thang, nam = int(p["ngay"]), int(p["thang"]), int(p["nam"])
        duong = bool(p.get("duong_lich", True))
        tz = float(p.get("time_zone", 7.0))
        try:
            raw = lap_la_so(ngay, thang, nam, p["gio_sinh"], p["gioi_tinh"], str(p.get("ten") or ""), duong, tz)
        except ValueError as exc:
            raise EngineError(str(exc)) from exc
        if len(raw.get("12_cung") or {}) != 12:
            raise EngineError("Engine không tạo đủ 12 cung")

        analyzed = analyze_chart(raw)
        analyzed.setdefault("input", {})["lich"] = "Dương lịch" if duong else "Âm lịch"
        chart = normalize_engine_chart(analyzed)

        nam_xem = int(p.get("nam_xem") or nam)
        thang_xem = p.get("thang_xem")
        ngay_xem = p.get("ngay_xem")
        gio_xem = p.get("gio_xem")
        thang_xem = int(thang_xem) if thang_xem else None
        ngay_xem = int(ngay_xem) if ngay_xem else None
        gio_xem = int(gio_xem) if gio_xem else None
        try:
            calc = calculate_chart(chart, year=nam_xem, month=thang_xem, day=ngay_xem, hour=gio_xem)
        except ValueError as exc:
            raise EngineError(str(exc)) from exc
        chart["van"] = calc.get("van", {})
        chart["viewing"] = {"year": nam_xem, "month": thang_xem, "day": ngay_xem, "hour": gio_xem}
        chart.pop("ai_context", None)

        norm = normalize_birth_input(ngay, thang, nam, p["gio_sinh"], p["gioi_tinh"], "", duong, tz)
        birth_lunar = solar_to_lunar(ngay, thang, nam, tz) if duong else (ngay, thang, nam)
        han_moi: dict[str, Any] = {}
        if thang_xem and ngay_xem:
            han_moi = luu_han_theo_quy_tac(
                chart,
                {"lunar": birth_lunar, "gio_idx": norm.hour},
                date(nam_xem, thang_xem, ngay_xem),
                gio_xem,
                tz,
            )

        palaces = as_list(chart.get("12_cung"))
        result = {
            "chart": chart,
            "summary": chart_summary(chart),
            "cach_cuc": cach_cuc_view(chart),
            "sao": star_directory(chart),
            "van": van_table(chart),
            "han": {**han_hien_tai(chart), **han_moi},
            "relations": {str(pl.get("cung")): palace_relations(chart, str(pl.get("cung"))) for pl in palaces},
            "palaces": [
                {
                    "cung": pl.get("cung"),
                    "cung_so": pl.get("cung_so"),
                    "dia_chi": branch_of(pl),
                    "can_chi": pl.get("can_chi"),
                    "ngu_hanh": element_label(pl.get("ngu_hanh")),
                    "am_duong": pl.get("am_duong"),
                    "than_cu": bool(pl.get("than_cu")),
                    "tuan": bool(pl.get("tuan")),
                    "triet": bool(pl.get("triet")),
                    "trang_sinh": pl.get("vong_trang_sinh"),
                    "dai_van": (pl.get("dai_van") or {}).get("tuoi_bat_dau"),
                    "tieu_van_chi": (pl.get("tieu_van") or {}).get("chi"),
                    "vi_tri": pl.get("vi_tri"),
                    "chinh_tinh": [_star_view(s, "Chính tinh") for s in as_list(pl.get("chinh_tinh"))],
                    "phu_tinh": [_star_view(s, "Phụ tinh") for s in as_list(pl.get("phu_tinh"))],
                }
                for pl in palaces
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)
    except EngineError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    except (KeyError, TypeError, ValueError) as exc:
        return json.dumps({"error": f"Dữ liệu đầu vào không hợp lệ: {exc}"}, ensure_ascii=False)
