// Hàm dựng HTML thuần từ kết quả engine. Mọi chuỗi đưa vào HTML đều đi qua esc().

export const CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];
export const GIO_LABEL = ["23–01", "01–03", "03–05", "05–07", "07–09", "09–11", "11–13", "13–15", "15–17", "17–19", "19–21", "21–23"];
const ELEMENT_CLASS = { "Kim": "el-kim", "Mộc": "el-moc", "Thủy": "el-thuy", "Hỏa": "el-hoa", "Thổ": "el-tho" };
const TAG = {
  dai_van: { abbr: "ĐV", title: "Đại vận hiện tại" },
  luu_nien_dai_van: { abbr: "LNĐV", title: "Lưu niên Đại vận" },
  tieu_van: { abbr: "TV", title: "Tiểu vận" },
  luu_nien_nam: { abbr: "LN", title: "Lưu niên (Chi năm)" },
  luu_nguyet: { abbr: "LNg", title: "Lưu nguyệt (tháng tiết khí)" },
  luu_nhat: { abbr: "LNh", title: "Lưu nhật (ngày xem)" },
  luu_thoi: { abbr: "LT", title: "Lưu thời (giờ xem)" },
};

export function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

const dacLabel = (star) => (star.dac_tinh ? `<span class="dac">(${esc(star.dac_tinh)})</span>` : "");
const palaceByName = (result, name) => result.palaces.find((p) => p.cung === name);

/** Tên cung đang chịu từng lớp hạn cho năm xem (dùng để gắn nhãn lên bàn số). */
export function hanTags(result) {
  const year = result.chart.viewing?.year;
  const row = (result.van.rows || []).find((r) => r.nam === year) || {};
  const han = result.han || {};
  const dv = result.van.dai_van_hien_tai;
  const dvPalace = dv ? result.palaces.find((p) => p.cung_so === dv.cung_so) : null;
  return {
    dai_van: dvPalace?.cung,
    luu_nien_dai_van: row.luu_nien_dai_van?.cung,
    tieu_van: row.tieu_van?.cung,
    luu_nien_nam: row.luu_nien_nam?.cung,
    luu_nguyet: han.luu_nguyet?.cung_ten,
    luu_nhat: han.luu_nhat?.cung_ten,
    luu_thoi: han.luu_thoi?.cung_ten,
  };
}

export function renderSummary(result) {
  const s = result.summary;
  const items = [
    ["Họ tên", s.ten],
    ["Năm sinh (Can Chi)", s.can_chi_nam],
    ["Bản mệnh", s.ban_menh],
    ["Cục", s.ten_cuc],
    ["Mệnh chủ / Thân chủ", `${s.menh_chu} / ${s.than_chu}`],
    ["Âm dương · Ngũ hành", `${s.am_duong_menh} · ${s.sinh_khac}`],
    ["Cung Mệnh", s.cung_menh],
    ["Cung Thân", s.cung_than],
    ["Số sao · Cách Cục", `${s.so_sao} sao · ${s.so_cach_cuc} Cách Cục`],
    ["Lịch", result.chart.input?.lich || ""],
  ];
  return `<h2>Tóm tắt lá số</h2><div class="summary">${items
    .map(([k, v]) => `<div><span>${esc(k)}</span><b>${esc(v || "—")}</b></div>`).join("")}</div>`;
}

