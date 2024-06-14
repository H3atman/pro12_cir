import streamlit as st
import requests
from modules.dataValidation import Offense_Validation
from pydantic import ValidationError
from config.database import api_endpoint


# Cache data for 30 minutes
@st.cache_data(ttl=1800)
def get_offense_classifications():
    # Make a GET request to the FastAPI endpoint
    response = requests.get(f"{api_endpoint}/offense_classifications")
    response.raise_for_status()  # Ensure we handle HTTP errors

    # Parse the JSON response
    data = response.json()

    return data

data = get_offense_classifications()

# Function to generate unique keys
def generate_key(base, index):
    return f"{base}_{index}"

def investigator_info():
    st.subheader("Investigator-on-Case")
    col1, col2 = st.columns(2)

    with col1:
        #Other Details
        ioc = st.text_input("Investigator on Case",placeholder="Name")
        ioc_cp_number = st.text_input("Contact Number of Investigator",placeholder="Contact Number")


    with col2:
        senior_ioc = st.text_input("Head Investigator on Case",placeholder="Name")
        senior_ioc_cp_number = st.text_input("Contact Number of Head Investigator",placeholder="Contact Number")


def offenseDetails(index):
    # Initialize Offense Values
    offense_classifications = get_offense_classifications()
    offense_values = []
    classifications = []
    for item in offense_classifications:
        if 'incidents' in item:
            offense_values.append(item['incidents'])
        if 'classification' in item:
            classifications.append(item['classification'])
    with st.container(border=True):
        st.subheader("Offense :red[#]")

        felony = ["ATTEMPTED", "CONSUMMATED", "FRUSTRATED"]
        stg_felony = st.selectbox("Stages of Felony",felony,index=None, key=generate_key("stg_felony", index))
        
        offenseType = st.selectbox("Select Offense :red[#]", offense_values, index=None, key=generate_key("offenseType", index))
        warning = st.empty()
        if offenseType is None:
            warning.warning("Please select an Offense")

        modus_list = ["Physical Injuries", "``BESTFREN`` Gang", "Agaw-armas", "Akyat Bahay", "Ambush", "Applied as driver", "Applied as helper", "Asphyxiation", "Bag Snatching", "Bag/Purse Slashing", "Bag/Purse Snatching", "Baklas bubong/dingding", "Basag Kotse/Salamin", "Beheading", "Biting", "Bolt cutter", "Bombing", "Budol Budol", "Budol-budol", "Bukas Kotse", "Bundol", "Burning", "Cable/electric meter", "Cattle Rustling", "Cellphone Snatching", "Chemicals", "Child Prostitution", "Child Trafficking", "Choking", "Chopping", "Clubbing", "Committed by an employee (commercial/store/shop)", "Conspiracy to bribe voters", "Crowbar/destroying lock", "Deadly Weapon (non-firearm)", "Deprived of Reason or Unconcious (Under the influence of Drugs)", "Deprived of Reason or Unconcious (Under the influence of Liquior)", "Destroying window", "Donut (Gulong)", "Drowning", "Economic Abuse", "Electrocution", "Estribo", "Explosion", "Extortion", "Failed to Return (FTR)", "Fetishism/Object Rape", "Force, Threat and Intimidation", "Forcibly Taken (FT)", "Fraudulent Machinations", "Gang Rape", "Gang War", "Gang/Party", "Grave Abuse of Authority", "Gun Ban violation", "Hacking", "Hanging", "Hitting with hard object", "Hold-up w/ gun", "Hold-up w/ sharp object", "Indiscriminate Firing/Stray Bullet", "Intentional Mutilation", "Ipit Kotse", "Jewelry snatching", "Jewelry Snathcing", "Liquor Ban violation", "Martilyo", "Mauling", "Motor Vehicle Parts & Accessories", "Motorcycle Riding Suspects (Riding in Tandem)", "Obscene Publication", "Other Acts of Abuse", "Paihi/syphon", "Parts and accessories of motor vehicle", "Petnapping", "Physical Violence", "Pick-Pocketing", "Poisoning", "Possession", "Psychological Violence", "Punching", "Pushing", "Salisi", "Salisi (akyat bahay)", "Salisi (Cellphone/Laptop)", "Salisi (establishment)", "Salisi (park)", "Salisi (terminal)", "Seized At Gunpoint with Intimidation (SAGPI)", "Sexual Violence", "Shooting", "Shoplifting", "Snatching", "Sniping", "Stabbing", "Stabbing & hacking", "Statutory rape", "Stolen While Parked Unattended (SWPU)", "Stoning/thrown object", "Strafing", "Strangulation", "Sungkit", "Taken on occasion of civil disturbance/war", "Taken without owner's consent (TWOC)", "Test Drive", "Tunneling", "Tutok Kalawit", "Undue influence", "Using", "Vehicle Parts & Accessories", "Vote Buying/Selling", "Wagering/Betting upon result of election", "Water meter"]
        modus = st.selectbox("Modus", modus_list, index=None, key=generate_key("modus", index))


    # # Create a directory of data
    # data = {
    #     "offense": offense,
    #     "offense_class": offense_class,
    #     "case_status": case_status,
    #     "check": check
    # }


    # # Mapping of field names to user-friendly names
    # field_name_mapping = {
    #     "offense": "Type of Offense based on the Dropdown",
    #     "offense_class": "Offense Classification",
    #     "otherOffense": "If Offense is not in the Dropdown, Type Offense Here",
    #     "case_status": "Status of the Offense",
    #     "check": "Check if the check function is enabled"
    # }

    # offense_detail = ""

    # # Validate the data using Pydantic
    # try:
    #     offense_detail = Offense_Validation(**data)
    #     # Data is valid, proceed with database operations
    #     return offense_detail
    # except ValidationError as e:
    #     for error in e.errors():
    #         field = error['loc'][0]
    #         message = error['msg']
    #         user_friendly_field = field_name_mapping.get(field, field)
    #         st.error(f"Error in {user_friendly_field}: {message}")
    # # finally:
    # #     st.write(offense_detail)

    # return offense_detail

def addOffense():

    # Initialize session state for the number of victims
    if 'offense_count' not in st.session_state:
        st.session_state.offense_count = 1

    offense_data_list = []

    # Add a victim for each count in the session state
    for i in range(st.session_state.offense_count):
        victim_data = offenseDetails(i)
        if victim_data:
            offense_data_list.append(victim_data)

    # Buttons to add or remove victims
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Add Another Offense", use_container_width=True, type="primary",key="offense_btn1"):
            st.session_state.offense_count += 1
            st.rerun()  # Rerun the app to show the new victim form

    with col2:
        if st.button("Remove Last Offense", use_container_width=True, type="primary",key="offense_btn2"):
            if st.session_state.offense_count > 1:
                st.session_state.offense_count -= 1
                st.rerun()  # Rerun the app to remove the last victim form