# 🛍️ Shopify Import Builder with AI

An advanced, AI-enhanced Streamlit web app that transforms raw product data (CSV/Excel) into a **Shopify-compatible CSV** file — complete with product variants, smart inventory controls, and **AI-generated descriptions and tags** using Google Gemini.

---

## 🚀 Features

- ✅ Upload product data in `.csv` or `.xlsx`
- ✅ Preview and analyze columns
- ✅ Generate SEO-optimized product descriptions with **Gemini AI**
- ✅ Create 5 Shopify tags per product automatically
- ✅ Smart variant generation (Size × Color)
- ✅ Dynamic quantity management for each variant
- ✅ Fully exportable, ready-to-import **Shopify CSV**
- ✅ Beautiful, responsive UI powered by Streamlit and custom CSS

---

## 🧠 AI Modes

You can choose from:
- **Default template** — No AI, just structured formatting
- **Simple mode** — Uses the first sentence + AI-generated tags
- **Full AI mode** — Rewrites description + adds 5 smart tags

---

## 📋 Required Columns in Your Input File

Make sure your input `.csv` or `.xlsx` file contains the following columns:

- `title` – Product name  
- `description` – Raw product description  
- `size` – Sizes (comma-separated, e.g. `S,M,L`)  
- `colour` – Colors (comma-separated, e.g. `Red,Blue`)  
- `product code` – SKU base  
- `product category` – Category name  
- `type` – Product type  
- `published` – Status: `active` or `inactive`

---

## 🧪 Quick Start (Installation + Run)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/shopify-import-builder.git
cd shopify-import-builder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Google Gemini API key
# Option 1: Create a .env file with this content:
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env

# Option 2 (alt): export it directly in terminal (Linux/macOS)
export GEMINI_API_KEY=your_gemini_api_key_here

# 4. Run the Streamlit app
streamlit run app.py