/** Dải vận hạn đặt ngay trên bàn số: tên cung đang chịu từng lớp hạn. */
export function renderHanStrip(result) {
  const v = result.van || {};
  const h = result.han || {};
  const year = result.chart.viewing?.year;
  const row = (v.rows || []).find((r) => r.nam === year) || {};
  const dv = v.dai_van_hien_tai;
  const dvName = dv ? (dv.cung || palaceNameBySo(result, dv.cung_so)) : null;
  const items = [
    ["ĐV", dvName, dv ? `${dv.tuoi_bat_dau}–${dv.tuoi_ket_thuc}` : ""],
    ["LNĐV", row.luu_nien_dai_van?.cung],
    ["TV", row.tieu_van?.cung],
    ["LN", row.luu_nien_nam?.cung],
    ["LNg", h.luu_nguyet?.cung_ten, h.luu_nguyet ? `tháng ${h.luu_nguyet.thang_am}` : ""],
    ["LNh", h.luu_nhat?.cung_ten, h.luu_nhat ? `ngày ${h.luu_nhat.ngay_am}` : ""],
    ["LT", h.luu_thoi?.cung_ten, h.luu_thoi?.gio ? `giờ ${h.luu_thoi.gio}` : ""],
  ];
  const view = result.chart.viewing || {};
  return `<div class="han-strip">
      <div class="han-head">Vận hạn năm ${esc(year)} · ${esc(view.day ?? "")}/${esc(view.month ?? "")}</div>
      <div class="han-chips">${items.map(([k, name, sub]) =>
        `<span class="han-chip" title="${esc(TAG_TITLE[k] || k)}"><b>${esc(k)}</b> ${esc(name || "—")}${sub ? ` <small>${esc(sub)}</small>` : ""}</span>`).join("")}</div>
    </div>`;
}

/** Dải liệt kê rõ ràng: 12 tháng âm (Lưu nguyệt) và các ngày âm của tháng xem (Lưu nhật). */
export function renderLuuDai(result) {
  const h = result.han || {};
  if (!h.luu_nguyet) return "";
  const ln = h.luu_nguyet;
  const months = ln.bang.map((r) => `
      <div class="luu-chip ${r.thang_am === ln.thang_am ? "cur" : ""}">
        <b>Tháng ${r.thang_am}</b><span>${esc(r.cung_ten)} · ${esc(r.dia_chi)}</span>
      </div>`).join("");
  const days = (h.luu_nhat?.bang || []).map((r) => `
      <span class="day-chip ${r.ngay_am === h.luu_nhat.ngay_am ? "cur" : ""}" title="${esc(r.duong)} · ${esc(r.cung_ten)}">${r.ngay_am}</span>`).join("");
  return `<div class="luu-dai">
      <div class="han-head">Lưu nguyệt · 12 tháng âm ${esc(ln.nam_am)} (tô sáng: tháng đang xem)</div>
      <div class="luu-grid">${months}</div>
      <div class="han-head" style="margin-top:8px">Lưu nhật · ngày âm ${esc(h.luu_nhat?.ngay_am)} của tháng ${esc(ln.thang_am)} (tô sáng: ngày đang xem)</div>
      <div class="day-grid">${days}</div>
    </div>`;
}

const TAG_TITLE = {
  ĐV: "Đại vận", LNĐV: "Lưu niên Đại vận", TV: "Tiểu vận", LN: "Lưu niên năm",
  LNg: "Lưu nguyệt", LNh: "Lưu nhật", LT: "Lưu thời",
};

/** Gom Lưu nguyệt (tháng âm), Lưu nhật (ngày âm), Lưu thời (giờ) theo tên cung để gắn lên từng ô. */
export function luuMarksByCung(result) {
  const h = result.han || {};
  const marks = {};
  const put = (cung, kind, item) => {
    if (!cung) return;
    (marks[cung] ||= { thang: [], ngay: [], gio: [] })[kind].push(item);
  };
  (h.luu_nguyet?.bang || []).forEach((r) => put(r.cung_ten, "thang", { n: r.thang_am, cur: r.thang_am === h.luu_nguyet.thang_am }));
  (h.luu_nhat?.bang || []).forEach((r) => put(r.cung_ten, "ngay", { n: r.ngay_am, cur: r.ngay_am === h.luu_nhat.ngay_am }));
  (h.luu_thoi?.bang || []).forEach((r) => put(r.cung_ten, "gio", { n: r.gio, cur: r.gio_so === h.luu_thoi.gio_so }));
  return marks;
}

