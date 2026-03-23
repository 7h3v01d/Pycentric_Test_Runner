"""
╔══════════════════════════════════════════════════════════╗
║          PyCentric Test Runner  —  GUI Edition           ║
║   Auto-discovers & runs pytest / unittest on any folder  ║
╚══════════════════════════════════════════════════════════╝

Requirements:
    pip install PyQt5

Usage:
    python test_runner_gui.py
"""

import os
import sys
import re
import ast
import time
import queue
import shlex
import signal
import threading
import subprocess
import datetime
from pathlib import Path

from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings,
)
from PyQt5.QtGui import (
    QColor, QTextCursor,
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit, QPlainTextEdit,
    QPushButton, QLabel, QLineEdit, QFileDialog, QComboBox,
    QCheckBox, QGroupBox, QStatusBar, QTabWidget, QProgressBar,
    QFrame, QMenuBar,
    QMessageBox, QHeaderView, QMenu,
)


# ─────────────────────────────────────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────────────────────────────────────

DARK_BG       = "#0f1117"
PANEL_BG      = "#161b22"
BORDER        = "#30363d"
TEXT_PRIMARY  = "#e6edf3"
TEXT_MUTED    = "#8b949e"
ACCENT_BLUE   = "#58a6ff"
ACCENT_GREEN  = "#3fb950"
ACCENT_RED    = "#f85149"
ACCENT_YELLOW = "#d29922"
ACCENT_PURPLE = "#bc8cff"
ACCENT_CYAN   = "#39d353"
BTN_PRIMARY   = "#238636"
BTN_DANGER    = "#da3633"
BTN_SECONDARY = "#21262d"

