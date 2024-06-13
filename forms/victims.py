import streamlit as st
import requests
from pydantic import ValidationError
from modules.dataValidation import VictimData_Validation
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


# Function to generate unique keys
def generate_key(base, index):
    return f"{base}_{index}"


def VictimDetails(mps_cps, ppo_cpo, pro, index):
    
    # Initialize Barangay Values and City Mun Values
    st.subheader("Victims's Profile")
    brgy_values, city_mun_value, province_value = get_brgy_city_mun(mps_cps)

    pro = pro
    ppo_cpo = ppo_cpo

    # First, Middle, and Last Name Portion
    col1, col2, col3 = st.columns(3)

    with col1:
        vic_fname = st.text_input("First Name :red[#]", key=generate_key("vic_fname", index))
        if not vic_fname:
            st.warning('Please enter a first name.')

        vic_qlfr = st.text_input("Qualifier", key=generate_key("vic_qlfr", index))


    with col2:
        vic_midname = st.text_input("Middle Name", key=generate_key("vic_mname", index))
        vic_alias = st.text_input("Alias", key=generate_key("vic_alias", index))
        if vic_alias is None:
            vic_alias = None
        else:
            vic_alias = f"alias {vic_alias}"



    with col3:
        vic_lname = st.text_input("Last Name :red[#]", key=generate_key("vic_lname", index))
        if not vic_lname:
            st.warning('Please enter a last name.')
        vic_gndr = st.radio("Gender :red[#]", ("Male", "Female"), index=None, horizontal=True, key=generate_key("vic_gndr", index))
        if not vic_gndr:
            st.warning('Please select a gender.')
        

    st.write("---")

    colA, colB, colC = st.columns(3)

    with colA:
        st.text_input("Region", value="Region XII", disabled=True, key=generate_key("vic_region", index))

    with colB:
        vic_distprov = st.selectbox("District/Province", ([province_value]), disabled=True, key=generate_key("vic_distprov", index))

    with colC:
        vic_cityMun = st.selectbox("City/Municipality", ([city_mun_value]), disabled=True, key=generate_key("vic_citymun", index))
    
    colD, colE = st.columns(2)
    vic_brgy = colD.selectbox("Barangay", brgy_values, placeholder="Please select a Barangay", key=generate_key("vic_brgy", index), index=None)
    vic_strName = colE.text_input("House No./Street Name", key=generate_key("vic_strName", index))

    st.write("---")

    col11, col12 = st.columns(2)
    with col11:
        vic_age_grp = st.selectbox("Age Group", index=None, placeholder="Select Victims Age Group", options=("Infant (0-12 months)", "Toddler (1-3 y/o)", "Kid (4-9 y/o)", "Preteen (10-12 y/o)", "Teenager (13-18 y/o)", "Young Adult (19-39 y/o)", "Middle age Adult (40-64 y/o)", "Old Age Adult (65 y/o-up)"), key=generate_key("vic_ageGrp", index))
        vic_age = st.number_input("Estimated or Exact Age", step=1, min_value=0, key=generate_key("vic_age", index))

    with col12:
        vic_birthdate = st.date_input("Birth Date", value=None, key=generate_key("vic_birthdate", index))
        vic_relation_to_suspect = st.text_input("Victim\'s Relationship to Suspect", key=generate_key("vic_relation_to_suspect", index))

    st.write("---")

    col21, col22, col23 = st.columns(3)

    with col21:
        vic_status = st.selectbox("Victim\'s Status",["Test1","Test2"],index=None, key=generate_key("vic_status", index))
        vic_educ = st.selectbox("Victim\'s Education",["Test1","Test2"],index=None, key=generate_key("vic_educ", index))

    with col22:
        vic_occupation = st.selectbox("Victim\'s Occupation",["Test1","Test2"],index=None, key=generate_key("vic_occupation", index))
        vic_sector = st.selectbox("Victim\'s Sector/Affliation",["Test1","Test2"],index=None, key=generate_key("vic_sector", index))

    with col23:
        vic_civil_status = st.selectbox("Victim\'s Civil Status",["Test1","Test2"],index=None, key=generate_key("vic_civil_status", index))
        vic_ethnic = st.selectbox("Victim\'s Ethnic Group",["Test1","Test2"],index=None, key=generate_key("vic_ethnic", index))

    # Create a dictionary of the data
    data = {
        "pro": pro,
        "ppo_cpo": ppo_cpo,
        "mps_cps": mps_cps,
        "vic_fname": vic_fname,
        "vic_midname": vic_midname,
        "vic_lname": vic_lname,
        "vic_qlfr": vic_qlfr,
        "vic_alias": vic_alias,
        "vic_gndr": vic_gndr,
        "vic_age": vic_age,
        "vic_distprov": vic_distprov,
        "vic_cityMun": vic_cityMun,
        "vic_brgy": vic_brgy,
        "vic_strName": vic_strName
    }

    # Mapping of field names to user-friendly names
    field_name_mapping = {
        "pro": "PRO",
        "ppo_cpo": "PPO",
        "mps_cps": "Station",
        "vic_fname": "Victim's First Name",
        "vic_midname": "Victim's Middle Name",
        "vic_lname": "Victim's Last Name",
        "vic_qlfr": "Qualifier",
        "vic_alias": "Alias",
        "vic_gndr": "Gender",
        "vic_age": "Age",
        "vic_distprov": "District/Province",
        "vic_cityMun": "City/Municipality",
        "vic_brgy": "Barangay",
        "vic_strName": "House No./Street Name"
    }

    # Validate the data using Pydantic
    victim_data = ""
    try:
        victim_data = VictimData_Validation(**data)
        # Data is valid, proceed with database operations
        return victim_data
    except ValidationError as e:
        for error in e.errors():
            field = error['loc'][0]
            message = error['msg']
            user_friendly_field = field_name_mapping.get(field, field)
            st.error(f"Error in {user_friendly_field}: {message}")
    finally:
        if victim_data:
            return dict(victim_data)
    