function luuLine(m) {
  if (!m) return "";
  const part = (label, items, fmt) => items.length
    ? `<span>${label} ${items.map((i) => `<b class="${i.cur ? "cur" : ""}">${esc(fmt(i))}</b>`).join(" ")}</span>` : "";
  return `<div class="luu-line">${part("T", m.thang, (i) => i.n)}${part("N", m.ngay, (i) => i.n)}${part("G", m.gio, (i) => i.n)}</div>`;
}

export function renderBoard(result, selected) {
  const tags = hanTags(result);
  const marks = luuMarksByCung(result);
  const cells = result.palaces.map((p) => {
    const row = p.vi_tri?.row ?? 1;
    const col = p.vi_tri?.column ?? 1;
    const badges = [
      p.than_cu ? `<span class="badge than">Thân</span>` : "",
      p.tuan ? `<span class="badge tuan">Tuần</span>` : "",
      p.triet ? `<span class="badge triet">Triệt</span>` : "",
    ].join("");
    const hanBadges = Object.entries(tags)
      .filter(([, cung]) => cung === p.cung)
      .map(([key]) => `<span class="badge han" title="${esc(TAG[key].title)}">${esc(TAG[key].abbr)}</span>`)
      .join("");
    const main = p.chinh_tinh.map((s) => `<div class="main-stars">${esc(s.ten)} ${dacLabel(s)}</div>`).join("");
    const tot = p.phu_tinh.filter((s) => s.kind !== "hung");
    const hung = p.phu_tinh.filter((s) => s.kind === "hung");
    const starCols = `<div class="star-cols">
        <div class="col-tot">${tot.map((s) => `<div>${esc(s.ten)}</div>`).join("")}</div>
        <div class="col-hung">${hung.map((s) => `<div>${esc(s.ten)}</div>`).join("")}</div>
      </div>`;
    const dvRange = p.dai_van != null ? `${p.dai_van}–${p.dai_van + 9}` : "";
    const elClass = ELEMENT_CLASS[p.ngu_hanh] || "";
    return `
      <div class="cell ${p.cung === selected ? "selected" : ""} ${p.cung === "Mệnh" ? "menh" : ""}"
           style="grid-row:${row};grid-column:${col}" role="button" tabindex="0" data-cung="${esc(p.cung)}"
           aria-label="Cung ${esc(p.cung)}">
        <div class="cell-head"><span class="cell-name ${elClass}">${esc(p.cung)}</span><span class="cell-chi">${esc(p.can_chi)}</span></div>
        <div class="badges">${badges}${hanBadges}</div>
        ${main}
        ${starCols}
        ${luuLine(marks[p.cung])}
        <div class="cell-foot"><span>${esc(p.ngu_hanh)} · ${esc(p.trang_sinh || "")}</span><span>${dvRange}</span></div>
      </div>`;
  }).join("");
  const t = result.summary;
  const h = result.han || {};
  const ln = h.luu_nguyet, lnh = h.luu_nhat, lt = h.luu_thoi;
  const at = (x) => (x ? esc(x) : "—");
  const center = `<div class="center">
      <div class="big">${esc(t.ten || "Lá số")}</div>
      <div class="sub">${esc(t.can_chi_nam)} · ${esc(t.ten_cuc)}</div>
      <div class="sub">${esc(result.chart.input?.lich || "")} · ${esc(result.chart.input?.gioi_tinh || "")}</div>
      <div class="center-luu">
        <div><span>Tháng</span><b>${esc(ln?.thang_am ?? "")}</b>${at(ln?.cung_ten)}</div>
        <div><span>Ngày</span><b>${esc(lnh?.ngay_am ?? "")}</b>${at(lnh?.cung_ten)}</div>
        <div><span>Giờ</span><b>${esc(lt?.gio || "")}</b>${at(lt?.cung_ten)}</div>
      </div>
      <div class="sub">Xem ${esc(lnh?.duong || "")}</div>
      <div class="legend">T tháng · N ngày · G giờ (Lưu)</div>
    </div>`;
  return cells + center;
}

