#!/usr/bin/env python3
"""
Khôi phục & kẻ bảng chuẩn 100% cho các bảng lớn bị vỡ dòng trong Chương II & Chương III:
1. Trang 62 (Chương II): Bảng Lục Thập Giáp Tý Nạp Âm (30 cặp / 60 Hoa Giáp)
2. Trang 79–80 (Chương III): Bảng Thuộc tính Ngũ hành của các Diệu Tinh
3. Trang 87–89 (Chương III): Bảng Các Sao trong 12 Cung Miếu, Vượng, Đắc địa, Bình, Hãm
Sau đó hợp nhất lại TAI_LIEU_BIEN_TAP_DAY_DU.md.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TD_DIR = ROOT / "tai-lieu-bien-tap"


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


TABLE_NAP_AM = """
**Bảng Lục Thập Giáp Tý Nạp Âm (60 Hoa Giáp)**

""" + md_table(
    ["Ngũ hành (Cục)", "Cặp 1 (Can Chi — Nạp Âm)", "Cặp 2 (Can Chi — Nạp Âm)", "Cặp 3 (Can Chi — Nạp Âm)"],
    [
        ["**KIM (4)**", "Giáp Tý, Ất Sửu — Hải Trung Kim", "Nhâm Thân, Quý Dậu — Kiếm Phong Kim", "Canh Thìn, Tân Tỵ — Bạch Lạp Kim"],
        ["**KIM (4)**", "Giáp Ngọ, Ất Mùi — Sa Trung Kim", "Nhâm Dần, Quý Mão — Kim Bạch Kim", "Canh Tuất, Tân Hợi — Thoa Xuyến Kim"],
        ["**MỘC (3)**", "Mậu Thìn, Kỷ Tỵ — Đại Lâm Mộc", "Nhâm Ngọ, Quý Mùi — Dương Liễu Mộc", "Canh Dần, Tân Mão — Tùng Bách Mộc"],
        ["**MỘC (3)**", "Mậu Tuất, Kỷ Hợi — Bình Địa Mộc", "Nhâm Tý, Quý Sửu — Tang Đố Mộc", "Canh Thân, Tân Dậu — Thạch Lựu Mộc"],
        ["**THỦY (2)**", "Bính Tý, Đinh Sửu — Giản Hạ Thủy", "Giáp Thân, Ất Dậu — Tuyền Trung Thủy", "Nhâm Thìn, Quý Tỵ — Trường Lưu Thủy"],
        ["**THỦY (2)**", "Bính Ngọ, Đinh Mùi — Thiên Hà Thủy", "Giáp Dần, Ất Mão — Đại Khê Thủy", "Nhâm Tuất, Quý Hợi — Đại Hải Thủy"],
        ["**HỎA (6)**", "Bính Dần, Đinh Mão — Lư Trung Hỏa", "Giáp Tuất, Ất Hợi — Sơn Đầu Hỏa", "Mậu Tý, Kỷ Sửu — Tích Lịch Hỏa"],
        ["**HỎA (6)**", "Bính Thân, Đinh Dậu — Sơn Hạ Hỏa", "Giáp Thìn, Ất Tỵ — Phúc Đăng Hỏa", "Mậu Ngọ, Kỷ Mùi — Thiên Thượng Hỏa"],
        ["**THỔ (5)**", "Canh Ngọ, Tân Mùi — Lộ Bàng Thổ", "Mậu Dần, Kỷ Mão — Thành Đầu Thổ", "Bính Tuất, Đinh Hợi — Ốc Thượng Thổ"],
        ["**THỔ (5)**", "Canh Tý, Tân Sửu — Bích Thượng Thổ", "Mậu Thân, Kỷ Dậu — Đại Trạch Thổ", "Bính Thìn, Đinh Tỵ — Sa Trung Thổ"],
    ],
)


TABLE_NGU_HANH_SAO = """
**Bảng liệt kê thuộc tính Ngũ hành chủ yếu của các Diệu Tinh (Sao)**

