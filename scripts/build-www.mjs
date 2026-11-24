// Gom web/ + engine Python + runtime Pyodide vào thư mục www/ (webDir của Capacitor).
// Chạy: npm run build:www
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const out = join(root, "www");
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

// 1) Giao diện
cpSync(join(root, "web"), out, { recursive: true });

// 2) Runtime Pyodide (chỉ các file cần thiết để chạy Python stdlib)
const pyodideDir = join(root, "node_modules", "pyodide");
const pyodideOut = join(out, "pyodide");
mkdirSync(pyodideOut, { recursive: true });
for (const f of ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "pyodide-lock.json", "python_stdlib.zip"]) {
  const src = join(pyodideDir, f);
  if (!existsSync(src)) throw new Error(`Thiếu ${src} — chạy npm install trước`);
  cpSync(src, join(pyodideOut, f));
}

// 3) Engine Python -> bundle JSON (path tương đối -> nội dung)
const engineDir = join(root, "engine");
const bundle = {};
const walk = (dir) => {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      if (name === "__pycache__") continue;
      walk(full);
    } else if (/\.(py|json)$/.test(name)) {
      bundle[relative(engineDir, full).split("\\").join("/")] = readFileSync(full, "utf8");
    }
  }
};
walk(engineDir);
mkdirSync(join(out, "py"), { recursive: true });
writeFileSync(join(out, "py", "bundle.json"), JSON.stringify(bundle));
console.log(`www/ đã sẵn sàng: ${Object.keys(bundle).length} file engine`);