export function renderPalaceDetail(result, cungName) {
  const p = palaceByName(result, cungName);
  if (!p) return `<div class="empty">Chọn một cung.</div>`;
  const rel = result.relations[cungName] || {};
  const relGroup = (title, list) => (list && list.length
    ? `<div class="rel-group"><h3>${esc(title)}</h3>${list.map((r) => `
        <div class="rel-item"><b>${esc(r.cung)}</b> <small>${esc(r.dia_chi)} · ${esc(r.can_chi)} · ${esc(r.ngu_hanh)}</small>
        <div class="small">${r.chinh_tinh.length ? esc(r.chinh_tinh.join(", ")) : "<span class='muted'>Không có chính tinh</span>"}</div></div>`).join("")}</div>`
    : "");
  const tags = hanTags(result);
  const hanNames = Object.entries(tags).filter(([, c]) => c === cungName).map(([k]) => TAG[k].title);
  const dvRange = p.dai_van != null ? `${p.dai_van}–${p.dai_van + 9} tuổi` : "—";
  return `
    <h2>Cung ${esc(p.cung)} · ${esc(p.can_chi)}</h2>
    <div class="detail-grid">
      <div class="kv">Địa chi: <b>${esc(p.dia_chi)}</b></div>
      <div class="kv">Ngũ hành: <b class="${ELEMENT_CLASS[p.ngu_hanh] || ""}">${esc(p.ngu_hanh)}</b></div>
      <div class="kv">Âm dương: <b>${esc(p.am_duong)}</b></div>
      <div class="kv">Tràng sinh: <b>${esc(p.trang_sinh || "—")}</b></div>
      <div class="kv">Đại vận: <b>${esc(dvRange)}</b></div>
      <div class="kv">Tiểu vận (Chi): <b>${esc(p.tieu_van_chi || "—")}</b></div>
      <div class="kv">Thân cư: <b>${p.than_cu ? "Có" : "Không"}</b> · Tuần: <b>${p.tuan ? "Có" : "Không"}</b> · Triệt: <b>${p.triet ? "Có" : "Không"}</b></div>
      <div class="kv">Đang hạn năm xem: <b>${esc(hanNames.join(", ") || "—")}</b></div>
    </div>
    <h3>Chính tinh</h3>
    ${p.chinh_tinh.length ? p.chinh_tinh.map((s) => `<div class="rel-item"><b>${esc(s.ten)}</b> ${dacLabel(s)} <small>${esc(s.ngu_hanh)}</small></div>`).join("") : "<div class='muted small'>Không có</div>"}
    <h3>Sao tốt</h3>
    <div class="small">${p.phu_tinh.filter((s) => s.kind !== "hung").map((s) => `${esc(s.ten)}${s.dac_tinh ? ` (${esc(s.dac_tinh)})` : ""}`).join(" · ") || "Không có"}</div>
    <h3>Hung tinh</h3>
    <div class="small">${p.phu_tinh.filter((s) => s.kind === "hung").map((s) => esc(s.ten)).join(" · ") || "Không có"}</div>
    <h3>Quan hệ cung (suy từ Địa Chi)</h3>
    ${relGroup("Tam Hợp", rel.tam_hop)}${relGroup("Xung Chiếu", rel.xung_chieu)}${relGroup("Nhị Hợp", rel.nhi_hop)}${relGroup("Giáp Cung", rel.giap_cung)}
  `;
}

