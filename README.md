# Tử Vi Đẩu Số — App Android (APK)

Ứng dụng lập lá số Tử Vi và luận hạn, chạy **offline** trên điện thoại Android.

- **An sao**: dùng nguyên engine Python của repo
  [suneJQK/luangiaibysun](https://github.com/suneJQK/luangiaibysun) (109 sao, Cách Cục, Đại vận / Tiểu vận / Lưu niên).
  Engine chạy ngay trong ứng dụng qua [Pyodide](https://pyodide.org) (Python WebAssembly), không cần server.
- **Vỏ app**: giao diện HTML/JS trong `web/`, đóng gói bằng [Capacitor](https://capacitorjs.com) thành APK.

## Tính năng

| Tab | Nội dung |
|---|---|
| Lá số | Form nhập (dương/âm lịch, giờ sinh, giới tính, múi giờ), tóm tắt, bàn số 12 cung 4×4, chạm cung để xem sao, đặc tính Miếu/Vượng/Đắc/Bình/Hãm, Thân/Tuần/Triệt, quan hệ cung (Tam Hợp, Xung Chiếu, Nhị Hợp, Giáp Cung) |
| Vận hạn | Chọn **ngày xem** (và giờ xem) → hạn tại thời điểm đó: Đại vận, Lưu niên Đại vận, Tiểu vận, Lưu niên năm, **Lưu nguyệt (tháng)**, **Lưu nhật (ngày)**, **Lưu thời (giờ)**; bảng 10 năm, dòng năm xem được tô sáng |
| Cách cục | Cách Cục khớp lá số kèm bằng chứng (cung/Địa Chi) và các modifier phá/giảm cấp |
| Danh bạ sao | Tất cả sao trên lá số, tìm kiếm, xem sao ở cung nào |
| Hồ sơ | Lưu / mở / xóa lá số đã lập (lưu trên máy) |

Bàn số có nhãn hạn trên từng cung: ĐV, LNĐV, TV, LN, LNg (lưu nguyệt), LNh (lưu nhật), LT (lưu thời).

### Ghi chú về lớp hạn
- **Lưu nguyệt**: tháng xác định theo tiết khí (Solar Longitude), cung là cung có Địa Chi của tháng đó; đúng theo `calculate_van_layers` của engine gốc. Nếu ngày xem sát giao tiết khí, engine sẽ cảnh báo cần giờ/phút.
- **Lưu nhật**: Can Chi của ngày xem (Julian Day), cung tương ứng trên lá số.
- **Lưu thời**: Can Chi giờ từ Can ngày + Chi giờ xem.

### Chưa có trong APK
Luận giải bằng AI (cần API key và server), kiểm toán dữ liệu, so sánh hai lá số, xuất file. Các phần này nằm trong repo gốc luangiaibysun.

## Cấu trúc

```
engine/            Engine an sao (sao chép từ luangiaibysun, xem engine/SOURCE.md)
  app_bridge.py    Cầu nối: gom pipeline lập lá số + vận hạn thành một hàm (không cần pydantic/FastAPI)
web/               Giao diện (index.html, css, js)
scripts/build-www.mjs   Gom web + engine + runtime Pyodide vào www/
tests/             Kiểm thử engine thật qua Pyodide + kiểm thử render
android/           Android project (Capacitor)
capacitor.config.json
.github/workflows/android-apk.yml   Build APK trên GitHub Actions
```

## Chạy thử trên máy (trình duyệt)

```bash
npm install
npm run build:www
python3 -m http.server 8080 --directory www   # mở http://localhost:8080
```

## Kiểm thử

```bash
npm test
```

## Build APK

**Cách 1 — GitHub Actions (khuyến nghị):** mỗi lần push, workflow `Build Android APK` chạy `npm test`, đóng gói, rồi build APK debug. Tải file `tuvi-debug-apk` trong tab Actions → artifact.

**Cách 2 — Máy có Android Studio:**

```bash
npm install
npm run android:sync
npm run android:open     # rồi Build > Build APK(s)
```

Yêu cầu Android 7.0 trở lên (`minSdkVersion 24`), vì Pyodide cần WebAssembly và WebView hiện đại.

## Nguồn và giới hạn
- Engine an sao: `suneJQK/luangiaibysun` (commit `ef5d9bd`). Repo `luangiaibysun-clean` không truy cập được khi tích hợp nên dùng repo này.
- Lỗi đã biết của engine gốc và đã xử lý trong `app_bridge.py`: Lưu niên năm trả về cung rỗng (tra cung theo Chi kiểu số), và Lưu nguyệt/nhật/thời trả cung dạng số `cung_so` (được đổi sang tên cung).
- APK bản debug, chưa ký phát hành (release) và chưa đưa lên Google Play.