""" + md_table(
    ["Tên Sao", "Ngũ Hành", "Tên Sao", "Ngũ Hành", "Tên Sao", "Ngũ Hành"],
    [
        ["Tử Vi", "Âm Thổ", "Thiên Cơ", "Âm Mộc", "Thái Dương", "Dương Hỏa"],
        ["Vũ Khúc", "Âm Kim", "Thiên Đồng", "Dương Thủy", "Liêm Trinh", "Âm Hỏa"],
        ["Thiên Phủ", "Dương Thổ", "Thái Âm", "Âm Thủy", "Tham Lang", "Dương Mộc / Âm Thủy"],
        ["Cự Môn", "Âm Thủy", "Thiên Tướng", "Dương Thủy", "Thiên Lương", "Dương Thổ"],
        ["Thất Sát", "Âm Kim / Dương Hỏa", "Phá Quân", "Âm Thủy", "Văn Xương", "Dương Kim"],
        ["Văn Khúc", "Âm Thủy", "Tả Phù", "Dương Thổ", "Hữu Bật", "Âm Thủy"],
        ["Thiên Khôi", "Dương Hỏa", "Thiên Việt", "Âm Hỏa", "Kình Dương", "Dương Kim"],
        ["Đà La", "Âm Kim", "Hỏa Tinh", "Dương Hỏa", "Linh Tinh", "Âm Hỏa"],
        ["Địa Không", "Âm Hỏa", "Địa Kiếp", "Dương Hỏa", "Lộc Tồn", "Âm Thổ"],
        ["Thiên Mã", "Dương Hỏa", "Hóa Lộc", "Âm Thổ", "Hóa Quyền", "Dương Mộc"],
        ["Hóa Khoa", "Dương Mộc", "Hóa Kỵ", "Dương Thủy", "Thiên Hình", "Dương Hỏa"],
        ["Thiên Diêu", "Âm Thủy", "Hàm Trì", "Âm Thủy", "Hồng Loan", "Âm Thủy"],
        ["Thiên Hỉ", "Dương Thủy", "Thiên Khốc", "Dương Kim", "Thiên Hư", "Âm Thổ"],
        ["Long Trì", "Dương Thủy", "Phượng Các", "Dương Thổ", "Cô Thần / Quả Tú", "Dương Hỏa / Âm Hỏa"],
    ],
)


TABLE_MIEU_VUONG_HAM = """
**BẢNG CÁC SAO TRONG 12 CUNG: MIẾU, VƯỢNG, ĐẮC ĐỊA, BÌNH, HÃM**

