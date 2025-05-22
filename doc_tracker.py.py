import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="Document Tracker", layout="wide")

# تحميل البيانات
try:
    df = pd.read_csv("documents.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "File Name", "Doc Ref", "Document Title", "Status", "Discipline",
        "File Type", "Rev Date", "Purpose of Issue", "Project", "Originator", "Project Stage"
    ])

status_options = [
    "Draft", "In Review", "Rejected", "Final",
    "A - Approved", "B - Approved with Comments",
    "C - Revise and Resubmit", "D - Rejected"
]

discipline_options = [
    "Architecture", "Civil", "Electrical", "Mechanical", "Surveying"
]

# ✅ إدخال بيانات جديدة
st.title("📁 Document Tracker")

with st.form("add_doc"):
    st.subheader("➕ Add New Document")
    file_name = st.text_input("File Name")
    doc_ref = st.text_input("Document Ref")
    title = st.text_input("Document Title")
    status = st.selectbox("Status", status_options)
    discipline = st.selectbox("Discipline", discipline_options)
    file_type = st.text_input("File Type")
    rev_date = st.date_input("Revision Date", value=datetime.date.today())
    purpose = st.text_input("Purpose of Issue")
    project = st.text_input("Project")
    originator = st.text_input("Originator")
    stage = st.text_input("Project Stage")
    submitted = st.form_submit_button("Save")

    if submitted:
        new_row = {
            "File Name": file_name,
            "Doc Ref": doc_ref,
            "Document Title": title,
            "Status": status,
            "Discipline": discipline,
            "File Type": file_type,
            "Rev Date": rev_date,
            "Purpose of Issue": purpose,
            "Project": project,
            "Originator": originator,
            "Project Stage": stage
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv("documents.csv", index=False)
        st.success("✅ Document added!")

# 🎨 تلوين الصف بالكامل
def highlight_row(row):
    if row["Status"] in ["C - Revise and Resubmit", "D - Rejected"]:
        return ['background-color: #ffcccc; font-weight: bold'] * len(row)
    else:
        return [''] * len(row)

# 📊 ملخص الحالات
st.markdown("## 📊 Document Status Summary")
if df.empty:
    st.info("No documents to summarize yet.")
else:
    status_counts = df["Status"].value_counts()
    for status in status_options:
        count = status_counts.get(status, 0)
        icon = "✅" if "A" in status else "🟠" if "B" in status else "🔴" if "C" in status else "🔥" if "D" in status else "📄"
        st.write(f"{icon} **{status}**: {count} document(s)")

# 🔍 بحث بالكلمة
st.markdown("## 🔍 Search Documents")
search_term = st.text_input("Enter a keyword to search:")
if search_term:
    search_results = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    if not search_results.empty:
        styled_search = search_results.style.apply(highlight_row, axis=1)
        st.dataframe(styled_search)
    else:
        st.warning("No documents matched your search.")

# 🔍 فلترة
with st.expander("🔍 Filter Documents"):
    selected_status = st.selectbox("Filter by Status", ["All"] + status_options)
    selected_discipline = st.selectbox("Filter by Discipline", ["All"] + discipline_options)

    filtered_df = df.copy()
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["Status"] == selected_status]
    if selected_discipline != "All":
        filtered_df = filtered_df[filtered_df["Discipline"] == selected_discipline]

    styled_filtered_df = filtered_df.style.apply(highlight_row, axis=1)
    st.dataframe(styled_filtered_df)

# 📋 عرض كامل
st.markdown("## 📋 All Documents")
styled_df = df.style.apply(highlight_row, axis=1)
st.dataframe(styled_df)

# 🖨️ زر طباعة
st.markdown("""
    <script>
    function printTable() {
        var divToPrint = document.querySelector("section.main");
        var newWin = window.open('', 'Print-Window');
        newWin.document.open();
        newWin.document.write('<html><head><title>Print Table</title></head><body onload="window.print()">'+divToPrint.innerHTML+'</body></html>');
        newWin.document.close();
        setTimeout(function(){newWin.close();},10);
    }
    </script>
    <button onclick="printTable()">🖨️ Print Table</button>
""", unsafe_allow_html=True)

# 📄 توليد PDF
def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="📄 Document Tracker Report", ln=1, align='C')
    pdf.ln(5)
    for index, row in dataframe.iterrows():
        for col in dataframe.columns:
            text = f"{col}: {row[col]}"
            pdf.cell(200, 6, txt=text, ln=1)
        pdf.ln(3)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer

# 📤 تصدير PDF و CSV
st.markdown("## 📤 Export")
if st.button("📄 Generate PDF"):
    pdf_buffer = generate_pdf(df)
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_buffer.getvalue(),
        file_name="documents.pdf",
        mime="application/pdf"
    )

st.download_button("⬇️ Download CSV", df.to_csv(index=False), "documents.csv")
