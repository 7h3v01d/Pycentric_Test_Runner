# 🧪 PyCentric Test Runner

A sleek, dark-themed GUI frontend for running **pytest** and **unittest** on any Python project — with live output, real-time results, and zero configuration needed.

![PyCentric Test Runner v1.3](Pycentric_Test_Runner_v1_3.png)

---

## ✨ Features

- **AST-based test discovery** — finds all tests without importing your code, so broken imports won't block discovery
- **Dual framework support** — run pytest, unittest, or both at once
- **Live streaming output** — ANSI colour codes rendered in real time as tests execute
- **Run All or Run Selected** — press F5 to run all, F6 or double-click to run a single test
- **Right-click to re-run** — instantly re-run any individual test result from the results panel
- **Auto-detects project root** — looks for `pyproject.toml`, `pytest.ini`, `tox.ini`, `setup.cfg`, `setup.py`, or `.git`
- **Auto-detects virtualenv** — finds `.venv`, `venv`, or `env` in your project automatically
- **Non-blocking I/O** — a background pipe-reader thread ensures the UI never freezes, even on failures or hung processes
- **120s watchdog** — automatically kills any subprocess that stops producing output for 2 minutes
- **stderr merged** — import errors and collection failures are always captured and shown
- **Smart issue classification** — detects import errors, collection errors, invalid args, and more
- **Save Log** — export the full output + results to a `.txt` file
- **Output / Log / Summary tabs** — clean separation of raw output, timestamped log, and run summary
- **Persistent settings** — remembers your last project folder, runner, and arguments between sessions
- **High-DPI aware** — works correctly on HiDPI / Retina displays

---

## 🖥️ Screenshot

The interface is split into three panels:

| Panel | Description |
|---|---|
| **Left** | Test discovery tree (files → classes → tests) and live results list |
| **Right — Output** | Raw pytest/unittest output with ANSI colour rendering |
| **Right — Log** | Timestamped event log |
| **Right — Summary** | Pass/fail/skip counts, duration, and run metadata |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pycentric-test-runner.git
   cd pycentric-test-runner
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python Pycentric_Test_Runner_v1_3.py
   ```

---

## 🎮 Usage

1. **Set your project folder** using the Browse button or type the path directly
2. **Choose your runner** — `pytest`, `unittest`, or `both`
3. **Add extra args** (optional) — e.g. `-x -v -k keyword -m marker`
4. Click **Run All** (or press `F5`) to run your entire test suite
5. **Double-click** any test in the discovery tree (or press `F6`) to run just that test
6. **Right-click** any result to re-run it individually
7. Click **Save Log** to export the full output to a `.txt` file

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `F5` | Run All tests |
| `F6` | Run selected test |

---

## ⚙️ Configuration

| Field | Description |
|---|---|
| **Project** | Root folder of your Python project |
| **Run from** | Working directory for the test runner (auto-detects repo root) |
| **Runner** | `pytest`, `unittest`, or `both` |
| **Args** | Extra arguments passed to the runner |
| **Python** | Path to Python interpreter (auto-detects project virtualenv) |
| **-v / --tb / colour** | Quick toggles for verbose, traceback style, and colour output |

---

## 📋 Requirements

See [requirements.txt](requirements.txt).

The only external dependency is **PyQt5**. Everything else uses the Python standard library.

---

## 🗂️ Project Structure

```
pycentric-test-runner/
├── Pycentric_Test_Runner_v1_3.py   # Main application
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🔧 How It Works

- **Discovery**: The app walks your project folder for `test_*.py` and `*_test.py` files and parses them with Python's `ast` module — no imports, no side effects.
- **Running**: Tests are executed in a `QThread` via `subprocess`, with stdout/stderr merged and drained by a non-blocking pipe reader.
- **Output**: ANSI escape codes are converted to inline HTML `<span>` styles for coloured rendering in the output pane.
- **Settings**: Project folder, runner choice, and arguments are persisted with `QSettings`.

---

## 📄 License

This project is open source. Add your preferred license here.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.
