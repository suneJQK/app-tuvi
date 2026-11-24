// Kiểm thử engine an sao thật (Python qua Pyodide) + các hàm render trên kết quả thật.
// Chạy: npm test   (cần npm install trước)
import { test, before } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";
import { createEngine } from "../web/js/engine.js";
import * as R from "../web/js/render.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const engineDir = join(root, "engine");

function readBundle() {
  const bundle = {};
  const walk = (dir) => {
    for (const name of readdirSync(dir)) {
      const full = join(dir, name);
      if (statSync(full).isDirectory()) { if (name !== "__pycache__") walk(full); }
      else if (/\.(py|json)$/.test(name)) bundle[relative(engineDir, full).split("\\").join("/")] = readFileSync(full, "utf8");
    }
  };
  walk(engineDir);
  return bundle;
}

let engine;
before(async () => {
  engine = await createEngine({
    loadPyodide,
    indexURL: join(root, "node_modules", "pyodide") + "/",
    bundle: readBundle(),
  });
});

const BIRTH = { ten: "Test", ngay: 15, thang: 8, nam: 1990, gio_sinh: "Ngọ", gioi_tinh: "Nam", duong_lich: true, time_zone: 7 };
const VIEW = { nam_xem: 2026, thang_xem: 11, ngay_xem: 24, gio_xem: 5 };

test("lập lá số: đủ 12 cung, bàn số 4x4 không trùng ô", () => {
  const r = engine.tinhLaSo({ ...BIRTH, ...VIEW });
  assert.equal(r.palaces.length, 12);
  const cells = new Set(r.palaces.map((p) => `${p.vi_tri.row}-${p.vi_tri.column}`));
  assert.equal(cells.size, 12);
  for (const p of r.palaces) {
    assert.ok(p.vi_tri.row >= 1 && p.vi_tri.row <= 4 && p.vi_tri.column >= 1 && p.vi_tri.column <= 4);
  }
  assert.equal(r.palaces.filter((p) => p.than_cu).length, 1);
  assert.ok(r.palaces.some((p) => p.cung === "Mệnh"));
  assert.equal(r.summary.cung_menh, "Sửu");
  assert.equal(r.summary.so_sao > 50, true);
});

test("Lưu nguyệt / Lưu nhật / Lưu thời khớp engine gốc", () => {
  const r = engine.tinhLaSo({ ...BIRTH, ...VIEW });
  // Kết quả đối chiếu trực tiếp với calculate_van_layers của repo luangiaibysun.
  assert.equal(r.han.luu_nguyet.chi_ten, "Hợi");
  assert.equal(r.han.luu_nguyet.cung_ten, "Phu thê");
  assert.equal(r.han.luu_nhat.chi_ten, "Dần");
  assert.equal(r.han.luu_nhat.cung_ten, "Phụ mẫu");
  assert.equal(r.han.luu_thoi.chi_ten, "Thìn");
  assert.equal(r.han.luu_thoi.cung_ten, "Điền trạch");
});

test("không xem giờ thì không có Lưu thời; không xem ngày thì không có Lưu nhật", () => {
  const r = engine.tinhLaSo({ ...BIRTH, nam_xem: 2026, thang_xem: 11, ngay_xem: 24, gio_xem: null });
  assert.ok(!r.han.luu_thoi);
  assert.ok(r.han.luu_nhat);
  const r2 = engine.tinhLaSo({ ...BIRTH, nam_xem: 2026, thang_xem: null, ngay_xem: null, gio_xem: null });
  assert.ok(!r2.han.luu_nhat);
  assert.ok(!r2.han.luu_nguyet);
});

test("Lưu niên năm: 10 dòng đều có cung (đã sửa lỗi tra cung của engine gốc)", () => {
  const r = engine.tinhLaSo({ ...BIRTH, ...VIEW });
  assert.equal(r.van.rows.length, 10);
  for (const row of r.van.rows) {
    assert.ok(row.luu_nien_nam.cung, `năm ${row.nam} thiếu cung`);
    assert.ok(row.luu_nien_dai_van.cung && row.tieu_van.cung);
  }
  assert.ok(r.van.dai_van_hien_tai && r.van.dai_van_hien_tai.cung, "phải có Đại vận hiện tại");
  assert.equal(r.van.dai_van_hien_tai.cung, "Điền trạch");
  assert.equal(r.van.dai_van_hien_tai.tuoi_bat_dau, 36);
  // 2026 là năm Bính Ngọ -> cung Ngọ
  const y2026 = r.van.rows.find((x) => x.nam === 2026);
  assert.equal(y2026.luu_nien_nam.dia_chi, "Ngọ");
  assert.equal(y2026.luu_nien_nam.can_chi, "Bính Ngọ");
  assert.equal(y2026.luu_nien_nam.cung_can_chi, "Nhâm Ngọ");
});

test("Cách Cục, danh bạ sao, quan hệ cung đều có dữ liệu", () => {
  const r = engine.tinhLaSo({ ...BIRTH, ...VIEW });
  assert.ok(Array.isArray(r.cach_cuc.items));
  assert.ok(r.sao.length > 20);
  const tuVi = r.sao.find((s) => s.ten === "Tử vi");
  assert.ok(tuVi && tuVi.cung.length >= 1);
  const rel = r.relations["Mệnh"];
  assert.equal(rel.tam_hop.length, 2);
  assert.equal(rel.xung_chieu.length, 1);
  assert.equal(rel.nhi_hop.length, 1);
  assert.equal(rel.giap_cung.length, 2);
});

test("đầu vào sai báo lỗi tiếng Việt", () => {
  assert.throws(() => engine.tinhLaSo({ ...BIRTH, ngay: 31, thang: 2, ...VIEW }), /Ngày sinh không hợp lệ/);
  assert.throws(() => engine.tinhLaSo({ ...BIRTH, gio_sinh: "Xyz", ...VIEW }), /gio_sinh/);
});

test("âm lịch được đổi đúng (không báo lỗi, có Chi năm)", () => {
  const r = engine.tinhLaSo({ ...BIRTH, duong_lich: false, ...VIEW });
  assert.equal(r.chart.input.lich, "Âm lịch");
  assert.ok(r.summary.can_chi_nam.includes("Canh"));
});

test("các hàm render chạy trên kết quả thật và có escape HTML", () => {
  const r = engine.tinhLaSo({ ...BIRTH, ten: "<img src=x onerror=alert(1)>", ...VIEW });
  const html = [
    R.renderSummary(r), R.renderBoard(r, "Mệnh"), R.renderPalaceDetail(r, "Mệnh"),
    R.renderHanCards(r), R.renderVanTable(r), R.renderCach(r), R.renderSao(r, "tử"),
  ].join("\n");
  assert.ok(html.length > 2000);
  assert.ok(!html.includes("<img src=x"), "tên người dùng phải được escape");
  assert.ok(html.includes("Lưu nguyệt") && html.includes("Lưu nhật") && html.includes("Lưu thời"));
  assert.equal((R.renderBoard(r, "Mệnh").match(/class="cell /g) || []).length, 12);
});
