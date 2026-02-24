# 🔬 Scientific Truth Machine (STM)

**Master Thesis Implementation - Sohom Chatterjee, MBA**

A hybrid AI system for clinical substantiation and brand integrity verification in nutraceutical products, compliant with EU Regulation (EC) No 1924/2006.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Data Collection](#data-collection)
- [Troubleshooting](#troubleshooting)
- [Web Dashboard (Coming Soon!)](#web-dashboard)

---

## 🎯 Overview

The STM system analyzes nutraceutical products across three dimensions:

1. **Module 1: Perception & Extraction**
   - OCR text extraction from product labels
   - Visual health signal detection (symbols, colors, shapes)
   - Nutrition facts parsing and normalization

2. **Module 2: Semantic Validation**
   - Health claim extraction and validation
   - Scientific evidence retrieval (PubMed)
   - EU legal compliance checking

3. **Module 3: Nutrition Analysis**
   - Anomaly detection in nutrition facts
   - Category-based comparison
   - Claim-nutrition consistency verification

**Output:** Scientific Integrity Score (0-100%) with risk level and recommendations.

---

## 🏗️ System Architecture
```
STM_APP/
├── data/
│   ├── raw/              # Put product images and PDFs here
│   ├── processed/        # Cleaned data (auto-generated)
│   └── results/          # Analysis results (auto-generated)
│
├── module1_perception/
│   ├── ocr_extractor.py
│   ├── visual_analyzer.py
│   └── nutrition_parser.py
│
├── module2_semantic/
│   ├── claim_validator.py
│   ├── legal_checker.py
│   └── evidence_retrieval.py
│
├── module3_nutrition/
│   ├── anomaly_detector.py
│   └── category_comparison.py
│
├── database/
│   └── unified_db.py     # SQLite database
│
├── venv/                 # Virtual environment (DO NOT DELETE!)
├── config.py             # System settings
├── main.py               # Main controller
└── requirements.txt      # Dependencies
```

---

## 💻 Installation

### Prerequisites

- macOS (M1/M2 chip)
- Python 3.9+
- Tesseract OCR
- Homebrew

### First-Time Setup (Already Done!)

✅ Virtual environment created  
✅ All libraries installed  
✅ Tesseract OCR installed  
✅ Database initialized  

---

## 🚀 Quick Start

### Every Time You Work on This Project:

**Step 1: Open VS Code**
```bash
# Navigate to project folder
cd ~/Desktop/STM/STM_APP

# Open in VS Code
code .
```

**Step 2: Open Terminal in VS Code**

Press: `Ctrl + `` (backtick key)

**Step 3: Activate Virtual Environment**
```bash
source venv/bin/activate
```

✅ You should see `(venv)` at the start of your prompt!

**Step 4: Run STM**
```bash
python3 main.py
```

---

## 📖 Usage Guide

### Analyzing a Single Product

Create a Python script or use the interactive Python shell:
```python
from main import ScientificTruthMachine

# Initialize STM
stm = ScientificTruthMachine()

# Define product
product = {
    'name': 'Vitamin C 1000mg',
    'category': 'supplements',
    'brand': 'HealthCo',
    'image_path': 'data/raw/vitamin_c_label.jpg',
    'text': 'Supports immune health. High in Vitamin C.',
    'nutrition': {
        'energy_kcal': 15,
        'fat': 0,
        'saturated_fat': 0,
        'sugar': 3,
        'salt': 0.1,
        'protein': 0,
        'fiber': 0
    }
}

# Analyze
result = stm.analyze_product(product)

# Close when done
stm.close()
```

### Analyzing Multiple Products
```python
products = [
    {...},  # Product 1
    {...},  # Product 2
    {...},  # Product 3
]

results = stm.analyze_multiple_products(products)
```

---

## 📸 Data Collection

### What You Need for Each Product:

1. **Product Image** (label/packaging)
   - Format: JPG, PNG
   - Quality: Clear, readable text
   - Save in: `data/raw/`

2. **Product Information**
   - Name
   - Category (supplements, protein bars, cereals, etc.)
   - Brand
   - Marketing text (from webpage or label)

3. **Nutrition Facts** (per 100g)
   - Energy (kcal)
   - Fat, Saturated fat
   - Carbohydrates, Sugar
   - Protein
   - Fiber
   - Salt

### Data Collection Tips:

✅ **Take clear photos** of product labels  
✅ **Screenshot product webpages** as PDFs  
✅ **Organize by category** (create subfolders in `data/raw/`)  
✅ **Name files clearly** (e.g., `vitaminc_healthco_front.jpg`)  
✅ **Collect 20-30 products minimum** for good statistical analysis  

### Recommended Product Categories:

- Vitamin/mineral supplements
- Protein bars
- Breakfast cereals
- Yogurt drinks
- Functional beverages
- Probiotic supplements

---

## 🔧 Troubleshooting

### Issue: `(venv)` doesn't appear

**Solution:**
```bash
source venv/bin/activate
```

### Issue: "Module not found" error

**Solution:**
```bash
# Make sure venv is activated!
source venv/bin/activate

# Reinstall if needed
pip install -r requirements.txt
```

### Issue: Tesseract not found

**Solution:**
```bash
brew install tesseract
```

### Issue: Database locked

**Solution:**
```bash
# Close any running STM instances
# Delete database and recreate
rm database/stm_database.db
python3 main.py  # This recreates it
```

### Issue: Internet connection required

**Note:** PubMed API searches require internet. If offline, semantic validation will show "no evidence found" but system will still work.

---

## 🌐 Web Dashboard (Coming Soon!)

**Features in Development:**

✅ Drag-and-drop product image upload  
✅ Web form for nutrition input  
✅ Real-time analysis  
✅ Interactive charts and visualizations  
✅ PDF report generation  
✅ Product comparison tool  
✅ Shareable link for your thesis guide  

**Technology:** Streamlit (Python-based, FREE!)

**Timeline:** To be built this week!

---

## 📊 Understanding Results

### Scientific Integrity Score

- **85-100%** (Low Risk): Product appears compliant
- **70-84%** (Moderate Risk): Minor issues detected
- **50-69%** (High Risk): Significant compliance risks
- **0-49%** (Critical Risk): Do NOT place on market

### Risk Categories

1. **Semantic Score:** Are claims scientifically supported?
2. **Legal Score:** Are claims EU-legal?
3. **Nutrition Score:** Do nutrition facts match claims?

### Example Output
```
📊 SCORES:
   Semantic Validation:  85.0%
   Legal Compliance:     90.0%
   Nutrition Consistency: 100.0%
   ─────────────────────────────
   FINAL INTEGRITY SCORE: 88.3%
   ─────────────────────────────

✅ RISK LEVEL: LOW

💡 RECOMMENDATION:
   Product appears compliant. Review approved for market entry.
```

---

## 🎓 For Your Thesis

### Key Files for Analysis:

- **Database:** `database/stm_database.db` (all results stored here)
- **Results:** Query database for charts and statistics
- **Reports:** Generate from STM output

### Suggested Analysis:

1. Analyze 20-30 real nutraceutical products
2. Calculate average integrity scores by category
3. Identify most common violations
4. Compare claim types (disease prevention vs. body function)
5. Visualize: scores distribution, risk levels, category comparison

---

## ❓ Need Help?

**Common Commands:**
```bash
# Activate venv
source venv/bin/activate

# Run STM
python3 main.py

# Check Python version
python3 --version

# List installed packages
pip list

# Deactivate venv (when done)
deactivate
```

---

## 📝 Important Notes

⚠️ **ALWAYS activate venv before running!**  
⚠️ **DO NOT delete the venv folder!**  
⚠️ **Keep backups of your data!**  
⚠️ **Internet required for PubMed searches**  

---

## 🎯 Next Steps

1. ✅ System is built and working
2. 📸 Collect real product data (this week)
3. 🌐 Build web dashboard (this week)
4. 📊 Run analysis on collected data
5. 📈 Generate charts and statistics
6. 📄 Write thesis results section
7. 🎓 Present to guide with live demo!

---

**Built with:** Python, TensorFlow, scikit-learn, OpenCV, Tesseract OCR, SQLite  
**FREE Tools:** PubMed API, EU Health Claims Register, Open Food Facts  

**Good luck with your thesis! 🌟**