export function renderHanCards(result) {
  const v = result.van;
  const h = result.han || {};
  const year = result.chart.viewing?.year;
  const row = (v.rows || []).find((r) => r.nam === year) || {};
  const dv = v.dai_van_hien_tai;
  const card = (label, main, sub = "") => `<div class="han-item"><span>${esc(label)}</span><b>${esc(main || "—")}</b>${sub ? `<div class="sub">${esc(sub)}</div>` : ""}</div>`;
  const dq = h.dau_quan;
  const ln = h.luu_nguyet;
  const lh = h.luu_nhat;
  const lt = h.luu_thoi;
  const view = result.chart.viewing || {};
  const hasLunar = !!ln;
  return `
    <h2>Hạn tại thời điểm xem</h2>
    <div class="small muted" style="margin-bottom:8px">Dương lịch ${esc(view.day ?? "—")}/${esc(view.month ?? "—")}/${esc(year)} · tuổi ${esc(v.tuoi ?? "—")}${hasLunar ? ` · âm lịch ${esc(lh.ngay_am)}/${esc(ln.thang_am)}/${esc(ln.nam_am)}` : ""}</div>
    <div class="han-cards">
      ${card("Đại vận", dv ? (dv.cung || palaceNameBySo(result, dv.cung_so)) : "—", dv ? `${dv.tuoi_bat_dau}–${dv.tuoi_ket_thuc} tuổi · ${v.huong_vong_van || ""}` : "")}
      ${card("Lưu niên Đại vận", row.luu_nien_dai_van?.cung, "Theo Đại vận hiện tại")}
      ${card("Tiểu vận", row.tieu_van?.cung, "Theo Chi năm xem")}
      ${card("Lưu niên năm", row.luu_nien_nam?.cung, row.luu_nien_nam?.can_chi ? `Năm ${row.luu_nien_nam.can_chi}` : "")}
      ${card("Đấu quân", dq?.cung_ten, dq ? `Tháng Giêng âm ${dq.nam_am} · ${dq.dia_chi}` : "")}
      ${card("Lưu nguyệt", ln?.cung_ten, ln ? `Tháng âm ${ln.thang_am} · ${ln.dia_chi}` : "")}
      ${card("Lưu nhật", lh?.cung_ten, lh ? `Ngày âm ${lh.ngay_am} · ${lh.dia_chi}` : "")}
      ${card("Lưu thời", lt?.cung_ten, lt?.gio ? `Giờ ${lt.gio}` : "Chọn giờ xem để xác định")}
    </div>`;
}

