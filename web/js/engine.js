// Nạp engine an sao Python (tuvi_engine) vào trình duyệt / WebView bằng Pyodide.
// Engine chạy hoàn toàn trên máy: không cần server, không cần internet sau khi cài APK.

/**
 * @param {object} opts
 * @param {Function} opts.loadPyodide  hàm loadPyodide (global từ pyodide.js, hoặc import trong test)
 * @param {string}   opts.indexURL     thư mục chứa runtime Pyodide (có đuôi /)
 * @param {object}   opts.bundle       { "tuvi_engine/...py": "<nội dung>", ... }
 * @param {Function} [opts.onStatus]   callback(text) hiển thị tiến trình
 * @returns {Promise<{tinhLaSo: (payload: object) => object}>}
 */
export async function createEngine({ loadPyodide, indexURL, bundle, onStatus = () => {} }) {
  onStatus("Đang nạp bộ chạy Python…");
  const py = await loadPyodide({ indexURL });

  onStatus("Đang nạp engine an sao…");
  const root = "/app";
  py.FS.mkdirTree(root);
  for (const [path, content] of Object.entries(bundle)) {
    const full = `${root}/${path}`;
    const dir = full.slice(0, full.lastIndexOf("/"));
    py.FS.mkdirTree(dir);
    py.FS.writeFile(full, content);
  }
  py.runPython(`import sys\nif '${root}' not in sys.path:\n    sys.path.insert(0, '${root}')`);
  const bridge = py.pyimport("app_bridge");

  return {
    /** Lập lá số + vận hạn cho ngày xem. Ném Error nếu engine báo lỗi đầu vào. */
    tinhLaSo(payload) {
      const data = JSON.parse(bridge.tinh_la_so(JSON.stringify(payload)));
      if (data.error) throw new Error(data.error);
      return data;
    },
  };
}