""" + md_table(
    ["Cung vị", "Miếu địa", "Vượng địa", "Đắc địa", "Bình hòa", "Hãm địa"],
    [
        ["**Tý**", "Thiên Cơ, Thiên Phủ, Thái Âm, Thiên Lương, Phá Quân, Lộc Tồn, Thiên Khôi", "Vũ Khúc, Thiên Đồng, Cự Môn, Thiên Tướng, Thất Sát, Văn Khúc", "Tả Phù, Hữu Bật, Thiên Khốc, Thiên Hư", "Tử Vi, Liêm Trinh, Tham Lang, Văn Xương", "Thái Dương, Kình Dương, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp, Hóa Kỵ"],
        ["**Sửu**", "Tử Vi, Vũ Khúc, Thiên Phủ, Thái Âm, Tham Lang, Thất Sát, Văn Xương, Văn Khúc, Tả Phù, Hữu Bật, Kình Dương, Đà La", "Thiên Lương, Phá Quân", "Thiên Tướng, Hỏa Tinh, Linh Tinh", "Thiên Cơ, Liêm Trinh, Cự Môn", "Thái Dương, Thiên Đồng, Địa Không, Địa Kiếp"],
        ["**Dần**", "Tử Vi, Thiên Phủ, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Lộc Tồn, Hỏa Tinh, Linh Tinh", "Thái Dương, Liêm Trinh, Thiên Đồng, Văn Xương, Văn Khúc", "Thiên Cơ, Vũ Khúc, Phá Quân, Tả Phù, Hữu Bật, Địa Không, Địa Kiếp", "Tham Lang, Thiên Mã", "Thái Âm, Đà La"],
        ["**Mão**", "Thái Dương, Thiên Cơ, Cự Môn, Thiên Lương, Lộc Tồn", "Thiên Đồng, Phá Quân, Hỏa Tinh, Linh Tinh", "Vũ Khúc, Liêm Trinh, Thiên Phủ, Tham Lang, Thiên Tướng, Thất Sát, Tả Phù, Hữu Bật", "Tử Vi, Văn Xương, Văn Khúc", "Thái Âm, Kình Dương, Địa Không, Địa Kiếp"],
        ["**Thìn**", "Vũ Khúc, Thiên Phủ, Tham Lang, Thiên Lương, Thất Sát, Văn Xương, Văn Khúc, Tả Phù, Hữu Bật, Kình Dương, Đà La", "Thái Dương, Tử Vi, Thiên Tướng", "Thiên Cơ, Liêm Trinh, Phá Quân", "Thiên Đồng, Cự Môn, Hỏa Tinh, Linh Tinh", "Thái Âm, Địa Không, Địa Kiếp"],
        ["**Tỵ**", "Thái Dương, Thiên Phủ, Lộc Tồn, Hỏa Tinh, Linh Tinh", "Tử Vi, Vũ Khúc, Thiên Lương, Văn Xương, Văn Khúc", "Thiên Cơ, Liêm Trinh, Thiên Tướng, Thất Sát, Tả Phù, Hữu Bật, Địa Không, Địa Kiếp", "Thiên Đồng, Phá Quân", "Thái Âm, Tham Lang, Cự Môn, Đà La"],
        ["**Ngọ**", "Tử Vi, Thái Dương, Thiên Phủ, Thiên Lương, Thất Sát, Phá Quân, Lộc Tồn, Hỏa Tinh, Linh Tinh", "Thiên Cơ, Vũ Khúc, Thiên Đồng, Cự Môn, Thiên Tướng, Văn Khúc", "Tả Phù, Hữu Bật, Thiên Khốc, Thiên Hư", "Liêm Trinh, Tham Lang, Văn Xương", "Thái Âm, Kình Dương, Địa Không, Địa Kiếp"],
        ["**Mùi**", "Tử Vi, Vũ Khúc, Thiên Phủ, Tham Lang, Thất Sát, Văn Xương, Văn Khúc, Tả Phù, Hữu Bật, Kình Dương, Đà La", "Thái Dương, Thái Âm, Thiên Lương, Phá Quân", "Thiên Tướng, Hỏa Tinh, Linh Tinh", "Thiên Cơ, Liêm Trinh, Cự Môn", "Thiên Đồng, Địa Không, Địa Kiếp"],
        ["**Thân**", "Tử Vi, Thiên Phủ, Cự Môn, Thiên Tướng, Thất Sát, Lộc Tồn", "Thiên Đồng, Liêm Trinh, Thái Âm, Văn Xương, Văn Khúc", "Thiên Cơ, Vũ Khúc, Thiên Lương, Phá Quân, Tả Phù, Hữu Bật, Địa Không, Địa Kiếp", "Thái Dương, Tham Lang, Hỏa Tinh, Linh Tinh", "Đà La"],
        ["**Dậu**", "Thiên Cơ, Thái Âm, Cự Môn, Lộc Tồn, Văn Xương, Văn Khúc", "Phá Quân", "Vũ Khúc, Liêm Trinh, Thiên Phủ, Tham Lang, Thiên Tướng, Thiên Lương, Thất Sát, Tả Phù, Hữu Bật", "Tử Vi, Thiên Đồng", "Thái Dương, Kình Dương, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp"],
        ["**Tuất**", "Vũ Khúc, Thiên Phủ, Thái Âm, Tham Lang, Thất Sát, Văn Xương, Văn Khúc, Tả Phù, Hữu Bật, Kình Dương, Đà La", "Tử Vi, Thiên Tướng, Thiên Lương", "Thiên Cơ, Liêm Trinh, Phá Quân, Hỏa Tinh, Linh Tinh", "Thiên Đồng, Cự Môn", "Thái Dương, Địa Không, Địa Kiếp"],
        ["**Hợi**", "Thái Âm, Thiên Phủ, Lộc Tồn", "Tử Vi, Vũ Khúc, Thiên Đồng, Văn Xương, Văn Khúc", "Thiên Cơ, Liêm Trinh, Thiên Tướng, Thất Sát, Tả Phù, Hữu Bật, Địa Không, Địa Kiếp", "Cự Môn, Phá Quân", "Thái Dương, Tham Lang, Thiên Lương, Đà La, Hỏa Tinh, Linh Tinh"],
    ],
)


def patch_ch2():
    p = TD_DIR / "02-chuong-2-muoi-hai-cung.md"
    t = p.read_text(encoding="utf-8")
    # Thay thế toàn bộ trang 62 (Lục thập giáp tý nạp âm) bị vỡ dòng
    pattern = r"(<!-- Trang 62 .*?-->)(.*?)(?=<!-- Trang 63 )"
    m = re.search(pattern, t, re.S)
    if m:
        replacement = m.group(1) + "\n" + TABLE_NAP_AM.strip() + "\n\n"
        t = t[:m.start()] + replacement + t[m.end():]
        p.write_text(t, encoding="utf-8")
        print("Đã khôi phục Bảng Lục Thập Giáp Tý Nạp Âm (Trang 62 - Chương II)!")


def patch_ch3():
    p = TD_DIR / "03-chuong-3-dieu-tinh-va-tu-hoa.md"
    t = p.read_text(encoding="utf-8")

    # 1. Trang 79-80: Bảng thuộc tính ngũ hành của các diệu tinh
    pat1 = r"Bảng liệt kê thuộc tính ngũ hành chủ yếu của các diệu tinh \(SAO\).*?(?=<!-- Trang 81 )"
    if re.search(pat1, t, re.S):
        t = re.sub(pat1, TABLE_NGU_HANH_SAO.strip() + "\n\n", t, count=1, flags=re.S)
        print("Đã khôi phục Bảng Thuộc tính Ngũ hành các Diệu Tinh (Trang 79-80 - Chương III)!")

    # 2. Trang 87-89: Bảng Các sao trong 12 cung Miếu, Vượng, Đắc địa, Bình, Hãm
    pat2 = r"BẢNG CÁC SAO TRONG 12 CUNG MIẾU, VƯỢNG, ĐẮC ĐỊA,.*?(?=<!-- Trang 90 )"
    if re.search(pat2, t, re.S):
        t = re.sub(pat2, TABLE_MIEU_VUONG_HAM.strip() + "\n\n", t, count=1, flags=re.S)
        print("Đã khôi phục Bảng 12 Cung Miếu-Vượng-Đắc-Bình-Hãm (Trang 87-89 - Chương III)!")

    p.write_text(t, encoding="utf-8")


def rebuild_full_md():
    parts = [
        "# TUYỂN TẬP MỆNH LÝ THIÊN CƠ — TỬ VI NAM PHÁI (BẢN BIÊN TẬP & HIỆU ĐÍNH TOÀN VĂN)",
        "### *(Giữ nguyên toàn văn 1.000 trang tài liệu gốc, đã chuẩn hóa toàn bộ bảng biểu từ Chương I đến Chương V, sửa lỗi sai và bổ sung chú thích giải nghĩa xuyên suốt)*\n",
        "---\n",
    ]
    for fname in sorted(TD_DIR.glob("*.md")):
        parts.append(fname.read_text(encoding="utf-8").strip())
        parts.append("\n---\n")
    full_md = ROOT / "TAI_LIEU_BIEN_TAP_DAY_DU.md"
    full_md.write_text("\n".join(parts), encoding="utf-8")
    print(f"Đã hợp nhất lại {full_md.name} ({full_md.stat().st_size:,} bytes)")


if __name__ == "__main__":
    patch_ch2()
    patch_ch3()
    rebuild_full_md()