def addVictim(mps_cps, ppo_cpo, pro):

    # Initialize session state for the number of victims
    if 'victim_count' not in st.session_state:
        st.session_state.victim_count = 1

    victim_data_list = []

    # Add a victim for each count in the session state
    for i in range(st.session_state.victim_count):
        victim_data = VictimDetails(mps_cps, ppo_cpo, pro, i)
        if victim_data:
            victim_data_list.append(victim_data)

    # Buttons to add or remove victims
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Add Another Complainant", use_container_width=True, type="primary"):
            st.session_state.victim_count += 1
            st.experimental_rerun()  # Rerun the app to show the new victim form

    with col2:
        if st.button("Remove Last Complainant", use_container_width=True, type="primary"):
            if st.session_state.victim_count > 1:
                st.session_state.victim_count -= 1
                st.experimental_rerun()  # Rerun the app to remove the last victim form


# def addVictim(mps_cps,ppo_cpo,pro):
#     # Initialize Barangay Values and City Mun Values
#     brgy_values, city_mun_value, province_value = get_brgy_city_mun(mps_cps)

#     pro = pro
#     ppo_cpo = ppo_cpo

#     # First, Middle, and Last Name Portion
#     fname, mname = st.columns(2)
#     vic_fname = fname.text_input("First Name :red[#]",key="vic_fname")
#     vic_midname = mname.text_input("Middle Name",key="vic_mname")
#     vic_lname = st.text_input("Last Name :red[#]",key="vic_lname")

#     if not vic_fname:
#         fname.warning('Please enter a first name.')
#     if not vic_lname:
#         st.warning('Please enter a last name.')

#     # Qualifier, Alias and Gender
#     qlfr, alias, gndr= st.columns(3)
#     vic_qlfr = qlfr.text_input("Qualifier",key="vic_qlfr")
#     vic_alias = alias.text_input("Alias",key="vic_alias")
#     if vic_alias is None:
#         vic_alias = None
#     else:
#         vic_alias = f"alias {vic_alias}"

#     with gndr:
#         vic_gndr = st.radio("Gender :red[#]",("Male", "Female"),index=None,horizontal=True,key="vic_gndr")

#     if not vic_gndr:
#         gndr.warning('Please select a gender.')


#     # Age Group
#     ageGrp, age = st.columns(2)
#     ageGrp.selectbox("Age Group",index=None,placeholder="Select Victims Age Group",options=("Infant (0-12 months)","Toddler (1-3 y/o)","Kid (4-9 y/o)","Preteen (10-12 y/o)","Teenager (13-18 y/o)","Young Adult (19-39 y/o)","Middle age Adult (40-64 y/o)","Old Age Adult (65 y/o-up)"),key="vic_ageGrp")
#     vic_age = age.number_input("Estimated or Exact Age",step=1,min_value=0,key="vic_age")

#     # Address - Region and Disttict/Province
#     st.subheader("Victim's Address")
#     region, distprov = st.columns(2)
#     region.text_input("Region",value="Region XII",disabled=True,key="vic_region")
#     vic_distprov = distprov.selectbox("District/Province",([province_value]),disabled=True,key="vic_distprov")

#     # Address - RCity/Municipality, Barangay and House No/Street Name
#     citymun, brgy = st.columns(2)
#     vic_cityMun = citymun.selectbox("City/Municipality",([city_mun_value]),disabled=True,key="vic_citymun")
#     vic_brgy = brgy.selectbox("Barangay :red[#]",brgy_values,placeholder="Please select a Barangay",key="vic_abrgy",index=None)


#     # Check if a Barangay was selected
#     vic_strName = ""
#     if vic_brgy == None:
#         st.warning("Please select a Barangay.")
#     else:
#         vic_strName = st.text_input("House No./Street Name",key="vic_strName")

#     st.write("---")

