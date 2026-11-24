// Điều khiển ứng dụng: form, nút chức năng, lưu hồ sơ, gọi engine Python (Pyodide).
import { createEngine } from "./engine.js";
import {
  CHI, GIO_LABEL, esc, renderBoard, renderCach, renderHanCards, renderPalaceDetail,
  renderLuuBang, renderProfiles, renderSao, renderSummary, renderVanTable,
} from "./render.js";

const $ = (sel) => document.querySelector(sel);
const KEY_PROFILES = "tuvi.profiles.v1";
const KEY_LAST = "tuvi.last.v1";

const state = {
  engine: null,
  birth: null,   // thông tin sinh
  view: null,    // ngày/giờ xem
  result: null,  // kết quả engine
  selected: "Mệnh",
};

// ------------------------------------------------------------ tiện ích

function toast(message, isError = false) {
  const el = $("#toast");
  el.textContent = message;
  el.className = `toast show${isError ? " error" : ""}`;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { el.className = "toast"; }, 2600);
}

function todayParts() {
  const d = new Date();
  return { y: d.getFullYear(), m: d.getMonth() + 1, d: d.getDate() };
}

const pad = (n) => String(n).padStart(2, "0");
const isoDate = (y, m, d) => `${y}-${pad(m)}-${pad(d)}`;

function fillGioSelects() {
  const gio = $("#f-gio");
  gio.innerHTML = CHI.map((c, i) => `<option value="${c}">${c} (${GIO_LABEL[i]})</option>`).join("");
  const gioXem = $("#v-gio");
  gioXem.innerHTML = `<option value="">Không xem giờ</option>` +
    CHI.map((c, i) => `<option value="${i + 1}">${c} (${GIO_LABEL[i]})</option>`).join("");
}

function readBirthForm() {
  const num = (id, label) => {
    const v = Number($(id).value);
    if (!Number.isInteger(v)) throw new Error(`${label} phải là số nguyên`);
    return v;
  };
  const tz = Number($("#f-tz").value);
  if (!Number.isFinite(tz)) throw new Error("Múi giờ không hợp lệ");
  return {
    ten: $("#f-ten").value.trim(),
    ngay: num("#f-ngay", "Ngày"),
    thang: num("#f-thang", "Tháng"),
    nam: num("#f-nam", "Năm"),
    gio_sinh: $("#f-gio").value,
    gioi_tinh: $("#f-gioi").value,
    duong_lich: $("#f-lich").value === "duong",
    time_zone: tz,
  };
}

function fillBirthForm(b) {
  $("#f-ten").value = b.ten || "";
  $("#f-ngay").value = b.ngay;
  $("#f-thang").value = b.thang;
  $("#f-nam").value = b.nam;
  $("#f-gio").value = b.gio_sinh;
  $("#f-gioi").value = b.gioi_tinh;
  $("#f-lich").value = b.duong_lich ? "duong" : "am";
  $("#f-tz").value = b.time_zone;
}

// ------------------------------------------------------------ tính toán

function compute(birth, view) {
  const payload = {
    ...birth,
    nam_xem: view.nam_xem,
    thang_xem: view.thang_xem,
    ngay_xem: view.ngay_xem,
    gio_xem: view.gio_xem || null,
  };
  const result = state.engine.tinhLaSo(payload);
  state.birth = birth;
  state.view = view;
  state.result = result;
  localStorage.setItem(KEY_LAST, JSON.stringify({ birth, view: { ...view, gio_xem: view.gio_xem || null } }));
  renderAll();
}