export function renderLuuBang(result) {
  const h = result.han || {};
  if (!h.luu_nguyet) return `<div class="card empty">Chọn ngày xem để xem bảng Lưu nguyệt, Lưu nhật, Lưu thời.</div>`;
  const ln = h.luu_nguyet, lh = h.luu_nhat, lt = h.luu_thoi;
  const tbl = (head, rows) => `<table><thead><tr>${head.map((x) => `<th>${esc(x)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table>`;
  const thang = tbl(["Tháng âm", "Cung", "Địa Chi"], ln.bang.map((r) =>
    `<tr class="${r.thang_am === ln.thang_am ? "current" : ""}"><td>${r.thang_am}</td><td>${esc(r.cung_ten)}</td><td>${esc(r.dia_chi)}</td></tr>`).join(""));
  const ngay = tbl(["Ngày âm", "Dương lịch", "Cung"], lh.bang.map((r) =>
    `<tr class="${r.ngay_am === lh.ngay_am ? "current" : ""}"><td>${r.ngay_am}</td><td>${esc(r.duong)}</td><td>${esc(r.cung_ten)}</td></tr>`).join(""));
  const gio = tbl(["Giờ", "Cung"], lt.bang.map((r) =>
    `<tr class="${r.gio_so === lt.gio_so ? "current" : ""}"><td>${esc(r.gio)}</td><td>${esc(r.cung_ten)}</td></tr>`).join(""));
  return `<div class="card table-card"><h2>Lưu nguyệt · 12 tháng âm ${esc(ln.nam_am)}</h2>${thang}
      <p class="hint">${esc(ln.phuong_phap)}</p></div>
    <div class="card table-card"><h2>Lưu nhật · ${esc(lh.so_ngay_trong_thang)} ngày tháng ${esc(lh.thang_am)}</h2>${ngay}
      <p class="hint">${esc(lh.phuong_phap)}</p></div>
    <div class="card table-card"><h2>Lưu thời · ngày xem</h2>${gio}
      <p class="hint">${esc(lt.phuong_phap)}</p></div>`;
}

function palaceNameBySo(result, so) {
  return result.palaces.find((p) => p.cung_so === so)?.cung || "—";
}

export function renderVanTable(result) {
  const v = result.van;
  const year = result.chart.viewing?.year;
  const rows = (v.rows || []).map((r) => `
    <tr class="${r.nam === year ? "current" : ""}">
      <td>${esc(r.nam)}</td><td>${esc(r.tuoi)}</td>
      <td>${esc(r.luu_nien_dai_van?.cung || "—")}</td>
      <td>${esc(r.tieu_van?.cung || "—")}</td>
      <td>${esc(r.luu_nien_nam?.cung || "—")}<div class="small muted">${esc(r.luu_nien_nam?.can_chi || "")}</div></td>
    </tr>`).join("");
  return `<h2>Bảng 10 năm</h2>
    <table><thead><tr><th>Năm</th><th>Tuổi</th><th>Lưu niên Đại vận</th><th>Tiểu vận</th><th>Lưu niên năm</th></tr></thead>
    <tbody>${rows}</tbody></table>
    <p class="hint">Dòng được tô sáng là năm đang xem. Đại vận hiện tại: ${esc(v.dai_van_hien_tai ? (v.dai_van_hien_tai.cung || palaceNameBySo(result, v.dai_van_hien_tai.cung_so)) : "—")}.</p>`;
}

export function renderCach(result) {
  const items = result.cach_cuc.items || [];
  if (!items.length) return `<div class="card empty">Lá số này không khớp Cách Cục nào trong bộ rule của engine.</div>`;
  return items.map((it) => `
    <div class="card cach-item ${it.kind === "modifier" ? "modifier" : ""}">
      <h3>${esc(it.name)} <span class="badge">${it.kind === "modifier" ? "Phá/giảm cấp" : "Cách Cục"}</span></h3>
      <div class="small">${esc(it.description || "")}</div>
      ${it.interpretation ? `<p class="small">${esc(it.interpretation)}</p>` : ""}
      <div class="evidence">Bằng chứng: ${it.evidence.length ? esc(it.evidence.map((e) => (typeof e === "string" ? e : (e.cung || e.name || JSON.stringify(e)))).join(" · ")) : "—"}</div>
      <div class="evidence">Mã rule: ${esc(it.rule_id)}</div>
    </div>`).join("");
}

export function renderSao(result, query) {
  const q = (query || "").trim().toLowerCase();
  const list = result.sao.filter((s) => !q || s.ten.toLowerCase().includes(q));
  if (!list.length) return `<div class="card empty">Không có sao khớp “${esc(query)}”.</div>`;
  return list.map((s) => `
    <div class="star-row" data-star="${esc(s.ten)}">
      <div class="top"><b>${esc(s.ten)}</b><span class="small muted">${esc(s.nhom)} · ${esc(s.ngu_hanh)} · ${s.cung.length} cung</span></div>
      <div class="cungs">${s.cung.map((c) => `${esc(c.cung)} (${esc(c.dia_chi)})${c.dac_tinh ? ` · ${esc(c.dac_tinh)}` : ""}`).join("<br>")}
        ${s.phuong_vi ? `<br><span class="muted">Phương vị: ${esc(s.phuong_vi)}</span>` : ""}</div>
    </div>`).join("");
}

export function renderProfiles(profiles) {
  if (!profiles.length) return `<div class="card empty">Chưa có hồ sơ nào. Lập lá số rồi bấm <b>Lưu hồ sơ</b>.</div>`;
  return profiles.map((p, i) => `
    <div class="card profile">
      <div><b>${esc(p.label)}</b><div class="meta">${esc(p.summary)}</div></div>
      <div class="actions">
        <button class="btn small-btn" data-open="${i}">Mở</button>
        <button class="btn small-btn danger" data-del="${i}">Xóa</button>
      </div>
    </div>`).join("");
}
