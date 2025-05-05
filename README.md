# 🧲 AHP Façade Ranking Tool

Rank façade design alternatives with interactive AHP logic using data from Google Sheets and visualize results with Streamlit.

**Applied using:** Python · Streamlit · Plotly · AHPy

---

## 📋 Table of Contents

* [Why this exists](#-why-this-exists)
* [Process Overview](#-process-overview)
* [How it works (TL;DR)](#-how-it-works-tldr)
* [Repository Layout](#-repository-layout)
* [Quick Start](#-quick-start)
* [Detailed Workflow](#-detailed-workflow)
* [Implementation Decisions](#-implementation-decisions)
* [Limitations & Future Work](#-limitations--future-work)
* [References](#-references)

---

## ✨ Why this exists

This tool supports early-stage decision making in façade design by ranking alternatives based on environmental impact, cost, and performance. It helps designers explore trade-offs and justify selections using both objective performance data and subjective stakeholder preferences.

---

## 🚦 Process Overview

1. 📊 Pulls façade data from multiple Google Sheets.
2. 🧮 Normalizes performance indicators.
3. ⚖️ Applies Analytic Hierarchy Process (AHP) to rank alternatives.
4. 🖼️ Displays ranking table and image grid.
5. 📈 Shows parallel coordinates plot to visualize trade-offs.

---

## ⚙️ How it works (TL;DR)

* Sub-criteria are grouped under three top-level categories.
* Data is normalized and pairwise comparisons are calculated.
* AHPy builds the full AHP tree.
* Streamlit sliders let users adjust weights in real time.
* Outputs include a ranked table, images, and a parallel plot.

---

## 🗂️ Repository Layout

```
.
├─ app/
│  └─ facade_ahp.py            # Main Streamlit app
├─ images/
│  └─ <Alternative>.png        # Image files for each alternative
├─ requirements.txt            # Python dependencies
└─ README.md                   # You're reading it!
```

---

## ⚡ Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/facade-ahp-tool.git
cd facade-ahp-tool

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/facade_ahp.py
```

---

## 🔍 Detailed Workflow

| Step | Script/File     | What it does                                     |
| ---- | --------------- | ------------------------------------------------ |
| 1    | `facade_ahp.py` | Loads Google Sheet data and normalizes values    |
| 2    | `facade_ahp.py` | Applies AHP with ahpy for each criteria level    |
| 3    | `facade_ahp.py` | Renders ranking table, image grid, and PCP chart |

Debug tip: If images don't load, check that your `images/` folder has the right filenames matching `Alternative`.

---

## 🛠 Implementation Decisions

| Decision                               | Why                                              | Alternatives                       |
| -------------------------------------- | ------------------------------------------------ | ---------------------------------- |
| Use Google Sheets                      | Dynamic update of input data without redeploying | Local CSVs or database             |
| Use AHPy                               | Simple integration with Streamlit                | Custom pairwise matrix logic       |
| Normalize on load                      | Ensures fair comparison                          | Use raw values, harder to compare  |
| Separate slider for each sub-criterion | Fine-tuned control                               | Simpler UI with group weights only |

---

## ⚠️ Limitations & Future Work

### Known Limitations

* No error handling for invalid/missing image files.
* One AHP tree per run (no multiple stakeholder support yet).

### Future Improvements

* Add export of final scores to CSV.
* Enable user uploads of CSV instead of hardcoded URLs.
* Add login & save presets for stakeholder profiles.
* More sophisticated normalization options.

---

## 📚 References

* [AHPy Docs](https://github.com/robbieaverill/ahpy)
* [Streamlit](https://docs.streamlit.io/)
* [Saaty's AHP Method](https://en.wikipedia.org/wiki/Analytic_hierarchy_process)
* [Google Sheets CSV Export Guide](https://support.google.com/docs/answer/9143383)
