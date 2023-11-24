import streamlit
# this is wam calculator
# Your WAM is weighted according to the credit point value and academic level (such as junior or senior) of the units you’ve completed, and may include credited units which have marks and grades displayed. The weight of a unit of study is assigned by the owning faculty or school. Only grades that are allocated a mark contribute to your WAM.
# wam is calculated by the formula sum of (unit credit point * unit mark)/sum of unit credit point
# hwam is calculated by the formula sum of (unit credit point * the weighting * unit mark)/sum of unit credit point,For undergraduate students in Engineering and IT courses, the weightings are 0 for 1000 level units, 2 for 2000 level units, 3 for 3000 level units and 4 for 4000 level or above units. For postgraduate students in Engineering and IT courses, the weighting is 1 for all units of study.
# add a title: USYD WAM&HWAM Calculator for engineering and IT students
streamlit.title("USYD WAM & HWAM Calculator")
# first input value: number of unit studied til now
Num_of_unit = streamlit.number_input("Number of unit studied til now", min_value=0, max_value=100, value=0, step=1)
# ask if the user want to calculate the hwam, true or false
hwam = streamlit.checkbox("Calculate HWAM", value=False)
# based on the number of unit studied, generate the number of input boxes, each input box is for the credit point of each unit and the mark of each unit
mark = []
credit_point = []
weight = []
for x in range(Num_of_unit):
    # string shown above the input box: unit x
    streamlit.write("Unit", x)
    cols = streamlit.columns(3)
    # input box for credit point of unit x, it can only be 2, 3, 6. default value is 6
    credit_of_unit = cols[0].number_input("Credit point of unit", min_value=2, max_value=6, value=6, step=1, key=f"credit_{x}")
    mark_of_unit = cols[1].number_input("Mark of unit", min_value=0, max_value=100, value=0, step=1, key=f"mark_{x}")
    # if the user want to calculate hwam, then make a input of level of units, 1000=0, 2000=2, 3000=3
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
# calculate the wam
if sum(credit_point) != 0:
    wam = 0
    for x in range(Num_of_unit):
        wam += credit_point[x] * mark[x]
    wam /= sum(credit_point)
    # show the wam
    streamlit.write("WAM:", wam)
    if hwam:
        hwam_mark = 0
        total_weighted_credits = 0
        for x in range(Num_of_unit):
            hwam_mark += credit_point[x] * mark[x] * weight[x]
            total_weighted_credits += credit_point[x] * weight[x]
        if total_weighted_credits != 0:
            hwam_mark /= total_weighted_credits
        streamlit.write("HWAM:", hwam_mark)
    # save the data
    streamlit.write("Save the data for future use?")
    if streamlit.button("Save"):
        # save the data as a csv file in column format
        streamlit.write("Data saved")
streamlit.write("This calculator is for engineering and IT students only. It is based on the information from link below")
streamlit.markdown(
    """
    <a target="_blank" href="https://rp-handbooks.sydney.edu.au/handbooks/archive/2012/engineering/rules/faculty_resolutions.shtml">
        <button>Go to handbook page</button>
    </a>
    """,
    unsafe_allow_html=True,
)