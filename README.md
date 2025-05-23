# 🧪 Domain Guest Post Checker - GUI Edition

A stylish Python desktop application that checks whether domains accept guest posts or article submissions via automated Google search queries.

## 🚀 Features

- Custom GUI with sleek blue header bar (`X`, `?`, `-`)
- File picker buttons for `Query` and `Domain` files
- Tooltip hints to guide users
- Status bar with real-time processing updates and color indicators
- Simulated domain search and CSV export with semicolon delimiter
- Fully offline and lightweight

## 📁 How It Works

1. **Query File (`query.txt`)**
   Contains a search template using `{{domain}}`.  
   Example:
   ```
   site:{{domain}} "guest post"
   ```

2. **Domains File (`domains.txt`)**
   List of domains to test, one per line:
   ```
   example.com
   nytimes.com
   fake-domain.xyz
   ```

3. **Click `Start Check`**
   The program simulates searches and saves:
   ```
   Domain;Status
   example.com;N
   nytimes.com;Y
   fake-domain.xyz;ISSUE
   ```

## 📦 Output

- `results.csv`: CSV using semicolon (`;`)
- Status:
  - `Y`: likely accepts guest posts
  - `N`: no match found
  - `ISSUE`: error during lookup

## ⚙️ Installation

> Requires Python 3.8 or later

### 📌 Step-by-step (Windows/macOS/Linux)

1. **Install Python**  
   Download from [python.org](https://www.python.org/downloads/) and ensure it's added to your PATH.

2. **Run the script**
   ```bash
   python main.py
   ```

✅ No external libraries required — only `tkinter` (comes with Python).

---

## 👨‍💻 Author

Mitchell Symington  
[GitHub Profile](https://github.com/MitchellSymington)
