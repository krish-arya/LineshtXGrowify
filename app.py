# streamlit_app.py
import os, time, json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from google import genai

# ── 1) Init GenAI Client ──────────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# ── 2) Enhanced UI Setup ─────────────────────────────────────────────
st.set_page_config(
    page_title="Shopify Import Builder", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .step-header {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .variant-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    .ai-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .ai-enabled { background-color: #d4edda; color: #155724; }
    .ai-disabled { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🛍️ Advanced Shopify CSV Builder</h1>
    <p>Transform your product data into Shopify-ready imports with AI-powered descriptions and smart inventory management</p>
</div>
""", unsafe_allow_html=True)

# AI Status Check
if not GEMINI_API_KEY:
    st.markdown('<div class="ai-status ai-disabled">⚠️ AI Features Disabled - Missing GEMINI_API_KEY</div>', unsafe_allow_html=True)
    ai_enabled = False
else:
    st.markdown('<div class="ai-status ai-enabled">✅ AI Features Enabled - Gemini 2.5 Flash Ready</div>', unsafe_allow_html=True)
    client = genai.Client(api_key=GEMINI_API_KEY)
    ai_enabled = True

# ── 3) Enhanced Sidebar Configuration ──────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Processing mode selection
    mode = st.radio(
        "🤖 AI Processing Mode:",
        options=[
            "Default template (no AI)",
            "Simple mode (first sentence + tags)",
            "Full AI mode (custom description + tags)"
        ],
        index=0 if not ai_enabled else 2,
        disabled=not ai_enabled,
        help="Choose how you want to process product descriptions"
    )
    
    st.markdown("---")
    
    # Brand customization
    st.markdown("### 🏢 Brand Settings")
    vendor_name = st.text_input("Vendor Name", value="YourBrandName", help="This will appear as the vendor in Shopify")
    
    # Quantity settings
    st.markdown("### 📦 Inventory Settings")
    default_qty = st.number_input("Default Quantity per Variant", min_value=0, value=10, step=1)
    bulk_qty_mode = st.checkbox("Enable Bulk Quantity Setting", help="Set same quantity for all variants")
    
    if bulk_qty_mode:
        bulk_qty = st.number_input("Bulk Quantity", min_value=0, value=default_qty, step=1)
    
    st.markdown("---")
    
    # File format info
    with st.expander("📋 Required Columns", expanded=False):
        st.markdown("""
        **Essential columns:**
        - `title` - Product name
        - `description` - Product description
        - `size` - Sizes (comma-separated)
        - `colour` - Colors (comma-separated)
        - `product code` - SKU base
        - `product category` - Category
        - `type` - Product type
        - `published` - Status (active/inactive)
        """)

# ── 4) File Upload Section ──────────────────────────────────────────
st.markdown('<div class="step-header"><h2>📁 Step 1: Upload Your Product Data</h2></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose your CSV or Excel file",
        type=["csv", "xlsx"],
        help="Upload a file containing your product data"
    )

with col2:
    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.metric("File Size", f"{file_size:.1f} KB")

with col3:
    if uploaded_file:
        file_type = "Excel" if uploaded_file.name.lower().endswith(".xlsx") else "CSV"
        st.metric("File Type", file_type)

if not uploaded_file:
    st.info("👆 Please upload a CSV or Excel file to get started")
    st.stop()

# ── 5) Load & Preview Data ──────────────────────────────────────────
try:
    df_raw = pd.read_excel(uploaded_file) if uploaded_file.name.lower().endswith(".xlsx") else pd.read_csv(uploaded_file)
    
    # Display success metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Total Products</p></div>'.format(len(df_raw)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Columns</p></div>'.format(len(df_raw.columns)), unsafe_allow_html=True)
    with col3:
        total_variants = sum(len(str(row.get('size', '')).split(',')) * len(str(row.get('colour', '')).split(',')) for _, row in df_raw.iterrows())
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Est. Variants</p></div>'.format(total_variants), unsafe_allow_html=True)
    with col4:
        active_products = sum(1 for _, row in df_raw.iterrows() if str(row.get('published', '')).lower() == 'active')
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Active Products</p></div>'.format(active_products), unsafe_allow_html=True)
    
    # Data preview with tabs
    tab1, tab2 = st.tabs(["📊 Data Preview", "🔍 Column Analysis"])
    
    with tab1:
        st.dataframe(df_raw.head(10), use_container_width=True)
    
    with tab2:
        col_analysis = pd.DataFrame({
            'Column': df_raw.columns,
            'Data Type': df_raw.dtypes,
            'Non-Null Count': df_raw.count(),
            'Null Count': df_raw.isnull().sum(),
            'Sample Value': [str(df_raw[col].iloc[0]) if len(df_raw) > 0 else 'N/A' for col in df_raw.columns]
        })
        st.dataframe(col_analysis, use_container_width=True)

except Exception as e:
    st.error(f"❌ Could not load file: {e}")
    st.stop()

# ── 6) AI Helper Functions ──────────────────────────────────────────
def refine_and_tag(text: str) -> tuple[str, str]:
    if not ai_enabled:
        return text, ""
    
    prompt = (
        "You are a top-tier Shopify copywriter.\n"
        "1) Rewrite this product description to be clear, engaging, and on-brand.\n"
        "2) Then output on the next line exactly five comma-separated tags.\n\n"
        f"Original description:\n\"\"\"\n{text}\n\"\"\"\n\n"
        "Respond with exactly two lines:\n"
        "- Line 1: your rewritten description\n"
        "- Line 2: tag1,tag2,tag3,tag4,tag5"
    )
    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        parts = (resp.text or "").strip().split("\n", 1)
        return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")
    except Exception as e:
        st.warning(f"AI processing failed: {e}")
        return text, ""

def tags_only(text: str) -> str:
    if not ai_enabled:
        return ""
    
    prompt = (
        "You are an expert Shopify copywriter.\n"
        "Suggest exactly five comma-separated Shopify tags for this product description:\n\n"
        f"\"\"\"\n{text}\n\"\"\"\n\n"
        "Respond with a single line:\n"
        "tag1,tag2,tag3,tag4,tag5"
    )
    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return (resp.text or "").strip()
    except Exception as e:
        st.warning(f"AI tag generation failed: {e}")
        return ""

# ── 7) Processing Section ──────────────────────────────────────────
st.markdown('<div class="step-header"><h2>🚀 Step 2: Process Your Data</h2></div>', unsafe_allow_html=True)

process_button = st.button("🔄 Start Processing", type="primary", use_container_width=True)

if process_button or 'processed_data' in st.session_state:
    
    # Only do AI processing if button was clicked (not on rerun)
    if process_button:
        df = df_raw.copy()
        n = len(df)
        
        # Processing progress with detailed status
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            custom_descs, all_tags = [], []

            with st.spinner("🔮 AI is working its magic..."):
                for i, (_, row) in enumerate(df.iterrows()):
                    status_text.text(f"Processing product {i+1}/{n}: {row.get('title', 'Unknown')[:30]}...")
                    
                    original = row.get("description", "") or ""
                    if mode == "Default template (no AI)":
                        desc = f"{row.get('title', '').strip()} - {row.get('product category', '').strip()}"
                        tags = ""
                    elif mode == "Simple mode (first sentence + tags)":
                        first_sent = original.split(".", 1)[0].strip()
                        desc = first_sent
                        tags = tags_only(first_sent)
                    else:
                        desc, tags = refine_and_tag(original)

                    custom_descs.append(desc)
                    all_tags.append(tags)
                    progress_bar.progress((i + 1) / n)
                    time.sleep(0.1)  # Reduced sleep time

            status_text.text("✅ AI processing complete!")

        df["custom_description"] = custom_descs
        df["ai_tags"] = all_tags

        # Explode variants - Fixed approach
        df_exploded_list = []
        for _, row in df.iterrows():
            sizes = [s.strip() for s in str(row.get("size", "")).split(",") if s.strip()]
            colors = [c.strip() for c in str(row.get("colour", "")).split(",") if c.strip()]
            
            # If no sizes or colors, create default entries
            if not sizes:
                sizes = [""]
            if not colors:
                colors = [""]
            
            # Create all combinations
            for size in sizes:
                for color in colors:
                    new_row = row.copy()
                    new_row["sizes_list"] = size
                    new_row["colours_list"] = color
                    df_exploded_list.append(new_row)
        
        df = pd.DataFrame(df_exploded_list)
        
        # Store processed data in session state
        st.session_state.processed_data = df
        st.session_state.variant_quantities = {}
    else:
        # Use existing processed data
        df = st.session_state.processed_data

    # ── 8) Interactive Quantity Management ──────────────────────────────
    st.markdown('<div class="step-header"><h2>🧮 Step 3: Set Inventory Quantities</h2></div>', unsafe_allow_html=True)
    
    # Get unique variants with better handling - only once
    if 'unique_variants_processed' not in st.session_state:
        unique_variants = []
        variant_products = {}
        
        for _, row in df.iterrows():
            size = str(row['sizes_list']).strip()
            color = str(row['colours_list']).strip()
            title = str(row['title']).strip()
            
            variant_key = (size, color, title)
            if variant_key not in unique_variants:
                unique_variants.append(variant_key)
                variant_products[variant_key] = title
        
        st.session_state.unique_variants = unique_variants
        st.session_state.variant_products = variant_products
        st.session_state.unique_variants_processed = True
    else:
        unique_variants = st.session_state.unique_variants
        variant_products = st.session_state.variant_products
    
    # Initialize quantities if not exists
    if 'variant_quantities' not in st.session_state:
        st.session_state.variant_quantities = {}
        # Pre-populate with defaults
        for size, color, title in unique_variants:
            variant_key = f"{size}|{color}|{title}"
            st.session_state.variant_quantities[variant_key] = default_qty
    
    if bulk_qty_mode:
        st.info(f"📦 Bulk mode enabled: Setting {bulk_qty} for all variants")
        # Update all quantities at once
        for size, color, title in unique_variants:
            variant_key = f"{size}|{color}|{title}"
            st.session_state.variant_quantities[variant_key] = bulk_qty
    else:
        # Group variants by product for better organization - cache this too
        if 'products_variants_grouped' not in st.session_state:
            products_variants = {}
            for size, color, title in unique_variants:
                if title not in products_variants:
                    products_variants[title] = []
                products_variants[title].append((size, color))
            st.session_state.products_variants_grouped = products_variants
        else:
            products_variants = st.session_state.products_variants_grouped
        
        # Quick bulk update option
        col1, col2 = st.columns([1, 1])
        with col1:
            quick_qty = st.number_input("🚀 Quick Set All", min_value=0, value=default_qty, step=1, key="quick_qty")
        with col2:
            if st.button("Apply to All Variants", key="apply_all", use_container_width=True):
                for size, color, title in unique_variants:
                    variant_key = f"{size}|{color}|{title}"
                    st.session_state.variant_quantities[variant_key] = quick_qty
                st.success(f"✅ Set all variants to {quick_qty}")
                st.rerun()
        
        # Fast input mode - use forms to batch updates
        st.markdown("### Individual Variant Settings")
        
        # Create expandable sections for each product
        for product_title, variants in products_variants.items():
            with st.expander(f"📦 {product_title} ({len(variants)} variants)", expanded=len(products_variants) <= 2):
                
                # Use form for batch updates per product
                with st.form(key=f"form_{hash(product_title) % 10000}"):
                    # Use columns for better layout
                    num_cols = min(4, len(variants))  # More columns for faster input
                    if num_cols > 0:
                        cols = st.columns(num_cols)
                        
                        variant_inputs = {}
                        for idx, (size, color) in enumerate(variants):
                            with cols[idx % num_cols]:
                                variant_key = f"{size}|{color}|{product_title}"
                                current_qty = st.session_state.variant_quantities.get(variant_key, default_qty)
                                
                                # Simpler display, faster input
                                qty = st.number_input(
                                    f"{size} / {color}",
                                    min_value=0, 
                                    value=int(current_qty), 
                                    step=1, 
                                    key=f"form_qty_{variant_key}_{hash(variant_key) % 10000}"
                                )
                                variant_inputs[variant_key] = qty
                    
                    # Submit button for this product
                    if st.form_submit_button(f"Update {product_title}", use_container_width=True):
                        # Batch update all variants for this product
                        for variant_key, qty in variant_inputs.items():
                            st.session_state.variant_quantities[variant_key] = qty
                        st.success(f"✅ Updated quantities for {product_title}")
        
        # Alternative: Fast table-based input for power users
        with st.expander("⚡ Power User: Table Input Mode", expanded=False):
            st.markdown("*Copy/paste friendly bulk editing*")
            
            # Create a dataframe for editing
            variant_data = []
            for size, color, title in unique_variants:
                variant_key = f"{size}|{color}|{title}"
                variant_data.append({
                    'Product': title,
                    'Size': size if size else 'N/A',
                    'Color': color if color else 'N/A',
                    'Quantity': st.session_state.variant_quantities.get(variant_key, default_qty),
                    'Key': variant_key
                })
            
            variant_df = pd.DataFrame(variant_data)
            
            # Use data editor for super fast editing
            edited_variants = st.data_editor(
                variant_df[['Product', 'Size', 'Color', 'Quantity']], 
                hide_index=True,
                use_container_width=True,
                key="variant_editor"
            )
            
            if st.button("Apply Table Changes", key="apply_table"):
                for i, (variant_key, new_qty) in enumerate(zip(variant_df['Key'], edited_variants['Quantity'])):
                    st.session_state.variant_quantities[variant_key] = int(new_qty)
                st.success("✅ Applied all table changes!")
                st.rerun()

    # Apply quantities to dataframe - much faster vectorized approach
    variant_qty_map = st.session_state.variant_quantities
    
    # Create a fast lookup series
    df["_variant_key"] = (df["sizes_list"].astype(str).str.strip() + "|" + 
                          df["colours_list"].astype(str).str.strip() + "|" + 
                          df["title"].astype(str).str.strip())
    
    df["Variant Inventory Qty"] = df["_variant_key"].map(variant_qty_map).fillna(0).astype(int)

    # Generate handles and build final dataset - optimized
    df["_base_handle"] = (df["title"].astype(str).str.strip()
                         .str.replace(r"[^\w\s-]", "", regex=True)  # Remove special chars
                         .str.replace(r"\s+", "-", regex=True)      # Replace spaces
                         .str.lower())
    
    # Create unique serials for each unique handle - vectorized
    unique_handles = df["_base_handle"].unique()
    handle_serial_map = {h: str(idx+1).zfill(2) for idx, h in enumerate(unique_handles)}
    df["_serial"] = df["_base_handle"].map(handle_serial_map)
    df["Handle"] = df["_base_handle"] + "-" + df["_serial"]

    # Build final Shopify dataset with better error handling
    out = pd.DataFrame({
        "Handle": df["Handle"],
        "Title": df["title"],
        "Body (HTML)": "<p>" + df["custom_description"].astype(str) + "</p>",
        "Vendor": vendor_name,
        "Product Category": df.get("product category", pd.Series(dtype=str)).fillna(""),
        "Type": df.get("type", pd.Series(dtype=str)).fillna(""),
        "Tags": df["ai_tags"],
        "Published": df.get("published", pd.Series(dtype=str)).astype(str).str.lower().eq("active").map({True:"TRUE",False:"FALSE"}),
        "Option1 Name": "Size",
        "Option1 Value": df["sizes_list"],
        "Option2 Name": "Color", 
        "Option2 Value": df["colours_list"],
        "Variant SKU": (df.get("product code", pd.Series(dtype=str)).fillna("").astype(str) + "-" + 
                       df["_serial"].astype(str) + "-" + 
                       df["sizes_list"].astype(str) + "-" + 
                       df["colours_list"].astype(str)),
        "Variant Grams": 0,
        "Variant Inventory Tracker": df.get("Variant Inventory Tracker", pd.Series(dtype=str)).fillna(""),
        "Variant Inventory Qty": df["Variant Inventory Qty"],
        "Variant Inventory Policy": df.get("Variant Inventory Policy", pd.Series(dtype=str)).fillna(""),
        "Variant Fulfillment Service": "manual",
        "Variant Price": pd.to_numeric(df.get("Variant Price", pd.Series(dtype=float)), errors='coerce').fillna(0),
        "Variant Compare At Price": pd.to_numeric(df.get("Variant Compare At Price", pd.Series(dtype=float)), errors='coerce').fillna(0),
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
        "Status": df.get("Status", pd.Series(dtype=str)).fillna("")
    })

    # ── 9) Results Display ──────────────────────────────────────────
    st.markdown('<div class="step-header"><h2>📊 Step 4: Review & Download</h2></div>', unsafe_allow_html=True)
    
    # Final statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Final Variants</p></div>'.format(len(out)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Total Inventory</p></div>'.format(int(out["Variant Inventory Qty"].sum())), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Unique Products</p></div>'.format(out["Handle"].nunique()), unsafe_allow_html=True)
    with col4:
        avg_price = out["Variant Price"].replace(0, pd.NA).mean()
        st.markdown('<div class="stats-box"><h3>{}</h3><p>Avg Price</p></div>'.format(f"${avg_price:.0f}" if pd.notna(avg_price) else "N/A"), unsafe_allow_html=True)

    # Tabbed results view
    tab1, tab2, tab3 = st.tabs(["📋 Final Preview", "📈 Inventory Summary", "🏷️ AI Tags Overview"])
    
    with tab1:
        st.dataframe(out.head(20), use_container_width=True)
    
    with tab2:
        try:
            inventory_summary = out.groupby(["Handle", "Title"]).agg({
                "Variant Inventory Qty": ["sum", "count"],
                "Variant Price": "first"
            }).round(2)
            inventory_summary.columns = ["Total Qty", "Variants", "Price"]
            st.dataframe(inventory_summary, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating inventory summary: {e}")
            st.dataframe(out[["Handle", "Title", "Variant Inventory Qty", "Variant Price"]], use_container_width=True)
    
    with tab3:
        if ai_enabled and mode != "Default template (no AI)":
            tags_df = out[out["Tags"] != ""][["Title", "Tags"]].drop_duplicates()
            st.dataframe(tags_df, use_container_width=True)
        else:
            st.info("No AI tags generated in current mode")

    # Download section
    csv_data = out.to_csv(index=False).encode("utf-8")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Shopify CSV",
            data=csv_data,
            file_name=f"shopify_import_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Process Another File", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Success message
    st.success("🎉 Your Shopify CSV is ready! The file contains all variants with proper inventory quantities.")
    
    # Usage tips
    with st.expander("💡 Next Steps & Tips"):
        st.markdown("""
        ### 📋 What to do next:
        1. **Download** your CSV file using the button above
        2. **Review** the data in Excel/Google Sheets if needed
        3. **Import** to Shopify via: Products → Import
        4. **Check** that all variants imported correctly
        
        ### ⚠️ Important Notes:
        - Make sure your Shopify store accepts the product categories used
        - Verify that all image URLs (if any) are accessible
        - Double-check pricing and inventory levels
        - Test with a small batch first if you have many products
        """)