STYLE = f"""
QMainWindow, QWidget {{
    background: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Text', sans-serif;
    font-size: 13px;
}}
QMenuBar {{
    background: {PANEL_BG};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {BORDER};
    padding: 2px;
}}
QMenuBar::item:selected {{ background: {BORDER}; border-radius: 4px; }}
QMenu {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
}}
QMenu::item:selected {{ background: {ACCENT_BLUE}; color: #fff; }}
QSplitter::handle {{ background: {BORDER}; width: 2px; height: 2px; }}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
QPushButton {{
    background: {BTN_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{ background: #30363d; border-color: {ACCENT_BLUE}; }}
QPushButton:pressed {{ background: {DARK_BG}; }}
QPushButton:disabled {{ color: {TEXT_MUTED}; }}
QPushButton#btnRun {{
    background: {BTN_PRIMARY};
    border-color: #2ea043;
    font-weight: 700;
    padding: 8px 20px;
}}
QPushButton#btnRun:hover {{ background: #2ea043; }}
QPushButton#btnRunSingle {{
    background: #1a3a5c;
    border-color: {ACCENT_BLUE};
    color: {ACCENT_BLUE};
    font-weight: 600;
    padding: 8px 16px;
}}
QPushButton#btnRunSingle:hover {{ background: #1d4775; }}
QPushButton#btnStop {{
    background: {BTN_DANGER};
    border-color: #b91c1c;
    font-weight: 700;
    padding: 8px 20px;
}}
QPushButton#btnStop:hover {{ background: #b91c1c; }}
QPushButton#btnSave {{
    background: #1f2937;
    border-color: {ACCENT_BLUE};
    color: {ACCENT_BLUE};
}}
QPushButton#btnSave:hover {{ background: #243447; }}
QLineEdit, QComboBox, QSpinBox {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 5px;
    color: {TEXT_PRIMARY};
    padding: 5px 8px;
    selection-background-color: {ACCENT_BLUE};
}}
QLineEdit:focus, QComboBox:focus {{ border-color: {ACCENT_BLUE}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT_BLUE};
}}
QCheckBox {{ color: {TEXT_MUTED}; spacing: 6px; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background: {PANEL_BG};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
}}
QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 0 0 6px 6px; }}
QTabBar::tab {{
    background: {PANEL_BG};
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 6px 16px;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
}}
QTabBar::tab:selected {{
    background: {DARK_BG};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {DARK_BG};
}}
QTabBar::tab:hover {{ color: {TEXT_PRIMARY}; }}
QTreeWidget {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    alternate-background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
}}
QTreeWidget::item {{ padding: 3px 4px; }}
QTreeWidget::item:selected {{ background: #1d3251; color: {TEXT_PRIMARY}; }}
QTreeWidget::item:hover {{ background: #21262d; }}
QHeaderView::section {{
    background: {PANEL_BG};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QPlainTextEdit, QTextEdit {{
    background: {DARK_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {TEXT_PRIMARY};
    font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: #264f78;
    padding: 6px;
}}
QProgressBar {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{ background: {ACCENT_BLUE}; border-radius: 4px; }}
QProgressBar[state="fail"]::chunk {{ background: {ACCENT_RED}; border-radius: 4px; }}
QProgressBar[state="pass"]::chunk {{ background: {ACCENT_GREEN}; border-radius: 4px; }}
QStatusBar {{
    background: {PANEL_BG};
    border-top: 1px solid {BORDER};
    color: {TEXT_MUTED};
    font-size: 11px;
    padding: 2px 8px;
}}
QScrollBar:vertical {{ background: {PANEL_BG}; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QFrame#separator {{ background: {BORDER}; max-height: 1px; }}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  ANSI → HTML
# ─────────────────────────────────────────────────────────────────────────────

ANSI_MAP = {
    "31": f"color:{ACCENT_RED}",
    "32": f"color:{ACCENT_GREEN}",
    "33": f"color:{ACCENT_YELLOW}",
    "34": f"color:{ACCENT_BLUE}",
    "35": f"color:{ACCENT_PURPLE}",
    "36": f"color:{ACCENT_CYAN}",
    "37": f"color:{TEXT_PRIMARY}",
    "90": f"color:{TEXT_MUTED}",
    "91": f"color:{ACCENT_RED}",
    "92": f"color:{ACCENT_GREEN}",
    "93": f"color:{ACCENT_YELLOW}",
    "1":  "font-weight:bold",
}


def ansi_to_html(text: str) -> str:
    text = (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
    result = []
    open_spans = 0
    i = 0
    while i < len(text):
        if text[i] == "\x1b" and i + 1 < len(text) and text[i + 1] == "[":
            end = text.find("m", i)
            if end == -1:
                result.append(text[i])
                i += 1
                continue
            codes = text[i + 2:end].split(";")
            i = end + 1
            styles = []
            for c in codes:
                if c == "0":
                    for _ in range(open_spans):
                        result.append("</span>")
                    open_spans = 0
                elif c in ANSI_MAP:
                    styles.append(ANSI_MAP[c])
            if styles:
                result.append(f'<span style="{";".join(styles)}">')
                open_spans += 1
        else:
            result.append(text[i])
            i += 1
    for _ in range(open_spans):
        result.append("</span>")
    return "".join(result)


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mKGHF]", "", text)


ROOT_MARKERS = (
    "pyproject.toml",
    "pytest.ini",
    "tox.ini",
    "setup.cfg",
    "setup.py",
    ".git",
)


def detect_project_root(folder: str) -> Path:
    current = Path(folder).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate
    return current


def _venv_candidates(base: Path):
    if os.name == "nt":
        names = [
            ".venv/Scripts/python.exe",
            "venv/Scripts/python.exe",
            "env/Scripts/python.exe",
        ]
    else:
        names = [
            ".venv/bin/python",
            "venv/bin/python",
            "env/bin/python",
        ]
    return [base / rel for rel in names]


def detect_project_python(folder: str, run_root: str | Path | None = None) -> Path:
    bases = []
    for value in (run_root, folder):
        if not value:
            continue
        p = Path(value).expanduser().resolve()
        if p not in bases:
            bases.append(p)
    for base in bases:
        for candidate in _venv_candidates(base):
            if candidate.exists() and candidate.is_file():
                return candidate
    return Path(sys.executable).resolve()


def build_unittest_id(test: dict, run_root: str | Path) -> str:
    file_path = Path(test["file_path"]).resolve()
    root = Path(run_root).resolve()
    try:
        rel = file_path.relative_to(root)
        module = ".".join(rel.with_suffix("").parts)
    except ValueError:
        module = file_path.stem

    if test.get("class_name"):
        return f"{module}.{test['class_name']}.{test['name']}"
    return f"{module}.{test['name']}"


# ─────────────────────────────────────────────────────────────────────────────
#  TEST DISCOVERY  (AST-based, no imports)
# ─────────────────────────────────────────────────────────────────────────────

def discover_tests(folder: str):
    """
    Walk folder, find test_*.py / *_test.py, parse with AST.
    Returns list of:
      { path, rel_path, tests: [{ name, kind, class_name, framework_hint, ... }] }
    """
    folder = Path(folder)
    seen, unique_files = set(), []
    for f in list(folder.rglob("test_*.py")) + list(folder.rglob("*_test.py")):
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    unique_files.sort()

    results = []
    for py_file in unique_files:
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError:
            continue

        rel = py_file.relative_to(folder)
        rel_posix = rel.as_posix()
        tests = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [
                    b.id if isinstance(b, ast.Name)
                    else b.attr if isinstance(b, ast.Attribute)
                    else ""
                    for b in node.bases
                ]
                is_unittest_class = any("TestCase" in base for base in bases)
                is_test = node.name.startswith("Test") or is_unittest_class

                if is_test:
                    framework_hint = "unittest" if is_unittest_class else "pytest"
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test"):
                            tests.append({
                                "name": item.name,
                                "kind": "method",
                                "class_name": node.name,
                                "framework_hint": framework_hint,
                                "file_path": str(py_file),
                                "rel_path": rel_posix,
                                "pytest_node_id": f"{rel_posix}::{node.name}::{item.name}",
                            })
            elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tests.append({
                    "name": node.name,
                    "kind": "function",
                    "class_name": None,
                    "framework_hint": "pytest",
                    "file_path": str(py_file),
                    "rel_path": rel_posix,
                    "pytest_node_id": f"{rel_posix}::{node.name}",
                })

        if tests:
            results.append({
                "path": str(py_file),
                "rel_path": str(rel),
                "tests": tests,
            })

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  NON-BLOCKING PIPE READER
#  A background thread drains stdout into a Queue so the main loop never
#  blocks — even if the subprocess crashes mid-write or hangs forever.
# ─────────────────────────────────────────────────────────────────────────────

_SENTINEL = object()


def _pipe_reader(stream, q: queue.Queue):
    try:
        for line in iter(stream.readline, ""):
            q.put(line)
    except Exception as exc:
        q.put(f"\x1b[31m[pipe error] {exc}\x1b[0m\n")
    finally:
        q.put(_SENTINEL)


# ─────────────────────────────────────────────────────────────────────────────
#  RUNNER THREAD
# ─────────────────────────────────────────────────────────────────────────────

class RunnerThread(QThread):
    # Emit a *batch* of lines as one string — far fewer cross-thread calls
    chunk_ready  = pyqtSignal(str)       # multiple raw lines joined
    test_result  = pyqtSignal(str, str)  # (node_id, STATUS)
    finished_run = pyqtSignal(dict)      # summary dict

    WATCHDOG_TIMEOUT = 120   # seconds of silence before forceful kill
    FLUSH_INTERVAL   = 0.033 # seconds between UI flushes (~30 fps)
    MAX_LINE_LEN     = 2000  # truncate runaway single lines
    MAX_TOTAL_LINES  = 5000  # after this many lines cap output (prevent OOM)

    def __init__(
        self,
        folder,
        framework,
        extra_args,
        node_spec=None,
        python_exe=None,
        work_dir=None,
    ):
        super().__init__()
        self.folder = str(Path(folder).resolve())
        self.framework = framework
        self.extra_args = extra_args
        self.node_spec = node_spec
        self.python_exe = str(Path(python_exe or sys.executable).resolve())
        self.work_dir = str(Path(work_dir or folder).resolve())
        self._proc = None
        self._abort = False
        self._recent_clean_lines = []
        self._issue_text = ""

    def stop(self):
        self._abort = True
        self._kill_proc()

    def _kill_proc(self):
        p = self._proc
        if p is None or p.poll() is not None:
            return
        try:
            if sys.platform != "win32":
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            else:
                p.terminate()
        except Exception:
            try:
                p.kill()
            except Exception:
                pass

    def _append_recent_line(self, line: str):
        clean = strip_ansi(line).rstrip()
        if not clean:
            return
        self._recent_clean_lines.append(clean)
        if len(self._recent_clean_lines) > 250:
            self._recent_clean_lines.pop(0)

    def _classify_issue(self, rc: int) -> str:
        blob = "\n".join(self._recent_clean_lines[-120:]).lower()
        if "module not found" in blob or "modulenotfounderror" in blob or "importerror" in blob:
            return "Import error or missing dependency"
        if "error collecting" in blob or "failed to collect" in blob:
            return "Test collection error"
        if "usage:" in blob or "unrecognized arguments" in blob:
            return "Invalid runner arguments"
        if self._abort:
            return "Stopped by user"
        if rc >= 2:
            return "Runner exited early"
        return ""

    def _single_target(self):
        if not self.node_spec:
            return None, None
        if isinstance(self.node_spec, dict):
            framework = self.framework if self.framework != "both" else self.node_spec.get("framework_hint", "pytest")
            target = self.node_spec.get("unittest_id") if framework == "unittest" else self.node_spec.get("pytest_node_id")
        else:
            target = str(self.node_spec)
            framework = self.framework if self.framework != "both" else ("pytest" if "::" in target else "unittest")
        return framework, target

    def _commands(self):
        if self.node_spec:
            framework, target = self._single_target()
            if framework == "unittest":
                return [("unittest (single)", [
                    self.python_exe, "-m", "unittest",
                ] + self.extra_args.get("unittest", []) + [target])]
            return [("pytest (single)", [
                self.python_exe, "-m", "pytest",
            ] + self.extra_args.get("pytest", []) + [target])]

        cmds = []
        if self.framework in ("pytest", "both"):
            cmds.append(("pytest", [
                self.python_exe, "-m", "pytest",
            ] + self.extra_args.get("pytest", []) + [self.folder]))
        if self.framework in ("unittest", "both"):
            cmds.append(("unittest", [
                self.python_exe, "-m", "unittest",
                "discover", "-s", self.folder, "-t", self.work_dir,
            ] + self.extra_args.get("unittest", [])))
        return cmds

    def run(self):
        summary = {
            "passed": 0, "failed": 0, "error": 0,
            "skipped": 0, "total": 0, "duration": 0.0,
            "framework": self.framework,
            "runner_issue": False,
            "issue_text": "",
            "python_exe": self.python_exe,
            "work_dir": self.work_dir,
            "folder": self.folder,
        }
        t0 = time.time()
        for label, cmd in self._commands():
            if self._abort:
                break
            self._run_one(cmd, label, summary)
        summary["duration"] = round(time.time() - t0, 2)
        self.finished_run.emit(summary)

    def _run_one(self, cmd, label, summary):
        pretty_cmd = subprocess.list2cmdline(cmd) if os.name == "nt" else " ".join(shlex.quote(p) for p in cmd)
        self.chunk_ready.emit(
            f"\x1b[36m{'─'*60}\n▶  {label}  —  {self.folder}\n"
            f"Python : {self.python_exe}\n"
            f"Run dir: {self.work_dir}\n"
            f"Command: {pretty_cmd}\n"
            f"{'─'*60}\x1b[0m\n"
        )

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        try:
            kwargs = dict(
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.work_dir,
                env=env,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            if sys.platform != "win32":
                kwargs["start_new_session"] = True
            self._proc = subprocess.Popen(cmd, **kwargs)
        except FileNotFoundError as exc:
            self._issue_text = f"Cannot launch runner: {exc}"
            self.chunk_ready.emit(f"\x1b[31m✗  {self._issue_text}\x1b[0m\n")
            summary["runner_issue"] = True
            summary["issue_text"] = self._issue_text
            return
        except Exception as exc:
            self._issue_text = f"Launch error: {exc}"
            self.chunk_ready.emit(f"\x1b[31m✗  {self._issue_text}\x1b[0m\n")
            summary["runner_issue"] = True
            summary["issue_text"] = self._issue_text
            return

        q: queue.Queue = queue.Queue()
        t = threading.Thread(target=_pipe_reader, args=(self._proc.stdout, q), daemon=True)
        t.start()

        pipes_open = 1
        last_output = time.time()
        last_flush = time.time()
        batch = []
        total_lines = 0
        capped = False

        def _flush():
            nonlocal batch
            if batch:
                self.chunk_ready.emit("".join(batch))
                batch = []

        while pipes_open > 0 and not self._abort:
            try:
                item = q.get(timeout=0.025)
            except queue.Empty:
                _flush()
                last_flush = time.time()
                if self._proc.poll() is not None:
                    try:
                        while True:
                            item = q.get_nowait()
                            if item is _SENTINEL:
                                pipes_open -= 1
                                break
                            total_lines += 1
                            self._append_recent_line(item)
                            self._parse_line(item, summary, batch)
                    except queue.Empty:
                        pass
                    _flush()
                    break
                if time.time() - last_output > self.WATCHDOG_TIMEOUT:
                    self._issue_text = f"No output for {self.WATCHDOG_TIMEOUT}s — killed hung process"
                    self.chunk_ready.emit(f"\x1b[33m⚠  {self._issue_text}\x1b[0m\n")
                    self._kill_proc()
                    summary["runner_issue"] = True
                    summary["issue_text"] = self._issue_text
                    break
                continue

            if item is _SENTINEL:
                pipes_open -= 1
                _flush()
                break

            last_output = time.time()
            total_lines += 1
            self._append_recent_line(item)

            if isinstance(item, str) and len(item) > self.MAX_LINE_LEN:
                item = item[:self.MAX_LINE_LEN] + " \x1b[33m[...line truncated]\x1b[0m\n"

            if not capped and total_lines > self.MAX_TOTAL_LINES:
                capped = True
                _flush()
                self.chunk_ready.emit(
                    f"\x1b[31m{'━'*60}\n"
                    f"⛔  OUTPUT CAPPED at {self.MAX_TOTAL_LINES} lines.\n"
                    f"    Process is still running — use ■ Stop to kill it.\n"
                    f"{'━'*60}\x1b[0m\n"
                )
                summary["runner_issue"] = True
                summary["issue_text"] = "Output capped"

            self._parse_line(item, summary, [] if capped else batch)

            if time.time() - last_flush >= self.FLUSH_INTERVAL:
                _flush()
                last_flush = time.time()

        try:
            self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._kill_proc()
            summary["runner_issue"] = True
            summary["issue_text"] = "Timed out while waiting for process exit"

        t.join(timeout=5)

        rc = self._proc.returncode if self._proc else -1
        if rc not in (0, None):
            ansi = "33" if rc == 1 else "31"
            self.chunk_ready.emit(f"\x1b[{ansi}m── exit code {rc} ──\x1b[0m\n")

        if rc is not None and rc >= 2 and not self._abort:
            issue = self._classify_issue(rc)
            summary["runner_issue"] = True
            summary["issue_text"] = issue
            self.chunk_ready.emit(
                f"\x1b[31m⚠  {issue}. Full runner output is captured above.\x1b[0m\n"
            )

    def _parse_line(self, raw: str, summary: dict, batch: list):
        batch.append(raw)
        clean = strip_ansi(raw)

        m = re.match(
            r"^([\w/\\.:\-]+(?:::\w+){1,2})\s+"
            r"(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\s*",
            clean.strip(),
        )
        if m:
            node_id, status = m.group(1).strip(), m.group(2)
            self.test_result.emit(node_id, status)
            summary[status.lower()] = summary.get(status.lower(), 0) + 1
            summary["total"] += 1
            return

        m2 = re.match(
            r"^(\w+)\s+\(([\w.]+)\)\s+\.\.\.\s+(ok|FAIL|ERROR|skipped.*)",
            clean.strip(),
        )
        if m2:
            name, owner, res = m2.group(1), m2.group(2), m2.group(3).strip()
            status = (
                "SKIPPED" if res.startswith("skipped") else
                {"ok": "PASSED", "FAIL": "FAILED", "ERROR": "ERROR"}.get(res, "ERROR")
            )
            node_id = f"{owner}.{name}"
            self.test_result.emit(node_id, status)
            summary[status.lower()] = summary.get(status.lower(), 0) + 1
            summary["total"] += 1


# ─────────────────────────────────────────────────────────────────────────────
#  ICONS
# ─────────────────────────────────────────────────────────────────────────────

STATUS_ICONS = {
    "PASSED":  ("●", ACCENT_GREEN),
    "FAILED":  ("●", ACCENT_RED),
    "ERROR":   ("●", ACCENT_RED),
    "SKIPPED": ("●", ACCENT_YELLOW),
    "XFAIL":   ("●", ACCENT_PURPLE),
    "XPASS":   ("●", ACCENT_CYAN),
    "PENDING": ("○", TEXT_MUTED),
}


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class TestRunnerGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCentric Test Runner v1.3")
        self.resize(1440, 880)
        self.setMinimumSize(900, 600)

        self._runner         = None
        self._raw_log_lines  = []
        self._discovered     = []
        self._result_items   = {}       # node_id → QTreeWidgetItem
        self._test_lookup    = {}       # pytest/unittest ids → discovered test dict
        self._settings       = QSettings("PyCentric", "TestRunner")
        self._t_start        = 0.0
        self._selected_test  = None     # currently selected discovered test dict

        self._build_ui()
        self.setStyleSheet(STYLE)
        self._restore_state()
        self._update_controls()

    # ─── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_menu()
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 4, 8, 4)
        root.setSpacing(6)

        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_sep())

        split = QSplitter(Qt.Horizontal)
        split.addWidget(self._build_left())
        split.addWidget(self._build_right())
        split.setSizes([380, 1060])
        split.setStretchFactor(1, 1)
        root.addWidget(split, 1)
        root.addWidget(self._build_status_strip())

        sb = QStatusBar()
        self.setStatusBar(sb)
        self.statusBar = sb
        self.statusBar.showMessage("Ready — select a project folder to begin")

    def _build_menu(self):
        mb = self.menuBar()

        fm = mb.addMenu("File")
        fm.addAction("Open Folder…",       self._browse_folder,   "Ctrl+O")
        fm.addAction("Save Output…",       self._save_output,     "Ctrl+S")
        fm.addSeparator()
        fm.addAction("Quit",               self.close,             "Ctrl+Q")

        rm = mb.addMenu("Run")
        rm.addAction("Run All Tests",      self._run_all,          "F5")
        rm.addAction("Run Selected Test",  self._run_selected,     "F6")
        rm.addAction("Stop",               self._stop_tests,       "Escape")
        rm.addSeparator()
        rm.addAction("Discover Tests",     self._discover,         "F7")

        vm = mb.addMenu("View")
        vm.addAction("Clear Output",       self._clear_output)
        vm.addAction("Clear Results",      self._clear_results)

        hm = mb.addMenu("Help")
        hm.addAction("About",              self._about)

    def _build_toolbar(self):
        bar = QWidget()
        outer = QVBoxLayout(bar)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(8)

        row1.addWidget(QLabel("Project:"))
        self.edtFolder = QLineEdit()
        self.edtFolder.setPlaceholderText("Select project folder…")
        self.edtFolder.textChanged.connect(self._on_folder_changed)
        row1.addWidget(self.edtFolder, 1)

        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._browse_folder)
        row1.addWidget(btn_browse)

        row1.addWidget(self._vsep())
        row1.addWidget(QLabel("Runner:"))
        self.cbFramework = QComboBox()
        self.cbFramework.addItems(["pytest", "unittest", "both"])
        self.cbFramework.setFixedWidth(110)
        row1.addWidget(self.cbFramework)

        row1.addWidget(self._vsep())
        row1.addWidget(QLabel("Args:"))
        self.edtArgs = QLineEdit()
        self.edtArgs.setPlaceholderText("-x  --lf  -k keyword  -m marker…")
        self.edtArgs.setFixedWidth(260)
        row1.addWidget(self.edtArgs)

        row1.addWidget(self._vsep())
        self.chkVerbose = QCheckBox("-v")
        self.chkVerbose.setChecked(True)
        row1.addWidget(self.chkVerbose)

        self.chkTB = QCheckBox("--tb")
        self.chkTB.setChecked(True)
        row1.addWidget(self.chkTB)

        self.chkColor = QCheckBox("colour")
        self.chkColor.setChecked(True)
        row1.addWidget(self.chkColor)

        row1.addWidget(self._vsep())

        self.btnDiscover = QPushButton("⟳ Discover")
        self.btnDiscover.clicked.connect(self._discover)
        row1.addWidget(self.btnDiscover)

        self.btnRunSingle = QPushButton("▶ Run Selected")
        self.btnRunSingle.setObjectName("btnRunSingle")
        self.btnRunSingle.setToolTip("Run the test selected in the discovery tree  (F6)")
        self.btnRunSingle.clicked.connect(self._run_selected)
        self.btnRunSingle.setShortcut("F6")
        row1.addWidget(self.btnRunSingle)

        self.btnRun = QPushButton("▶▶ Run All")
        self.btnRun.setObjectName("btnRun")
        self.btnRun.clicked.connect(self._run_all)
        self.btnRun.setShortcut("F5")
        row1.addWidget(self.btnRun)

        self.btnStop = QPushButton("■  Stop")
        self.btnStop.setObjectName("btnStop")
        self.btnStop.clicked.connect(self._stop_tests)
        self.btnStop.setEnabled(False)
        row1.addWidget(self.btnStop)

        self.btnSave = QPushButton("💾 Save Log")
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self._save_output)
        row1.addWidget(self.btnSave)

        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(8)

        row2.addWidget(QLabel("Run from:"))
        self.edtRunRoot = QLineEdit()
        self.edtRunRoot.setPlaceholderText("Auto-detect repo root from pyproject.toml / pytest.ini / .git")
        self.edtRunRoot.textChanged.connect(self._update_controls)
        row2.addWidget(self.edtRunRoot, 1)

        btn_root_auto = QPushButton("Auto")
        btn_root_auto.clicked.connect(self._clear_run_root_override)
        row2.addWidget(btn_root_auto)

        btn_root_browse = QPushButton("Browse…")
        btn_root_browse.clicked.connect(self._browse_run_root)
        row2.addWidget(btn_root_browse)

        row2.addWidget(self._vsep())
        row2.addWidget(QLabel("Python:"))
        self.edtPython = QLineEdit()
        self.edtPython.setPlaceholderText("Auto-detect .venv / venv, else use current interpreter")
        self.edtPython.textChanged.connect(self._update_controls)
        row2.addWidget(self.edtPython, 1)

        btn_python_auto = QPushButton("Auto")
        btn_python_auto.clicked.connect(self._clear_python_override)
        row2.addWidget(btn_python_auto)

        btn_python_browse = QPushButton("Browse…")
        btn_python_browse.clicked.connect(self._browse_python)
        row2.addWidget(btn_python_browse)

        self.lblResolved = QLabel("")
        self.lblResolved.setStyleSheet(f"color:{TEXT_MUTED}; font-size:11px;")
        row2.addWidget(self.lblResolved)

        outer.addLayout(row1)
        outer.addLayout(row2)
        return bar

    def _build_left(self):
        pane = QWidget()
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Discovery tree
        grp = QGroupBox("Test Discovery  (double-click or F6 to run one test)")
        gd = QVBoxLayout(grp)
        gd.setContentsMargins(4, 14, 4, 4)

        self.treeDisc = QTreeWidget()
        self.treeDisc.setHeaderLabels(["File / Class / Test", "Kind"])
        self.treeDisc.setAlternatingRowColors(True)
        self.treeDisc.header().setStretchLastSection(False)
        self.treeDisc.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.treeDisc.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.treeDisc.setIndentation(16)
        self.treeDisc.itemSelectionChanged.connect(self._on_disc_selection)
        self.treeDisc.itemDoubleClicked.connect(self._on_disc_double_click)
        self.treeDisc.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeDisc.customContextMenuRequested.connect(self._disc_context_menu)
        gd.addWidget(self.treeDisc)

        self.lblSelected = QLabel("No test selected")
        self.lblSelected.setWordWrap(True)
        self.lblSelected.setStyleSheet(
            f"color:{ACCENT_BLUE}; font-size:11px; padding:3px 6px; "
            f"background:{PANEL_BG}; border-radius:3px;"
        )
        gd.addWidget(self.lblSelected)

        self.lblDiscCount = QLabel("No tests discovered")
        self.lblDiscCount.setStyleSheet(f"color:{TEXT_MUTED}; font-size:11px; padding:2px 4px;")
        gd.addWidget(self.lblDiscCount)

        lay.addWidget(grp, 1)

        # Results tree
        grp2 = QGroupBox("Results  (right-click to re-run)")
        gr = QVBoxLayout(grp2)
        gr.setContentsMargins(4, 14, 4, 4)

        self.treeResults = QTreeWidget()
        self.treeResults.setHeaderLabels(["Test", "Status"])
        self.treeResults.setAlternatingRowColors(True)
        self.treeResults.header().setStretchLastSection(False)
        self.treeResults.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.treeResults.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.treeResults.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeResults.customContextMenuRequested.connect(self._result_context_menu)
        gr.addWidget(self.treeResults)
        lay.addWidget(grp2, 1)

        return pane

    def _build_right(self):
        pane = QWidget()
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.tabs = QTabWidget()

        self.txtOutput = QTextEdit()
        self.txtOutput.setReadOnly(True)
        self.txtOutput.setLineWrapMode(QTextEdit.NoWrap)
        self.tabs.addTab(self.txtOutput, "📋 Output")

        self.txtLog = QPlainTextEdit()
        self.txtLog.setReadOnly(True)
        self.tabs.addTab(self.txtLog, "📄 Log")

        self.txtSummary = QTextEdit()
        self.txtSummary.setReadOnly(True)
        self.tabs.addTab(self.txtSummary, "📊 Summary")

        lay.addWidget(self.tabs, 1)
        return pane

    def _build_status_strip(self):
        strip = QWidget()
        lay = QHBoxLayout(strip)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(12)

        self.barProgress = QProgressBar()
        self.barProgress.setRange(0, 100)
        self.barProgress.setValue(0)
        self.barProgress.setFixedHeight(8)
        lay.addWidget(self.barProgress, 1)

        def slbl(color, text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color:{color}; font-weight:600; font-size:12px; min-width:90px;")
            return lbl

        self.lblMode    = QLabel("")
        self.lblMode.setStyleSheet(f"color:{ACCENT_CYAN}; font-size:11px; font-weight:600;")
        self.lblPassed  = slbl(ACCENT_GREEN,  "✔ Passed: 0")
        self.lblFailed  = slbl(ACCENT_RED,    "✘ Failed: 0")
        self.lblSkipped = slbl(ACCENT_YELLOW, "⊘ Skipped: 0")
        self.lblTotal   = slbl(TEXT_PRIMARY,  "∑ Total: 0")
        self.lblElapsed = QLabel("⏱ 0.00s")
        self.lblElapsed.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px;")

        for w in [self.lblMode, self.lblPassed, self.lblFailed,
                  self.lblSkipped, self.lblTotal, self.lblElapsed]:
            lay.addWidget(w)

        return strip

    # ─── Small helpers ────────────────────────────────────────────────────────

    def _vsep(self):
        f = QFrame()
        f.setFrameShape(QFrame.VLine)
        f.setStyleSheet(f"color:{BORDER};")
        return f

    def _build_sep(self):
        f = QFrame()
        f.setObjectName("separator")
        f.setFrameShape(QFrame.HLine)
        return f

    # ─── Settings ─────────────────────────────────────────────────────────────

    def _restore_state(self):
        folder = self._settings.value("last_folder", "")
        if folder:
            self.edtFolder.setText(folder)

        fw = self._settings.value("framework", "pytest")
        idx = self.cbFramework.findText(fw)
        if idx >= 0:
            self.cbFramework.setCurrentIndex(idx)

        self.edtArgs.setText(self._settings.value("args", ""))
        self.edtRunRoot.setText(self._settings.value("run_root", ""))
        self.edtPython.setText(self._settings.value("python_exe", ""))

    def _save_state(self):
        self._settings.setValue("last_folder", self.edtFolder.text())
        self._settings.setValue("framework", self.cbFramework.currentText())
        self._settings.setValue("args", self.edtArgs.text())
        self._settings.setValue("run_root", self.edtRunRoot.text())
        self._settings.setValue("python_exe", self.edtPython.text())

    def closeEvent(self, ev):
        self._save_state()
        if self._runner and self._runner.isRunning():
            self._runner.stop()
            self._runner.wait(3000)
        super().closeEvent(ev)

    # ─── Folder ───────────────────────────────────────────────────────────────

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Project Folder",
            self.edtFolder.text() or str(Path.home()),
        )
        if folder:
            self.edtFolder.setText(folder)

    def _browse_run_root(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Working / Repo Root",
            self.edtRunRoot.text() or self.edtFolder.text() or str(Path.home()),
        )
        if folder:
            self.edtRunRoot.setText(folder)

    def _browse_python(self):
        start_dir = self.edtPython.text() or self.edtRunRoot.text() or self.edtFolder.text() or str(Path.home())
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Python Interpreter", start_dir,
            "Python executable (*.exe *.bat *.cmd *.sh *python*);;All files (*)",
        )
        if path:
            self.edtPython.setText(path)

    def _clear_run_root_override(self):
        self.edtRunRoot.clear()
        self._update_controls()

    def _clear_python_override(self):
        self.edtPython.clear()
        self._update_controls()

    def _resolve_run_context(self):
        folder = Path(self.edtFolder.text()).expanduser().resolve()

        if self.edtRunRoot.text().strip():
            run_root = Path(self.edtRunRoot.text().strip()).expanduser().resolve()
        else:
            run_root = detect_project_root(str(folder))

        if self.edtPython.text().strip():
            python_exe = Path(self.edtPython.text().strip()).expanduser().resolve()
        else:
            python_exe = detect_project_python(str(folder), run_root)

        return {
            "folder": str(folder),
            "run_root": str(run_root),
            "python_exe": str(python_exe),
        }

    def _on_folder_changed(self, text):
        self._update_controls()
        if text and Path(text).is_dir():
            try:
                ctx = self._resolve_run_context()
                self.lblResolved.setText(
                    f"auto root: {Path(ctx['run_root']).name or ctx['run_root']}   |   "
                    f"python: {Path(ctx['python_exe']).name}"
                )
            except Exception:
                self.lblResolved.setText("")
            self.statusBar.showMessage(f"Folder: {text}")

    def _update_controls(self):
        folder_ok = bool(self.edtFolder.text()) and Path(self.edtFolder.text()).is_dir()
        root_ok = (not self.edtRunRoot.text().strip()) or Path(self.edtRunRoot.text()).is_dir()
        python_ok = (not self.edtPython.text().strip()) or Path(self.edtPython.text()).is_file()
        ok = folder_ok and root_ok and python_ok
        running = self._runner is not None and self._runner.isRunning()
        self.btnRun.setEnabled(ok and not running)
        self.btnRunSingle.setEnabled(ok and not running and self._selected_test is not None)
        self.btnDiscover.setEnabled(folder_ok and not running)
        self.btnStop.setEnabled(running)

    # ─── Discovery ────────────────────────────────────────────────────────────

    def _discover(self):
        folder = self.edtFolder.text()
        if not folder or not Path(folder).is_dir():
            QMessageBox.warning(self, "No folder", "Please select a valid project folder first.")
            return

        self.treeDisc.clear()
        self._selected_test = None
        self._test_lookup = {}
        self.lblSelected.setText("No test selected")
        self._discovered = discover_tests(folder)
        total_tests = 0

        for fi in self._discovered:
            f_item = QTreeWidgetItem(self.treeDisc)
            f_item.setText(0, fi["rel_path"])
            f_item.setText(1, str(len(fi["tests"])))
            f_item.setForeground(0, QColor(ACCENT_BLUE))
            f_item.setData(0, Qt.UserRole, None)
            f_item.setExpanded(True)

            classes: dict = {}
            lone: list = []
            for t in fi["tests"]:
                self._test_lookup[t["pytest_node_id"]] = t
                if t["class_name"]:
                    classes.setdefault(t["class_name"], []).append(t)
                else:
                    lone.append(t)

            for cls_name, methods in classes.items():
                c_item = QTreeWidgetItem(f_item)
                c_item.setText(0, cls_name)
                c_item.setText(1, "class")
                c_item.setForeground(0, QColor(ACCENT_PURPLE))
                c_item.setData(0, Qt.UserRole, None)
                for m in methods:
                    m_item = QTreeWidgetItem(c_item)
                    m_item.setText(0, m["name"])
                    m_item.setText(1, m["framework_hint"])
                    m_item.setForeground(0, QColor(TEXT_MUTED))
                    m_item.setData(0, Qt.UserRole, m)

            for t in lone:
                t_item = QTreeWidgetItem(f_item)
                t_item.setText(0, t["name"])
                t_item.setText(1, t["framework_hint"])
                t_item.setForeground(0, QColor(TEXT_MUTED))
                t_item.setData(0, Qt.UserRole, t)

            total_tests += len(fi["tests"])

        fc = len(self._discovered)
        self.lblDiscCount.setText(
            f"{total_tests} test{'s' if total_tests != 1 else ''} "
            f"in {fc} file{'s' if fc != 1 else ''}"
        )
        self.statusBar.showMessage(f"Discovered {total_tests} tests in {fc} files")
        self._log(f"Discovery: {total_tests} tests, {fc} files — {folder}")
        self._update_controls()

    def _display_test_id(self, test: dict) -> str:
        return test.get("pytest_node_id") or test.get("name", "")

    def _register_runtime_test_aliases(self, run_root: str):
        for fi in self._discovered:
            for test in fi["tests"]:
                test["unittest_id"] = build_unittest_id(test, run_root)
                self._test_lookup[test["unittest_id"]] = test
                self._test_lookup[test["pytest_node_id"]] = test

    def _coerce_test_spec(self, spec):
        if isinstance(spec, dict):
            return spec
        return self._test_lookup.get(spec, spec)

    def _on_disc_selection(self):
        items = self.treeDisc.selectedItems()
        if not items:
            self._selected_test = None
            self.lblSelected.setText("No test selected")
            self._update_controls()
            return
        test = items[0].data(0, Qt.UserRole)
        if isinstance(test, dict):
            self._selected_test = test
            self.lblSelected.setText(f"▶  {test['name']}\n{self._display_test_id(test)}")
        else:
            self._selected_test = None
            self.lblSelected.setText("Select a test function (not a file or class)")
        self._update_controls()

    def _on_disc_double_click(self, item, _col):
        test = item.data(0, Qt.UserRole)
        if isinstance(test, dict) and not (self._runner and self._runner.isRunning()):
            self._selected_test = test
            self._run_node(test)

    def _disc_context_menu(self, pos):
        item = self.treeDisc.itemAt(pos)
        if not item:
            return
        test = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        if isinstance(test, dict):
            menu.addAction(f"▶  Run  {test['name']}", lambda: self._run_node(test))
            menu.addSeparator()
        menu.addAction("⟳  Discover", self._discover)
        menu.exec_(self.treeDisc.viewport().mapToGlobal(pos))

    def _result_context_menu(self, pos):
        item = self.treeResults.itemAt(pos)
        if not item:
            return
        spec = item.data(0, Qt.UserRole) or item.toolTip(0) or item.text(0)
        short = spec["name"] if isinstance(spec, dict) else str(spec).split("::")[-1].split(".")[-1]
        menu = QMenu(self)
        menu.addAction(f"▶  Re-run  {short}", lambda: self._run_node(spec))
        menu.exec_(self.treeResults.viewport().mapToGlobal(pos))

    # ─── Run ─────────────────────────────────────────────────────────────────

    def _sanitize_unittest_args(self, args):
        cleaned = []
        removed = []

        skip_with_value = {"-k", "-m", "--maxfail", "-p"}
        pytest_prefixes = ("--tb=", "--color=")
        pytest_flags = {
            "--lf", "--ff", "-q", "-s", "--disable-warnings",
            "--cache-clear", "--no-header", "--co", "--collect-only",
            "--last-failed", "--last-failed-no-failures",
        }

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in skip_with_value:
                removed.append(arg)
                if i + 1 < len(args):
                    removed.append(args[i + 1])
                    i += 2
                else:
                    i += 1
                continue
            if arg in pytest_flags or any(arg.startswith(prefix) for prefix in pytest_prefixes):
                removed.append(arg)
                i += 1
                continue
            cleaned.append(arg)
            i += 1

        return cleaned, removed

    def _extra_args(self):
        raw = shlex.split(self.edtArgs.text())
        pytest_args = list(raw)
        unittest_args, removed = self._sanitize_unittest_args(raw)

        if self.chkVerbose.isChecked() and "-v" not in pytest_args:
            pytest_args.append("-v")
        if self.chkTB.isChecked() and not any(a.startswith("--tb") for a in pytest_args):
            pytest_args.append("--tb=short")
        if self.chkColor.isChecked() and not any(a.startswith("--color") for a in pytest_args):
            pytest_args.append("--color=yes")
        if "--no-header" not in pytest_args:
            pytest_args.append("--no-header")
        if "-p" not in pytest_args and "no:cacheprovider" not in pytest_args:
            pytest_args.extend(["-p", "no:cacheprovider"])

        if self.chkVerbose.isChecked() and "-v" not in unittest_args:
            unittest_args.append("-v")

        return {
            "pytest": pytest_args,
            "unittest": unittest_args,
            "removed_for_unittest": removed,
        }

    def _start_runner(self, node_spec=None, mode_label="All Tests"):
        folder = self.edtFolder.text()
        if not folder or not Path(folder).is_dir():
            QMessageBox.warning(self, "No folder", "Please select a valid project folder first.")
            return

        try:
            ctx = self._resolve_run_context()
        except Exception as exc:
            QMessageBox.critical(self, "Invalid run configuration", str(exc))
            return

        if not Path(ctx["run_root"]).is_dir():
            QMessageBox.warning(self, "Invalid run root", "Please choose a valid working / repo root folder.")
            return
        if not Path(ctx["python_exe"]).is_file():
            QMessageBox.warning(self, "Invalid interpreter", "Please choose a valid Python interpreter.")
            return

        self._register_runtime_test_aliases(ctx["run_root"])

        self._clear_output()
        self._clear_results()
        self._raw_log_lines = []
        self._result_items = {}
        self._t_start = time.time()

        for lbl, txt in [
            (self.lblPassed, "✔ Passed: 0"),
            (self.lblFailed, "✘ Failed: 0"),
            (self.lblSkipped, "⊘ Skipped: 0"),
            (self.lblTotal, "∑ Total: 0"),
            (self.lblElapsed, "⏱ 0.00s"),
        ]:
            lbl.setText(txt)

        self.barProgress.setValue(0)
        self.barProgress.setProperty("state", "")
        self.barProgress.setStyleSheet(STYLE)
        self.lblMode.setText(f"Mode: {mode_label}")

        extra = self._extra_args()
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log(f"Run started — {ts}")
        self._log(f"Folder       : {ctx['folder']}")
        self._log(f"Run root     : {ctx['run_root']}")
        self._log(f"Python       : {ctx['python_exe']}")
        self._log(f"Framework    : {self.cbFramework.currentText()}")
        self._log(f"Pytest args  : {' '.join(extra['pytest']) or '(none)'}")
        self._log(f"Unittest args: {' '.join(extra['unittest']) or '(none)'}")
        if extra["removed_for_unittest"]:
            self._log(f"Removed for unittest: {' '.join(extra['removed_for_unittest'])}")
        if isinstance(node_spec, dict):
            self._log(f"Selected     : {node_spec.get('name')}  [{node_spec.get('framework_hint')}]")
            self._log(f"Pytest id    : {node_spec.get('pytest_node_id')}")
            self._log(f"Unittest id  : {node_spec.get('unittest_id')}")
        elif node_spec:
            self._log(f"Selected     : {node_spec}")

        self._runner = RunnerThread(
            ctx["folder"],
            self.cbFramework.currentText(),
            extra,
            node_spec=node_spec,
            python_exe=ctx["python_exe"],
            work_dir=ctx["run_root"],
        )
        self._runner.chunk_ready.connect(self._on_chunk)
        self._runner.test_result.connect(self._on_result)
        self._runner.finished_run.connect(self._on_finished)
        self._runner.start()

        self._update_controls()
        self.statusBar.showMessage(f"Running {mode_label}…")
        self.tabs.setCurrentIndex(0)

        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.timeout.connect(self._tick_elapsed)
        self._elapsed_timer.start(100)

    def _run_all(self):
        self._start_runner(node_spec=None, mode_label="All Tests")

    def _run_selected(self):
        if not self._selected_test:
            QMessageBox.information(
                self, "No test selected",
                "Click on a test function in the Discovery tree first.\n\n"
                "Tip: double-click any test to run it immediately."
            )
            return
        self._run_node(self._selected_test)

    def _run_node(self, spec):
        spec = self._coerce_test_spec(spec)
        if isinstance(spec, dict):
            self._selected_test = spec
            self.lblSelected.setText(f"▶  {spec['name']}\n{self._display_test_id(spec)}")
            self._start_runner(node_spec=spec, mode_label=f"Single: {spec['name']}")
        else:
            short = str(spec).split("::")[-1].split(".")[-1]
            self._start_runner(node_spec=spec, mode_label=f"Single: {short}")

    def _stop_tests(self):
        if self._runner:
            self._runner.stop()
            self._log("Stopped by user")
            self.statusBar.showMessage("Stopped by user")
        if hasattr(self, "_elapsed_timer"):
            self._elapsed_timer.stop()
        self._runner = None
        self._update_controls()

    def _tick_elapsed(self):
        self.lblElapsed.setText(f"⏱ {time.time() - self._t_start:.1f}s")

    # ─── Slots ────────────────────────────────────────────────────────────────

    def _on_chunk(self, raw_chunk: str):
        """
        Receive a batch of raw lines from the runner thread.
        - Stores plain text for log/save
        - Renders HTML into the output widget in ONE insertHtml call
        - Caps the QTextEdit to MAX_OUTPUT_BLOCKS to prevent memory/render death
        """
        MAX_OUTPUT_BLOCKS = 4000   # drop oldest blocks when exceeded

        lines = raw_chunk.splitlines(keepends=True)
        for line in lines:
            self._raw_log_lines.append(strip_ansi(line).rstrip())

        # Plain log tab — appendPlainText is fast
        self.txtLog.appendPlainText(strip_ansi(raw_chunk).rstrip())

        # Build one HTML string for the whole batch
        html_batch = ansi_to_html(raw_chunk).replace("\n", "<br>")
        html_blob = f'<span style="font-family:monospace;white-space:pre">{html_batch}</span>'

        # Insert at end
        cur = self.txtOutput.textCursor()
        cur.movePosition(QTextCursor.End)
        cur.insertHtml(html_blob)

        # Trim oldest content if DOM is getting huge
        doc = self.txtOutput.document()
        while doc.blockCount() > MAX_OUTPUT_BLOCKS:
            trim = QTextCursor(doc)
            trim.movePosition(QTextCursor.Start)
            trim.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            trim.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            trim.removeSelectedText()

        self.txtOutput.ensureCursorVisible()

    def _on_result(self, node_id: str, status: str):
        icon, color = STATUS_ICONS.get(status, ("○", TEXT_MUTED))

        if node_id in self._result_items:
            item = self._result_items[node_id]
        else:
            item = QTreeWidgetItem(self.treeResults)
            short = node_id.split("::")[-1] if "::" in node_id else node_id.split(".")[-1]
            item.setText(0, short)
            item.setToolTip(0, node_id)
            spec = self._test_lookup.get(node_id)
            if spec is not None:
                item.setData(0, Qt.UserRole, spec)
            self._result_items[node_id] = item

        item.setText(1, f"{icon} {status}")
        item.setForeground(1, QColor(color))
        self.treeResults.scrollToItem(item)
        self._mark_disc_item(node_id, color)

        counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0}
        total = 0
        for i in range(self.treeResults.topLevelItemCount()):
            it = self.treeResults.topLevelItem(i)
            s = it.text(1).split()[-1] if it.text(1) else ""
            total += 1
            if s in counts:
                counts[s] += 1

        self.lblPassed.setText(f"✔ Passed: {counts['PASSED']}")
        self.lblFailed.setText(f"✘ Failed: {counts['FAILED']}")
        self.lblSkipped.setText(f"⊘ Skipped: {counts['SKIPPED']}")
        self.lblTotal.setText(f"∑ Total: {total}")

        if total > 0:
            pct = int(counts["PASSED"] / total * 100)
            self.barProgress.setValue(pct)
            state = "fail" if counts["FAILED"] > 0 else "pass"
            self.barProgress.setProperty("state", state)
            self.barProgress.setStyleSheet(STYLE)

    def _mark_disc_item(self, node_id: str, color: str):
        """Colour the matching leaf node in the discovery tree."""
        def walk(parent):
            for i in range(parent.childCount()):
                child = parent.child(i)
                spec = child.data(0, Qt.UserRole)
                if isinstance(spec, dict):
                    aliases = {spec.get("pytest_node_id"), spec.get("unittest_id")}
                    if node_id in aliases:
                        child.setForeground(0, QColor(color))
                        return
                walk(child)
        walk(self.treeDisc.invisibleRootItem())

    def _on_finished(self, summary: dict):
        if hasattr(self, "_elapsed_timer"):
            self._elapsed_timer.stop()

        dur = summary["duration"]
        self.lblElapsed.setText(f"⏱ {dur:.2f}s")
        self._runner = None
        self._update_controls()

        issue_note = ""
        if summary.get("runner_issue"):
            issue_note = f"  ⚠ {summary.get('issue_text') or 'Runner issue'}."

        msg = (
            f"Done — {summary['passed']} passed, "
            f"{summary['failed']} failed, "
            f"{summary.get('skipped', 0)} skipped "
            f"in {dur:.2f}s{issue_note}"
        )
        self.statusBar.showMessage(msg)
        self._log(msg)
        self._raw_log_lines += ["", "─" * 60, msg]

        self.txtSummary.setHtml(self._build_summary_html(summary))
        if summary.get("runner_issue") or summary["failed"] > 0:
            self.tabs.setCurrentIndex(2)


    # ─── Summary ──────────────────────────────────────────────────────────────

    def _build_summary_html(self, s: dict) -> str:
        total  = max(s["total"], 1)
        p_pct  = s["passed"] / total * 100
        f_pct  = s["failed"] / total * 100
        sk_pct = s.get("skipped", 0) / total * 100

        def row(label, value, color):
            return (
                f'<tr>'
                f'<td style="padding:6px 16px;color:{TEXT_MUTED}">{label}</td>'
                f'<td style="padding:6px 16px;color:{color};font-weight:700">{value}</td>'
                f'</tr>'
            )

        issue_html = ""
        if s.get("runner_issue"):
            issue_html = (
                f'<p style="color:{ACCENT_RED};background:#2d0f0f;padding:8px 12px;'
                f'border-radius:4px;border-left:3px solid {ACCENT_RED};margin:12px 0">'
                f'⚠  Runner issue: {s.get("issue_text") or "Unknown"}<br>'
                f'The full diagnostic output is available in the Output tab and '
                f'will be included when you save the log.</p>'
            )

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <html><body style="background:{DARK_BG};color:{TEXT_PRIMARY};
                           font-family:'Segoe UI',sans-serif;padding:16px;">
        <h2 style="color:{ACCENT_BLUE};margin-bottom:4px;">Test Run Summary</h2>
        <p style="color:{TEXT_MUTED};font-size:11px;margin-top:0">{ts}</p>
        {issue_html}
        <hr style="border-color:{BORDER};margin:12px 0">
        <table cellspacing=0 cellpadding=0>
          {row("Mode",         self.lblMode.text(),                         ACCENT_CYAN)}
          {row("Framework",    s["framework"],                              ACCENT_CYAN)}
          {row("Folder",       s.get("folder", self.edtFolder.text()),      TEXT_PRIMARY)}
          {row("Run root",     s.get("work_dir", self.edtRunRoot.text() or "(auto)"), TEXT_PRIMARY)}
          {row("Python",       s.get("python_exe", self.edtPython.text() or sys.executable), TEXT_PRIMARY)}
          {row("Total",        s["total"],                                  TEXT_PRIMARY)}
          {row("Passed",       f"{s['passed']} ({p_pct:.0f}%)",             ACCENT_GREEN)}
          {row("Failed",       f"{s['failed']} ({f_pct:.0f}%)",             ACCENT_RED)}
          {row("Skipped",      f"{s.get('skipped',0)} ({sk_pct:.0f}%)",     ACCENT_YELLOW)}
          {row("Duration",     f"{s['duration']}s",                         TEXT_MUTED)}
          {row("Runner issue", "Yes" if s.get("runner_issue") else "No",
               ACCENT_RED if s.get("runner_issue") else ACCENT_GREEN)}
          {row("Issue detail", s.get("issue_text") or "—",
               ACCENT_RED if s.get("runner_issue") else TEXT_MUTED)}
        </table>
        </body></html>
        """

    # ─── Log ─────────────────────────────────────────────────────────────────

    def _log(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.txtLog.appendPlainText(entry)
        self._raw_log_lines.append(entry)

    # ─── Clear / Save ─────────────────────────────────────────────────────────

    def _clear_output(self):
        self.txtOutput.clear()
        self.txtLog.clear()
        self.txtSummary.clear()
        self._raw_log_lines = []

    def _clear_results(self):
        self.treeResults.clear()
        self._result_items = {}
        self.barProgress.setValue(0)
        for lbl, txt in [
            (self.lblPassed,  "✔ Passed: 0"),
            (self.lblFailed,  "✘ Failed: 0"),
            (self.lblSkipped, "⊘ Skipped: 0"),
            (self.lblTotal,   "∑ Total: 0"),
        ]:
            lbl.setText(txt)

    def _save_output(self):
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Output",
            str(Path.home() / f"test_output_{stamp}.txt"),
            "Text files (*.txt);;All files (*)",
        )
        if not path:
            return

        lines = [
            "=" * 72,
            "  PyCentric Test Runner — Full Output Log",
            f"  Saved    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Folder   : {self.edtFolder.text()}",
            f"  Runner   : {self.cbFramework.currentText()}",
            f"  Mode     : {self.lblMode.text()}",
            "=" * 72,
            "",
        ] + self._raw_log_lines + [
            "",
            "─" * 72,
            "  RESULTS",
            "─" * 72,
        ]

        for i in range(self.treeResults.topLevelItemCount()):
            it = self.treeResults.topLevelItem(i)
            lines.append(f"  {it.text(1).ljust(20)}  {it.toolTip(0) or it.text(0)}")

        lines += ["", "=" * 72]

        try:
            Path(path).write_text("\n".join(lines), encoding="utf-8")
            self.statusBar.showMessage(f"Saved → {path}")
            QMessageBox.information(self, "Saved", f"Output saved to:\n{path}")
        except OSError as exc:
            QMessageBox.critical(self, "Save Error", f"Could not write file:\n{exc}")

    # ─── About ────────────────────────────────────────────────────────────────

    def _about(self):
        QMessageBox.about(
            self, "PyCentric Test Runner",
            "<h3>PyCentric Test Runner v1.3</h3>"
            "<p>GUI frontend for <b>pytest</b> &amp; <b>unittest</b>.</p>"
            "<ul>"
            "<li>Auto-discovers tests via AST (no imports needed)</li>"
            "<li><b>Run all</b> (F5) or <b>run one test</b> (F6 / double-click)</li>"
            "<li>Right-click any result to re-run that test</li>"
            "<li>Live streamed output with ANSI colour</li>"
            "<li><b>stderr merged</b> — import / collection errors are always captured</li>"
            "<li><b>Non-blocking I/O</b> — never locks up on failures</li>"
            "<li>Auto-detects repo root and project virtualenv where possible</li>"
            "<li>Single-test mode supports pytest and unittest</li>"
            "<li>120s watchdog kills hung processes automatically</li>"
            "<li>Save full log + results to .txt</li>"
            "</ul>"
            f"<p style='color:{TEXT_MUTED}'>Python {sys.version.split()[0]}</p>",
        )


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyCentric Test Runner")
    app.setOrganizationName("PyCentric")

    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    win = TestRunnerGUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
