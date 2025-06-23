import streamlit as st
import pandas as pd

# Streamlit app: Shopify CSV generator with proper global handle sequencing
st.set_page_config(page_title="Shopify Import Builder", layout="centered")
st.title("🛍️ Shopify Import CSV Builder with Exploded Variants & Sequenced Handles")

st.markdown(
    "Upload your CSV/Excel with columns: title, description, product category, type, published, sizes (comma-separated), colours (comma-separated), product code, Variant Inventory Tracker, Variant Inventory Qty, Variant Inventory Policy, Variant Price, Variant Compare At Price, Status."
)

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file is not None:
    try:
        # 1) Load data
        if uploaded_file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.success("File loaded successfully!")

        # 2) Slugify titles
        df['_base_handle'] = (
            df['title'].str.strip()
                       .str.replace(r"\s+", "-", regex=True)
                       .str.lower()
        )
        # 3) Assign a global sequence per unique product
        unique_handles = df['_base_handle'].unique()
        handle_map = {h: str(i+1).zfill(2) for i, h in enumerate(unique_handles)}
        df['_serial'] = df['_base_handle'].map(handle_map)
        df['Handle'] = df['_base_handle'] + '-' + df['_serial']

        # 4) Split sizes/colors into lists and explode
        df['sizes_list'] = df['size'].str.split(r"\s*,\s*")
        df['colours_list'] = df['colour'].str.split(r"\s*,\s*")
        df = df.explode('sizes_list').explode('colours_list')

        # 5) Build Shopify DataFrame
        out = pd.DataFrame({
            "Handle": df['Handle'],
            "Title": df['title'],
            "Body (HTML)": "<p>" + df['description'].fillna('') + "</p>",
            "Vendor": "YourBrandName",
            "Product Category": df.get('product category', ''),
            "Type": df.get('type', ''),
            "Tags": df['description'].fillna('') + "," + df.get('product category',''),
            "Published": df['published'].map(lambda x: 'TRUE' if str(x).strip().lower()=='active' else 'FALSE'),
            "Option1 Name": '',
            "Option1 Value": df['sizes_list'],
            "Option1 Linked To": '',
            "Option2 Name": '',
            "Option2 Value": df['colours_list'],
            "Option2 Linked To": '',
            "Option3 Name": '',
            "Option3 Value": '',
            "Option3 Linked To": '',
            "Variant SKU": df['product code'] + '-' + df['sizes_list'],
            "Variant Grams": 0,
            "Variant Inventory Tracker": df.get('Variant Inventory Tracker', ''),
            "Variant Inventory Qty": df.get('Variant Inventory Qty', 0),
            "Variant Inventory Policy": df.get('Variant Inventory Policy',''),
            "Variant Fulfillment Service": 'manual',
            "Variant Price": df.get('Variant Price', 0),
            "Variant Compare At Price": df.get('Variant Compare At Price', 0),
            "Variant Requires Shipping": 'TRUE',
            "Variant Taxable": 'TRUE',
            "Status": df.get('Status','')
        })

        # 6) Only show option names on first variant row per handle
        grp = out.groupby('Handle').cumcount()
        out.loc[grp == 0, 'Option1 Name'] = 'Size'
        out.loc[grp == 0, 'Option2 Name'] = 'Color'

        # 7) Preview & Download
        st.subheader("Preview of Generated Shopify CSV")
        st.dataframe(out.head(10))

        csv = out.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Shopify-ready CSV",
            data=csv,
            file_name="shopify_ready.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Awaiting CSV or Excel file upload...")
