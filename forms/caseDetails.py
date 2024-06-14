import streamlit as st
import requests
from modules.ui_models import input_time_committed, input_time_reported
import datetime
from modules.dataValidation import Case_Detail_Validation
from pydantic import ValidationError
from config.database import api_endpoint

@st.cache_data(ttl=1800)  # Cache data for 30 minutes
def get_brgy_city_mun(mps_cps):
    # Make a GET request to the FastAPI endpoint
    response = requests.get(f"{api_endpoint}/brgy-city-mun/{mps_cps}")

    # Parse the JSON response
    data = response.json()

    # Extract the brgy_values and city_mun_value
    brgy_values = [item['brgy'] for item in data['brgy_values']]
    city_mun_value = data['city_mun_value']['city_mun']
    province_value = data['province_value']['province']


    return brgy_values, city_mun_value, province_value


def case_Details(mps_cps,ppo_cpo,pro):

    brgy_values, city_mun_value, province_value = get_brgy_city_mun(mps_cps)

    det_narrative = st.text_area("Narrative")

    pro = pro
    ppo_cpo = ppo_cpo
    mps_cps = mps_cps

    st.write("---")

    DTreported, DTcommitted = st.columns(2)

    # Initialize session state for times if not already done
    if "input_time_reported" not in st.session_state:
        st.session_state.input_time_reported = None
    if "input_time_committed" not in st.session_state:
        st.session_state.input_time_committed = None

    # Handling Date and Time Reported
    with DTreported:
        st.subheader("Date & Time Reported")
        dt_reported = st.date_input(
            "Date Reported :red[#]",
            help="If di po available sa data ang exact date reported paki pili nalang po ang 1st day of the month",
            format="YYYY/MM/DD"
        )
        
        col1, col2 = st.columns(2)
        time_reported_str = ""
        if st.session_state.input_time_reported:
            time_reported_str = st.session_state.input_time_reported.strftime("%I:%M %p")
        col1.text_input("Time Reported", value=time_reported_str, disabled=True)
        col2.write("\n")
        col2.write("\n")
        if col2.button("Enter Time", use_container_width=True, key="timereported"):
            input_time_reported()

    # Handling Date and Time Committed
    with DTcommitted:
        st.subheader("Date & Time Committed")
        dt_committed = st.date_input(
            "Date Committed",
            help="If di po available sa data ang exact date reported paki pili nalang po ang 1st day of the month",
            format="YYYY/MM/DD",value=None
        )
        
        col1, col2 = st.columns(2)
        time_committed_str = ""
        if st.session_state.input_time_committed:
            time_committed_str = st.session_state.input_time_committed.strftime("%I:%M %p")
        col1.text_input("Time Committed", value=time_committed_str, disabled=True)
        col2.write("\n")
        col2.write("\n")
        if col2.button("Enter Time", use_container_width=True, key="timecommitted"):
            input_time_committed()

    st.write("---")

    st.write("<h4>Place of Commission</h4>", unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)

    with colA:
        st.text_input("Region", value="Region XII", disabled=True)

    with colB:
        vic_distprov = st.selectbox("District/Province", ([province_value]))

    with colC:
        vic_cityMun = st.selectbox("City/Municipality", ([city_mun_value]))
    
    colD, colE = st.columns(2)
    vic_brgy = colD.selectbox("Barangay", brgy_values, placeholder="Please select a Barangay", index=None)
    vic_strName = colE.text_input("House No./Street Name")


    st.write("---")

    st.write("<h3>Case Status</h3>", unsafe_allow_html=True)

    col1a, col2a, col3a = st.columns(3)
    
    with col1a:
        case_status = st.selectbox("Case Status",["Cleared","Solved","Under Investigation"],index=None)

    with col2a:
        solve_type = ["SOLVED (AMICABLY SETTLED)", "SOLVED (FILED-ARRESTED)", "SOLVED (SUSPECT DIED)", "SOLVED (SUSPECT IDENTIFIED-VICTIM REFUSED TO FILE CHARGES)"]
        case_solve_type = st.selectbox("Case Solve Type",solve_type,index=None)

    with col3a:
        filing_type = ["E-INQUEST", "INQUEST", "REGULAR"]
        type_of_filing = st.selectbox("Type of Filing",filing_type,index=None)

    col1b, col2b = st.columns(2)

    with col1b:
        st.write("<h4>Status in Prosecution</h4>", unsafe_allow_html=True)
        status_pros = ["FOR FURTHER INVESTIGATION", "RESOLVED - DISMISSED", "RESOLVED - DISMISSED UNDER PETITION FOR REVIEW", "RESOLVED - FILED IN COURT", "UNDER PRELIMINARY INVESTIGATION"]
        status_prosecution = st.selectbox("Case Status in Prosecution",status_pros,index=None)

        grounds_for_dismissal = ["Death of Accused", "Failure to Attend Hearing", "Failure to Prosecute/Present Evidence", "Inadmissibility of Evidence due to illegal Search and Seizure", "Inconsistent Testimonies", "Insufficiency of Evidence", "Lack of Interest of Complainant", "Lack of Probable Cause", "Procedural Irregularities", "Referred for Further Investigation", "Respondent are Minors", "Violation of Chain of Custody", "Violation of Constitutional Rights"]
        if_dismissed_in_pros = st.selectbox("If Dismissed - Grounds for Dismissal",grounds_for_dismissal,index=None)

        date_filed_in_prosecutor = st.date_input("Date Filed in Prosecutor's Office")
        docket_number = st.text_input("IS/Docket Number")
        prosecutor = st.text_input("Prosecutor")

    with col2b:

        st.write("<h4>Status in Court</h4>", unsafe_allow_html=True)
        status_court = ["ARCHIVED", "ARRAIGNMENT", "DECIDED - ACQUITTED", "DECIDED - CONVICTION", "DECIDED - CONVICTION - ON MR", "DECIDED - CONVICTION - PLEA BARGAINING", "DECIDED - CONVICTION - WITH FINALITY (SUPREME COURT)", "DECIDED - CONVICTION (SERVED SENTENCE)", "DECIDED - DISMISSAL", "ON-GOING TRIAL", "PRE-TRIAL", "PROVISIONALLY DISMISSED", "REVERTED FOR MEDIATION", "REVERTED TO PROSECUTOR FOR FURTHER INVESTIGATION"]
        status_in_court = st.selectbox("Case Status in Court",status_court,index=None)

        grounds_for_dismissal_court = ["Death of Accused", "Failure to Attend Hearing", "Failure to Prosecute/Present Evidence", "Inadmissibility of Evidence due to illegal Search and Seizure", "Inconsistent Testimonies", "Insufficiency of Evidence", "Lack of Interest of Complainant", "Lack of Probable Cause", "Procedural Irregularities", "Referred for Further Investigation", "Respondent are Minors", "Violation of Chain of Custody", "Violation of Constitutional Rights"]
        if_dismissed_in_court = st.selectbox("If Dismissed is Court - Grounds for Dismissal",grounds_for_dismissal_court,index=None)

        date_filed_in_court = st.date_input("Date Filed in Court")
        cc_number = st.text_input("Criminal Case Number")
        judge = st.text_input("Judge")
        court_branch = st.text_input("Court Branch")


    # Create a directory of data
    data = {
        "pro": pro,
        "ppo_cpo": ppo_cpo,
        "mps_cps": mps_cps,
        "det_narrative": det_narrative,
        "dt_reported": dt_reported,
        "time_reported": st.session_state.input_time_reported,
        "dt_committed": dt_committed,
        "time_committed": st.session_state.input_time_committed
    }

    # Mapping of field names to user-friendly names
    field_name_mapping = {
        "det_narrative": "Case Narrative",
        "dt_reported": "Date Reported",
        "time_reported": "Time Reported",
        "dt_committed": "Date Committed",
        "time_committed": "Time Committed"
    }

    case_detail = ""

    # Validate the data using Pydantic
    try:
        case_detail = Case_Detail_Validation(**data)
        # Data is valid, proceed with database operations
        return case_detail
    except ValidationError as e:
        st.error(e)
    # finally:
    #     st.write(case_detail)

    return case_detail