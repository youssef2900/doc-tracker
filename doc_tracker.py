import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="📁 Document Tracker", layout="wide")

# تحميل البيانات
try:
    df = pd.read_csv("documents.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "File Name", "Doc Ref", "Document Title", "Status", "Discipline",
        "File Type", "Rev Date", "Delivery Date", "Project", "Originator", "Project Stage"
    ])

# القوائم المنسدلة
status_options = ["", "A - Approved", "B - Approved with Comments", "C - Revise and Resubmit", "D - Rejected"]
discipline_options = ["Architecture", "Civil", "Electrical", "Mechanical", "Surveying"]

# عنوان التطبيق
st.markdown("<h1 style='text-align:center;'>📁 Document Tracker</h1>", unsafe_allow_html=True)
st.markdown("---")

# ➕ إضافة مستند
with st.form("add_doc"):
    st.subheader("➕ Add New Document")
    c1, c2 = st.columns(2)
    with c1:
        file_name = st.text_input("📄 File Name")
        doc_ref = st.text_input("📁 Document Ref")
        title = st.text_input("📝 Document Title")
        status = st.selectbox("📌 Status (Optional)", status_options)
        discipline = st.selectbox("📚 Discipline", discipline_options)
        file_type = st.text_input("📂 File Type")
    with c2:
        rev_date = st.date_input("🗓️ Rev Date", value=datetime.date.today())
        delivery_date = st.date_input("📦 Delivery Date", value=datetime.date.today())
        project = st.text_input("🏗️ Project")
        originator = st.text_input("👤 Originator")
        stage = st.text_input("📶 Project Stage")
    save_btn = st.form_submit_button("💾 Save Document")

    if save_btn:
        if not all([file_name, doc_ref, title, discipline, file_type, project, originator, stage]):
            st.warning("🚨 Please fill all required fields before saving.")
        else:
            df = pd.concat([df, pd.DataFrame([{
                "File Name": file_name, "Doc Ref": doc_ref, "Document Title": title,
                "Status": status, "Discipline": discipline, "File Type": file_type,
                "Rev Date": rev_date, "Delivery Date": delivery_date,
                "Project": project, "Originator": originator, "Project Stage": stage
            }])], ignore_index=True)
            df.to_csv("documents.csv", index=False)
            st.success("✅ Document saved successfully!")
            st.rerun()

# 📋 عرض كل المستندات مع التعديل والحذف
st.subheader("🗂️ All Documents")
if df.empty:
    st.info("🚫 No documents found.")
else:
    for i, row in df.iterrows():
        with st.expander(f"📄 {row['File Name']}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fn = st.text_input("File Name", row["File Name"], key=f"fn_{i}")
                dr = st.text_input("Doc Ref", row["Doc Ref"], key=f"dr_{i}")
                dt = st.text_input("Document Title", row["Document Title"], key=f"dt_{i}")
            with c2:
                stt = st.selectbox("Status", status_options, index=status_options.index(row["Status"] if row["Status"] in status_options else ""), key=f"st_{i}")
                dis = st.selectbox("Discipline", discipline_options, index=discipline_options.index(row["Discipline"]) if row["Discipline"] in discipline_options else 0, key=f"dis_{i}")
                ft = st.text_input("File Type", row["File Type"], key=f"ft_{i}")
            with c3:
                rv = st.date_input("Rev Date", datetime.datetime.strptime(row["Rev Date"], "%Y-%m-%d"), key=f"rv_{i}")
                dd = st.date_input("Delivery Date", datetime.datetime.strptime(row["Delivery Date"], "%Y-%m-%d"), key=f"dd_{i}")
                pr = st.text_input("Project", row["Project"], key=f"pr_{i}")
                org = st.text_input("Originator", row["Originator"], key=f"org_{i}")
                stg = st.text_input("Project Stage", row["Project Stage"], key=f"ps_{i}")

            col1, col2 = st.columns([1, 1])
            if col1.button("✅ Save Changes", key=f"save_{i}"):
                df.at[i, "File Name"] = fn
                df.at[i, "Doc Ref"] = dr
                df.at[i, "Document Title"] = dt
                df.at[i, "Status"] = stt
                df.at[i, "Discipline"] = dis
                df.at[i, "File Type"] = ft
                df.at[i, "Rev Date"] = rv
                df.at[i, "Delivery Date"] = dd
                df.at[i, "Project"] = pr
                df.at[i, "Originator"] = org
                df.at[i, "Project Stage"] = stg
                df.to_csv("documents.csv", index=False)
                st.success("✅ Updated successfully!")
                st.rerun()

            if col2.button("🗑️ Delete", key=f"del_{i}"):
                df.drop(index=i, inplace=True)
                df.reset_index(drop=True, inplace=True)
                df.to_csv("documents.csv", index=False)
                st.warning("🗑️ Document deleted!")
                st.rerun()

# 📦 تصدير البيانات
st.subheader("⬇️ Export Data")

col_pdf, col_csv = st.columns(2)

# 📄 PDF
with col_pdf:
    if st.button("📄 Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="📋 All Documents", ln=True, align="C")

        for i, row in df.iterrows():
            line = f"{row['File Name']} | {row['Doc Ref']} | {row['Document Title']} | {row['Status']}"
            pdf.cell(200, 8, txt=line, ln=True)

        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        st.download_button("⬇️ Download PDF", pdf_buffer.getvalue(), file_name="documents.pdf")

# 📊 CSV
with col_csv:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, file_name="documents.csv", mime="text/csv")
