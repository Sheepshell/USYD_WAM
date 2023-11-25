import streamlit as st
from datetime import datetime
import pandas as pd

mark = []
credit_point = []
weight = []
st.title("USYD WAM & HWAM Calculator")
saved_csv = st.checkbox("Do you wanna upload a saved csv file to calculate your new WAM?", value=False)
if saved_csv:
    Num_of_unit = st.number_input("Enter the number of new UOS result", min_value=0, max_value=100, value=0, step=1)
    csv = st.file_uploader("Upload a saved csv file", type=["csv"])
    if csv != None:
        df = pd.read_csv(csv)
        mark = df["Mark"].tolist()
        # st.write(mark)
        credit_point = df["Credit point"].tolist()
        # st.write(credit_point)
        if "Weight" in df.columns:
            weight = df["Weight"].tolist()
            # st.write(weight)
else:
    Num_of_unit = st.number_input("Enter the number of UOS you have completed", min_value=0, max_value=100, value=0, step=1)
hwam = st.checkbox("Calculate HWAM", value=False)
for x in range(Num_of_unit):
    st.write("Unit", x)
    cols = st.columns(3)
    credit_of_unit = cols[0].number_input("Credit point of unit", min_value=2, max_value=6, value=6, step=1, key=f"credit_{x}")
    mark_of_unit = cols[1].number_input("Mark of unit", min_value=0, max_value=100, value=0, step=1, key=f"mark_{x}")
    if hwam:
        weight_of_unit = cols[2].selectbox("Level of unit", options=[1000, 2000, 3000, 4000, 5000, "thesis"], index=0, key=f"weight_{x}")
        if weight_of_unit == 1000:
            weight_of_unit = 0
        elif weight_of_unit == 2000:
            weight_of_unit = 2
        elif weight_of_unit == 3000:
            weight_of_unit = 3
        elif weight_of_unit == 4000:
            weight_of_unit = 4
        elif weight_of_unit == 5000:
            weight_of_unit = 5
        elif weight_of_unit == "thesis":
            weight_of_unit = 8
        weight.append(weight_of_unit)
    credit_point.append(credit_of_unit)
    mark.append(mark_of_unit)
if sum(credit_point) != 0:
    wam = 0
    for x in range(len(credit_point)):
        wam += credit_point[x] * mark[x]
    wam /= sum(credit_point)
    st.write("WAM:", wam)
    # save the data
    df = pd.DataFrame({"Credit point": credit_point, "Mark": mark, "wam": wam})
    if hwam:
        hwam_mark = 0
        total_weighted_credits = 0
        for x in range(len(credit_point)):
            hwam_mark += credit_point[x] * mark[x] * weight[x]
            total_weighted_credits += credit_point[x] * weight[x]
        if total_weighted_credits != 0:
            hwam_mark /= total_weighted_credits
        st.write("HWAM:", hwam_mark)
        df["Weight"] = weight
        df["hwam"] = hwam_mark
    csv = df.to_csv(index=False)
    current_date_file_name = datetime.now().strftime(r"%Y-%m-%d")+r"_my_wam.csv"
    st.write("Save the data for future use?")
    st.download_button(label='click to download', data = csv, file_name = current_date_file_name, mime='text/csv')
    st.write("HWAM is for engineering and IT students only. It is based on the information from link below")
    st.markdown(
    """
    <a target="_blank" href="https://rp-handbooks.sydney.edu.au/handbooks/archive/2012/engineering/rules/faculty_resolutions.shtml">
        <button>Go to handbook page</button>
    </a>
    """,
    unsafe_allow_html=True,
    )