function renderAll() {
  const r = state.result;
  $("#la-so-empty").classList.toggle("hidden", !!r);
  if (!r) { $("#birth-bar").classList.add("hidden"); $("#form-birth").classList.remove("hidden"); }
  $("#la-so-result").classList.toggle("hidden", !r);
  $("#van-empty").classList.toggle("hidden", !!r);
  $("#van-result").classList.toggle("hidden", !r);
  $("#cach-empty").classList.toggle("hidden", !!r);
  $("#sao-empty").classList.toggle("hidden", !!r);
  $("#sao-result").classList.toggle("hidden", !r);
  $("#btn-save-bar").disabled = !r;
  $("#cach-result").innerHTML = r ? renderCach(r) : "";
  if (!r) return;

  $("#birth-text").textContent = `${state.birth.ten || "Không tên"} · ${pad(state.birth.ngay)}/${pad(state.birth.thang)}/${state.birth.nam} · ${state.birth.gioi_tinh} · giờ ${state.birth.gio_sinh}`;
  $("#birth-bar").classList.remove("hidden");
  $("#form-birth").classList.add("hidden");
  $("#board").innerHTML = renderBoard(r, state.selected);
  $("#palace-detail").innerHTML = renderPalaceDetail(r, state.selected);

  $("#v-date").value = isoDate(state.view.nam_xem, state.view.thang_xem, state.view.ngay_xem);
  $("#v-gio").value = state.view.gio_xem || "";
  $("#han-cards").innerHTML = renderHanCards(r);
  $("#van-table").innerHTML = renderVanTable(r);
  $("#luu-bang").innerHTML = renderLuuBang(r);

  $("#sao-list").innerHTML = renderSao(r, $("#sao-search").value);
}

function selectPalace(name) {
  state.selected = name;
  document.querySelectorAll("#board .cell").forEach((el) => {
    el.classList.toggle("selected", el.dataset.cung === name);
  });
  $("#palace-detail").innerHTML = renderPalaceDetail(state.result, name);
  $("#palace-wrap").open = true;
}

// ------------------------------------------------------------ hồ sơ

function loadProfiles() {
  try { return JSON.parse(localStorage.getItem(KEY_PROFILES) || "[]"); } catch { return []; }
}
function saveProfiles(list) { localStorage.setItem(KEY_PROFILES, JSON.stringify(list)); }

function profileLabel(b) {
  return `${b.ten || "Không tên"} · ${pad(b.ngay)}/${pad(b.thang)}/${b.nam} · ${b.duong_lich ? "DL" : "AL"}`;
}

function renderProfilesView() {
  const list = loadProfiles();
  $("#ho-so-list").innerHTML = renderProfiles(list.map((p) => ({
    label: p.label, summary: `${p.birth.gioi_tinh} · giờ ${p.birth.gio_sinh} · lưu ${new Date(p.savedAt).toLocaleDateString("vi-VN")}`,
  })));
}

// ------------------------------------------------------------ sự kiện

