# Nguồn engine an sao

Các file trong thư mục này được sao chép nguyên văn từ repo
[suneJQK/luangiaibysun](https://github.com/suneJQK/luangiaibysun) (commit `ef5d9bd`):

- `tuvi_engine/`, `data/`, `tu_vi_calculator.py`, `chart_sanitizer.py`, `tuvi_lap_so_engine.py`
  — logic an sao, Đại vận / Tiểu vận / Lưu niên / **Lưu nguyệt / Lưu nhật / Lưu thời** (không sửa).

File do app này thêm vào:

- `app_bridge.py` — gom pipeline của `core/service.py` (lập lá số → phân tích Cách Cục →
  chuẩn hóa → tính vận hạn → danh bạ sao, quan hệ cung) thành một hàm thuần Python, không
  phụ thuộc pydantic/FastAPI, để chạy được trong Pyodide (WebAssembly) trên điện thoại.

Repo gốc `luangiaibysun-clean` không truy cập được tại thời điểm tích hợp, nên dùng `luangiaibysun`.
