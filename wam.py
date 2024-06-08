import PyPDF2
import pandas as pd
import streamlit as st

def extract_text_from_pdf_pypdf2(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    try:
        for number in range(10):
            page = pdf_reader.pages[number]
            text += page.extract_text()
    except IndexError:
        pass
    return text


st.title("WAM&HWAM Calculator")
st.write("This is a simple web application that can calculate your WAM and HWAM based on your transcript.")
st.write("Please upload your transcript in PDF format.")
st.write("Sydneystudent -> My studies -> Assessment -> View academic transcript -> Printable version")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:

    text = extract_text_from_pdf_pypdf2(uploaded_file)
    # Delete the anything before the third occurrence of the word Credit points
    text = text[text.find("Credit points") + len("Credit points"):]
    text = text[text.find("Credit points") + len("Credit points"):]
    # Delete the anything after the last occurrence of the word Credit points gained 
    text = text[:text.rfind("Credit points gained")]

    def is_mark(text):
        if '.' not in text:
            return False
        try:
            num = float(text)
            return 0 <= num <= 100
        except ValueError:
            return False

    year = []
    session = []
    unit_of_study_code = []
    mark = []
    grade = []
    credit_points = []
    level = []


    session_code = [
        "S1C", "S1CG", "S1CIAP", "S1CIFE", "S1CIJA", "S1CIJN", "S1CIMR", "S1CIMY", "S1CMBA", "S1CNDP", 
        "S1CRA", "S1CRB", "S1CRR1", "S1CRR2", "S1CVP1", "S1CVP2", "S1CVP3", "S1CVP4", "S1CVP5", "S1CVP6", 
        "S2C", "S2CE", "S2CG", "S2CIAU", "S2CIDE", "S2CIJL", "S2CINO", "S2CIOC", "S2CISE", "S2CMBA", 
        "S2CNDP", "S2CRA", "S2CRB", "S2CREA", "S2CREB", "S2CRR3", "S2CRR4", "S2CVP1", "S2CVP2", "S2CVP3", 
        "S2CVP4", "S2CVP5", "S2CVP6"
    ]

    grade_code_with_mark = ["HD", "DI", "CR", "PS", "FA"]
    grade_code_without_mark = ["AF", "CN", "DC", "DF", "FR", "SR", "WD", "IC", "RI", "UC"]

    for word in text.split():
        if word.isdigit() and len(word) == 4:
            year.append(word)
        elif word in session_code:
            session.append(word)
        elif word.isupper() and len(word) == 8:
            unit_of_study_code.append(word)
        elif is_mark(word):
            mark.append(word)
        elif word in grade_code_with_mark or word in grade_code_without_mark:
            grade.append(word)
        elif word.isdigit() and len(word) <= 2 and (last_word in grade_code_with_mark or last_word in grade_code_without_mark):
            credit_points.append(word)
        last_word = word

    for i in range(len(grade)):
        if grade[i] in grade_code_without_mark:
            mark.insert(i, "-")

    for code in unit_of_study_code:
        if code[4] == "1":
            level.append(0)
        elif code[4] <= "4":
            level.append(code[4])
        else:
            level.append(4)

    # Create a DataFrame
    df = pd.DataFrame({
        "Year": year,
        "Session": session,
        "Unit of Study Code": unit_of_study_code,
        "Mark": mark,
        "Grade": grade,
        "Credit Points": credit_points,
        "Level": level
    })

    # calculate the wam : Mark*Credit Points/Credit Points
    pd.options.mode.chained_assignment = None  # 默认为 'warn'
    wam = df[df["Mark"] != "-"]
    wam["Mark"] = wam["Mark"].astype(float)
    wam["Credit Points"] = wam["Credit Points"].astype(float)
    wam["Mark*Credit Points"] = wam["Mark"] * wam["Credit Points"]
    wam["Credit Points"] = wam["Credit Points"].astype(float)
    wam["Credit Points"] = wam["Credit Points"].sum()
    wam["Mark*Credit Points"] = wam["Mark*Credit Points"].sum()
    wam["WAM"] = wam["Mark*Credit Points"] / wam["Credit Points"]
    wam["WAM"] = wam["WAM"].round(2)
    wam = wam.drop(columns=["Mark", "Grade", "Credit Points", "Mark*Credit Points"])
    wam = wam.drop_duplicates()
    # show the wam to one word
    wam = wam["WAM"].values[0]
    st.write("wam:", wam)

    try:
        # calculate the hwam : Mark*Credit Points*level/Credit Points*level
        hwam = df[df["Mark"] != "-"]
        hwam = hwam[hwam["Level"] != 0]
        hwam["Mark"] = hwam["Mark"].astype(float)
        hwam["Credit Points"] = hwam["Credit Points"].astype(float)
        hwam["Level"] = hwam["Level"].astype(float)
        hwam["Mark*Credit Points*level"] = hwam["Mark"] * hwam["Credit Points"] * hwam["Level"]
        hwam["Credit Points*level"] = hwam["Credit Points"] * hwam["Level"]
        hwam["Mark*Credit Points*level"] = hwam["Mark*Credit Points*level"].sum()
        hwam["Credit Points*level"] = hwam["Credit Points*level"].sum()
        hwam["HWAM"] = hwam["Mark*Credit Points*level"] / hwam["Credit Points*level"]
        hwam["HWAM"] = hwam["HWAM"].round(2)
        hwam = hwam.drop(columns=["Mark", "Grade", "Credit Points", "Mark*Credit Points*level", "Credit Points*level", "Level"])
        hwam = hwam.drop_duplicates()
        # show the hwam to one word
        hwam = hwam["HWAM"].values[0]
        st.write("hwam:", hwam)
    except:
        st.write("hwam: First year got no hwam!")