function bindEvents() {
  document.querySelectorAll(".fn").forEach((btn) => btn.addEventListener("click", () => {
    document.querySelectorAll(".fn").forEach((b) => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === btn.dataset.view));
    window.scrollTo({ top: 0 });
    if (btn.dataset.view === "view-ho-so") renderProfilesView();
  }));

  $("#btn-edit").addEventListener("click", () => {
    $("#form-birth").classList.remove("hidden");
    $("#birth-bar").classList.add("hidden");
  });

  $("#form-birth").addEventListener("submit", (ev) => {
    ev.preventDefault();
    try {
      const birth = readBirthForm();
      const t = todayParts();
      state.selected = "Mệnh";
      compute(birth, { nam_xem: t.y, thang_xem: t.m, ngay_xem: t.d, gio_xem: null });
      toast("Đã lập lá số");
    } catch (err) {
      toast(err.message, true);
    }
  });

  $("#btn-save-bar").addEventListener("click", () => {
    if (!state.birth) return;
    const list = loadProfiles();
    const key = JSON.stringify(state.birth);
    const next = list.filter((p) => JSON.stringify(p.birth) !== key);
    next.unshift({ label: profileLabel(state.birth), birth: state.birth, savedAt: Date.now() });
    saveProfiles(next.slice(0, 50));
    toast("Đã lưu hồ sơ");
  });

  $("#form-view").addEventListener("submit", (ev) => {
    ev.preventDefault();
    try {
      const [y, m, d] = $("#v-date").value.split("-").map(Number);
      if (!y || !m || !d) throw new Error("Ngày xem không hợp lệ");
      const gio = $("#v-gio").value ? Number($("#v-gio").value) : null;
      compute(state.birth, { nam_xem: y, thang_xem: m, ngay_xem: d, gio_xem: gio });
      toast("Đã tính hạn theo ngày xem");
    } catch (err) {
      toast(err.message, true);
    }
  });

  $("#btn-today").addEventListener("click", () => {
    if (!state.birth) return;
    const t = todayParts();
    compute(state.birth, { nam_xem: t.y, thang_xem: t.m, ngay_xem: t.d, gio_xem: state.view?.gio_xem || null });
  });

  $("#board").addEventListener("click", (ev) => {
    const cell = ev.target.closest(".cell");
    if (cell) selectPalace(cell.dataset.cung);
  });
  $("#board").addEventListener("keydown", (ev) => {
    if (ev.key !== "Enter" && ev.key !== " ") return;
    const cell = ev.target.closest(".cell");
    if (cell) { ev.preventDefault(); selectPalace(cell.dataset.cung); }
  });

  $("#sao-search").addEventListener("input", () => {
    if (state.result) $("#sao-list").innerHTML = renderSao(state.result, $("#sao-search").value);
  });
  $("#sao-list").addEventListener("click", (ev) => {
    const row = ev.target.closest(".star-row");
    if (row) row.classList.toggle("open");
  });

  $("#ho-so-list").addEventListener("click", (ev) => {
    const list = loadProfiles();
    const openBtn = ev.target.closest("[data-open]");
    const delBtn = ev.target.closest("[data-del]");
    if (openBtn) {
      const p = list[Number(openBtn.dataset.open)];
      fillBirthForm(p.birth);
      document.querySelector('.fn[data-view="view-la-so"]').click();
      try {
        const t = todayParts();
        state.selected = "Mệnh";
        compute(p.birth, { nam_xem: t.y, thang_xem: t.m, ngay_xem: t.d, gio_xem: null });
      } catch (err) { toast(err.message, true); }
    }
    if (delBtn) {
      list.splice(Number(delBtn.dataset.del), 1);
      saveProfiles(list);
      renderProfilesView();
      toast("Đã xóa hồ sơ");
    }
  });
}

// ------------------------------------------------------------ khởi động

async function boot() {
  fillGioSelects();
  bindEvents();
  const t = todayParts();
  $("#f-nam").value = 1990;
  $("#f-ngay").value = 15;
  $("#f-thang").value = 8;
  $("#f-gio").value = "Ngọ";

  try {
    const last = JSON.parse(localStorage.getItem(KEY_LAST) || "null");
    if (last?.birth) fillBirthForm(last.birth);
  } catch { /* bỏ qua */ }

  const status = (text) => { $("#engine-status").textContent = text; $("#engine-status").className = "status"; };
  try {
    const [loadPyodide, bundle] = await Promise.all([
      waitForPyodide(),
      fetch("py/bundle.json").then((r) => { if (!r.ok) throw new Error("Không đọc được engine"); return r.json(); }),
    ]);
    state.engine = await createEngine({ loadPyodide, indexURL: "pyodide/", bundle, onStatus: status });
    status("Sẵn sàng · engine an sao offline");
    const last = JSON.parse(localStorage.getItem(KEY_LAST) || "null");
    if (last?.birth) {
      fillBirthForm(last.birth);
      compute(last.birth, { ...last.view, gio_xem: last.view.gio_xem || null });
      toast("Đã mở lá số gần nhất");
    }
  } catch (err) {
    console.error(err);
    status("Lỗi nạp engine");
    $("#engine-status").classList.add("error");
    toast(`Không khởi động được engine: ${err.message}`, true);
  }
  $("#v-date").value = isoDate(t.y, t.m, t.d);
}

function waitForPyodide() {
  return new Promise((resolve, reject) => {
    const started = Date.now();
    const tick = () => {
      if (typeof window.loadPyodide === "function") return resolve(window.loadPyodide);
      if (Date.now() - started > 15000) return reject(new Error("pyodide.js chưa tải xong"));
      setTimeout(tick, 50);
    };
    tick();
  });
}

boot();
