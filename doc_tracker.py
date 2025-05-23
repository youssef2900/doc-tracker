import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Document Tracker", layout="wide")

# تحميل البيانات
try:
    df = pd.read_csv("documents.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "File Name", "Doc Ref", "Document Title", "Status", "Discipline",
        "File Type", "Rev Date", "Delivery Date", "Project", "Originator", "Project Stage"
    ])

status_options = [
    "A - Approved",
    "B - Approved with Comments",
    "C - Revise and Resubmit",
    "D - Rejected"
]

discipline_options = [
    "Architecture", "Civil", "Electrical", "Mechanical", "Surveying"
]

st.title("📁 Document Tracker")

# ✅ إضافة مستند جديد
with st.form("add_form"):
    st.subheader("➕ Add New Document")
    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("📄 File Name")
        doc_ref = st.text_input("📁 Document Ref")
        title = st.text_input("📝 Document Title")
        status = st.selectbox("📌 Status (Optional)", [""] + status_options)
        discipline = st.selectbox("📚 Discipline", ["Select..."] + discipline_options)
        file_type = st.text_input("📂 File Type")
    with col2:
        rev_date = st.date_input("🗓️ Revision Date", value=datetime.date.today())
        delivery_date = st.date_input("🚚 Delivery Date", value=datetime.date.today())
        project = st.text_input("🏗️ Project")
        originator = st.text_input("👤 Originator")
        stage = st.text_input("📶 Project Stage")
    submit = st.form_submit_button("💾 Save")

    if submit:
        if (not file_name or not doc_ref or not title or
            discipline == "Select..." or not file_type or
            not delivery_date or not project or not originator or not stage):
            st.warning("❗ Please fill in all required fields before saving.")
        else:
            new_row = {
                "File Name": file_name, "Doc Ref": doc_ref, "Document Title": title,
                "Status": status, "Discipline": discipline, "File Type": file_type,
                "Rev Date": rev_date, "Delivery Date": delivery_date,
                "Project": project, "Originator": originator, "Project Stage": stage
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv("documents.csv", index=False)
            st.success("✅ Document added successfully!")
            st.rerun()

# ✅ فلترة احترافية
with st.expander("🔎 Filter Documents"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_status = st.selectbox("Status", ["All"] + status_options)
    with col2:
        selected_discipline = st.selectbox("Discipline", ["All"] + discipline_options)
    with col3:
        selected_originator = st.selectbox("Originator", ["All"] + df["Originator"].dropna().unique().tolist())
    with col4:
        selected_doc_ref = st.selectbox("Document Ref", ["All"] + df["Doc Ref"].dropna().unique().tolist())

    filtered_df = df.copy()
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["Status"] == selected_status]
    if selected_discipline != "All":
        filtered_df = filtered_df[filtered_df["Discipline"] == selected_discipline]
    if selected_originator != "All":
        filtered_df = filtered_df[filtered_df["Originator"] == selected_originator]
    if selected_doc_ref != "All":
        filtered_df = filtered_df[filtered_df["Doc Ref"] == selected_doc_ref]
    st.dataframe(filtered_df)

# ✅ عرض وتعديل المستندات - شكل احترافي
st.subheader("📝 Manage Documents")

for i, row in df.iterrows():
    st.markdown(f"""
    <div style="box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding:15px; margin-bottom:10px;
                border-left: 6px solid {'#e74c3c' if row['Status'] in ['C - Revise and Resubmit', 'D - Rejected'] else '#2ecc71'};
                background-color:#fff; border-radius: 6px;">
        <h4 style="margin:0;">📄 {row['File Name']}</h4>
        <p style="margin:0;"><b>Status:</b> {row['Status'] or 'Not Set'} | <b>Discipline:</b> {row['Discipline']}</p>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("✏️ Edit or Delete"):
        edited_row = {col: st.text_input(f"{col}", value=str(row[col]), key=f"{col}_{i}") for col in df.columns}
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save Changes", key=f"save_{i}"):
                for col in df.columns:
                    df.at[i, col] = edited_row[col]
                df.to_csv("documents.csv", index=False)
                st.success("✅ Changes saved!")
                st.rerun()
        with col2:
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                df.drop(index=i, inplace=True)
                df.reset_index(drop=True, inplace=True)
                df.to_csv("documents.csv", index=False)
                st.warning("🗑️ Document deleted.")
                st.rerun()
