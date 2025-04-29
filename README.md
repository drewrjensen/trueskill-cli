# TrueSkill CLI
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A cross-platform command-line application to manage players, matches, and rankings for competitive leagues using Microsoft's [TrueSkill](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/) system.

Supports:
- 🧑 Individual, 👥 team, and ⚔️ free-for-all matches
- 📅 Match history and date tracking
- 🧠 Undo/redo system
- 📈 Rankings with uncertainty (μ/σ)
- 🔄 Rating recalculation from any match
- 🧾 Database backups
- 🧰 Builds for Windows and Linux

---

## 🚀 Features

- Add, edit, or delete players and matches
- Auto-updating rankings with TrueSkill
- Date-aware match storage (`datetime` format)
- Comma-separated, team-formatted input:  
  e.g. `John,Erin`, `[Erin,Samantha],[John,Roger]`
- Interactive editing with autocomplete and fuzzy-matching
- Undo support for last operation
- CLI flags for version, DB file override, and help

---

## 🧑‍💻 Installation

### 🔧 From source (Linux/macOS)

```bash
git clone https://github.com/drewrjensen/trueskill-cli.git
cd trueskill-cli
chmod +x install-dependencies.sh
./install-dependencies.sh
python main.py
```

### 🪟 From source (Windows)

```cmd
git clone https://github.com/drewrjensen/trueskill-cli.git
cd trueskill-cli
install-dependencies.bat
python main.py
```

### 📦 From releases

Download prebuilt binaries from the [Releases](https://github.com/drewrjensen/trueskill-cli/releases) tab:
- Windows: `trueskill-cli.exe`
- Linux: `trueskill-cli`

---

## 🧪 Usage

### 🧍 Players

```bash
trueskill-cli players add John,Erin
trueskill-cli players list
trueskill-cli players delete John
```

### 📊 Rankings

```bash
trueskill-cli rankings
```

### 🏆 Matches

```bash
# Add a match now
trueskill-cli matches add John,Erin

# Add a match with custom time
trueskill-cli matches add John,Erin --time 2025-05-01T15:00

# Team match
trueskill-cli matches add [John,Samantha],[Erin,Rodger]

# Edit or delete
trueskill-cli matches edit 5
trueskill-cli matches delete 5

# List match history
trueskill-cli matches
```

### ⏪ Undo

```bash
trueskill-cli undo
```

---

## 🔧 Configuration

You can override the default database file:

```bash
trueskill-cli --db-path my_league.db players
```

---

## 🔄 Development

### Install dependencies

```bash
./install-dependencies.sh    # Linux/macOS
install-dependencies.bat     # Windows
```

### Clean build artifacts

```bash
./clean.sh
clean.bat
```

### Rebuild executable

```bash
pyinstaller --onefile --add-data "schemas.sql:." main.py --name trueskill-cli
```

> Windows: use `;.` instead of `:.`

---

## 🛠 Build System (GitHub Actions)

Automatically builds for:

- Windows
- Linux

Releases are published for version tags (e.g., `v1.0.0`).

---

## 📄 License

GPL © [Drew Jensen](https://github.com/drewrjensen)

## 📚 Third-Party Licenses

This project includes:

- `trueskill` by Heungsub Lee, licensed under the MIT License.  
  See [`LICENSES_trueskill.txt`](./LICENSES_trueskill.txt) for details.

---

## 🙋 Support or Contribute

- Submit issues or feature requests via [GitHub Issues](https://github.com/drewrjensen/trueskill-cli/issues)
- Fork and submit pull requests
- All contributions are welcome!