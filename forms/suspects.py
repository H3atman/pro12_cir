import streamlit as st
import requests
from pydantic import ValidationError
from modules.dataValidation import SuspectData_Validation
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


def SuspectDetails(mps_cps, ppo_cpo, pro, index):
    
    with st.container(border=True):
        # Initialize Barangay Values and City Mun Values
        st.subheader("Suspect's Info")
        brgy_values, city_mun_value, province_value = get_brgy_city_mun(mps_cps)

        pro = pro
        ppo_cpo = ppo_cpo

        # First, Middle, and Last Name Portion
        col1, col2, col3 = st.columns(3)

        with col1:
            sus_fname = st.text_input("First Name :red[#]", key=generate_key("sus_fname", index))

        with col2:
            sus_midname = st.text_input("Middle Name", key=generate_key("sus_mname", index))

        with col3:
            sus_lname = st.text_input("Last Name :red[#]", key=generate_key("sus_lname", index))

        col4, col5, col6 = st.columns(3)

        with col4:
            sus_qlfr = st.text_input("Qualifier", key=generate_key("sus_qlfr", index))

        with col5:
            sus_alias = st.text_input("Alias", key=generate_key("sus_alias", index))
            if sus_alias is None:
                sus_alias = None
            else:
                sus_alias = f"alias {sus_alias}"

        with col6:
            sus_gndr = st.radio("Gender :red[#]", ("Male", "Female"), index=None, horizontal=True, key=generate_key("sus_gndr", index))

        st.write("---")

        colA, colB, colC = st.columns(3)

        with colA:
            st.text_input("Region", value="Region XII", disabled=True, key=generate_key("sus_region", index))

        with colB:
            sus_distprov = st.selectbox("District/Province", ([province_value]), disabled=True, key=generate_key("sus_distprov", index))

        with colC:
            sus_cityMun = st.selectbox("City/Municipality", ([city_mun_value]), disabled=True, key=generate_key("sus_citymun", index))
        
        colD, colE = st.columns(2)
        sus_brgy = colD.selectbox("Barangay", brgy_values, placeholder="Please select a Barangay", key=generate_key("sus_brgy", index), index=None)
        sus_strName = colE.text_input("House No./Street Name", key=generate_key("sus_strName", index))

        st.write("---")

        col11, col12 = st.columns(2)
        with col11:
            sus_age_grp = st.selectbox("Age Group", index=None, placeholder="Select Victims Age Group", options=("Infant (0-12 months)", "Toddler (1-3 y/o)", "Kid (4-9 y/o)", "Preteen (10-12 y/o)", "Teenager (13-18 y/o)", "Young Adult (19-39 y/o)", "Middle age Adult (40-64 y/o)", "Old Age Adult (65 y/o-up)"), key=generate_key("sus_ageGrp", index))
            sus_age = st.number_input("Estimated or Exact Age", step=1, min_value=0, key=generate_key("sus_age", index))

        with col12:
            sus_birthdate = st.date_input("Birth Date", value=None, key=generate_key("sus_birthdate", index))
            sus_relation_to_suspect = st.text_input("Suspect\'s Relationship to Victim", key=generate_key("sus_relation_to_suspect", index))

        st.text_input("Suspect's Motive")

        st.write("---")



        col21, col22, col23 = st.columns(3)

        with col21:
            status_list = ["Deceased", "Escaped", "Found", "Found Dead Body", "Held Captive", "Hospitalized", "Injured", "Killed", "Missing", "Released", "Rescued", "Suicide", "Under Custody", "Unharmed", "Wounded"]
            sus_status = st.selectbox("Suspect\'s Status",status_list,index=None, key=generate_key("sus_status", index))

            education_list = ["ADULT EDUCATION", "AGRICULTURAL ADMINISTRATION", "AGRICULTURAL BOTANY", "AGRICULTURAL ECONOMICS", "AGRICULTURAL EDUCATION", "AGRICULTURAL ENGINEERING", "ARCHITECTURAL ENGINEERING", "ARCHITECTURE", "ASSOCIATE IN ARTS", "AUTO-MECHANIC", "BACHELOR OF ARTS", "BS IN CIVIL ENGINEERING", "BS IN ELECT. COMM. ENGINEERING", "BUSINESS ADMINISTRATION", "CIVIL ENGINEERING", "COLLEGE", "COLLEGE GRADUATE", "CRIMINOLOGY", "CULINARY ARTS", "CUSTOM ADMINISTRATION", "ECONOMICS", "ELECTRICAL ENGINEERING", "ELECTRICIAN", "ELEMENTARY EDUCATION/BSEED", "ELEMENTARY GRADUATE", "ELEMENTARY LEVEL (UNDERGRADUATE)", "ENGINEERING", "FARM MECHANICS", "FIRST YEAR", "FOURTH YEAR", "GENERAL MEDICINE", "GENERAL TEACHING", "GEODETIC ENGINEERING", "GRADE I", "GRADE II", "GRADE III", "GRADE IV", "GRADE V", "GRADE VI", "GRADE VII", "GRADUATE STUDIES", "GRADUATED", "HIGH SCHOOL", "HIGH SCHOOL GRADUATE", "K TO 12", "K TO 12 GRADUATE", "LAW", "MANAGEMENT", "MARINE ENGINEERING", "MARKETING", "MECHANICAL ENGINEERING", "MERCHANT MARINE ACADEMY", "NOT GRADUATED", "NURSING", "OTHERS", "PHILOSOPHY", "PHYSICAL EDUCATION", "POST GRADUATE", "PSYCHOLOGY", "SAFETY ENGINEERING", "SECOND YEAR", "SECONDARY EDUCATION/BSE", "TECHNICAL", "THEOLOGY", "THIRD YEAR", "VOCATIONAL"]
            sus_educ = st.selectbox("Education",education_list,index=None, key=generate_key("sus_educ", index))

        with col22:
            occupation_list = ["ACCOUNTANT", "ACCOUNTING CLERK", "ACTOR", "ADJUSTERS", "ADMINISTRATIVE OFFICER", "AGENT OF SECURITIES", "AGENTS", "AGRICULTURAL TECHNICIAN", "AGRONOMIST", "AIRCRAFT WORKER", "APPRAISERS", "ARCHITECT", "ARTIST", "ASST MANAGER", "ATHLETE COACHES", "AUDITOR", "BABY SITTER", "BAKER", "BANK EMPLOYEE", "BANK TELLER", "BARBER", "BARGE CREW", "BARTENDER", "BEAUTICIAN", "BGY TANOD", "BILL COLLECTOR", "BLACKSMITH", "BOATMAN SEAMAN", "BOOKIES AND BET TAKERS", "BOOKKEEPER", "BOOKKEEPING MACHINE OPERATOR", "BOUNCER", "BOXER", "BRGY CAPTAIN", "BRGY OFFICIAL", "BRICKLAYERS", "BUS DRIVER", "BUSINESSMAN MERCHANT", "BUTCHER", "CAFGU", "CALL CENTER AGENT", "CAMERA OPERATOR", "CANNERS", "CANVASSER", "CAR WASHER", "CAREGIVER", "CARETAKER", "CARPENTER", "CASHIER", "CATERER", "CATHOLIC PRIEST", "CHARCOAL BURNER", "CHEMICAL ENGINEER", "CHEMICAL WORKER", "CHEMIST", "CHIEF EXECUTIVE", "CIVIL ENGINEER", "CIVILIAN VOLUNTEER", "CLERGYMAN", "CLERK", "CLINIC ATTENDANT", "COACH BODY BUILDER", "COASTGUARD", "COLLECTOR", "COLLEGE PRESIDENT", "COMPUTER OPERATOR", "CONDUCTOR RAILWAY", "CONDUCTOR ROAD TRANSPORT", "CONFECTIONARY MAKERS", "CONSTRUCTION WORKER", "CONTINOUS STILL OPERATOR", "CONTRACTOR", "COOK", "COPRA MAKER", "COURT BAILIFFS", "CRAFTSMEN", "CRANE OPERATOR", "CUSTOM BROKER", "CUTTER", "DANCER", "DEALERS", "DEAN ADMINISTRATOR", "DECORATOR", "DELIVERY BOY", "DENTAL CLINIC CLERK", "DENTAL TECHNICIAN", "DENTIST", "DESIGNER", "DIETICIAN", "DIRECTOR", "DISC JOCKEY", "DISHWASHER", "DISPATCHER", "DIVER", "DOCTOR", "DRAFTSMAN", "DRESSMAKER", "DRIVER", "DRY CLEANER", "EDITOR NEWSPAPER", "EDP MACHINE OPERATOR", "ELECTED GOVERNMENT OFFICIALS (EGO)", "ELECTRICAL ENGINEER", "ELECTRICAL WORKER", "ELECTRICIAN", "ELEMENTARY TEACHER", "EMBALMER", "ENGINEER", "ENGINEER OFFICER", "ENLISTED MEN", "EX-ARMY", "FACTORY WORKERS", "FAITH HEALER", "FARM ADMINISTRATOR", "FARM MANAGER", "FARM OPERATOR", "FARM OWNER", "FARMER", "FIREMAN", "FISH CLASSIFIER", "FISHERMAN", "FISHPOND OPERATORS", "FITNESS INSTRUCTOR", "FLIGHT STEWARD", "FLOOR MANAGER ENTERTAINER", "FOOD PROCESSOR N.E.C.", "FOOTWEAR SEWER", "FOREMAN", "FOREST RANGER", "FREELANCE LABORER", "FREIGHT HANDLERS CARGADORS", "FRUIT DEALER", "FURNACEMAN GLASS", "FURNITURE MAKER", "G.R.O.", "GARBAGE COLLECTOR", "GARDENER", "GAS BOY", "GENERAL EMPLOYEE", "GENERATOR SET OPERATOR", "GEODETIC ENGINEER", "GLASS CUTTER", "GLASS FINISHER", "GLASS FORMER", "GLAZIER", "GOVERNMENT EMPLOYEE", "GRAIN MILLER & RELATED PRODUCTS", "HAIR DRESSER", "HEAD OF MINISTRY/DEPARTMENT", "HEAD OF OFFICE-EXECUTIVE", "HEALTH WORKER", "HEAVY EQUIPMENT OPERATOR", "HELPER", "HOSPITAL ATTENDANT", "HOSTESS TAXIDANCERS", "HOTEL ROOMBOY", "HOUSEBOY", "HOUSEKEEPER", "HOUSEKEEPING STEWARD", "HR MANAGER", "INDUSTRIAL ENGINEER", "INFORMATION TECHNOLOGY (IT)", "INSPECTOR, COMMUNICATION", "INSPECTOR, TRANSPORT", "INSTRUCTOR", "INSURANCE AGENT", "INSURANCE SALESMAN", "JAIL GUARD", "JAIL INSPECTOR", "JAIL WARDEN", "JANITOR", "JEEPNEY DRIVER", "JOBLESS", "JOURNALIST", "JUDGE", "KARGADOR", "KITCHEN WORKER", "LABORATORY TECHNICIANS", "LAUNDERER", "LAVENDERAS IN PRIVATE", "LAWYER", "LIASON OFFICER", "LIBRARIAN", "LIFE GUARD", "LINEMAN", "LOGGER", "LOGISTICS EMPLOYEE", "LUMBER MAN", "MACHINE OPERATOR", "MACHINE TOOL OPERATOR", "MAID", "MAKER OF NATIVE POTTERY", "MANAGEMENT ANALYST", "MANAGER", "MANGHIHILOT (MASSAGE THERAPIST)", "MANICURIST", "MANUFACTURERS", "MARINE ENGINEER", "MARKET INSPECTOR", "MARKET SWEEPER", "MARKET VENDORS", "MASON", "MASSAGE BATHOUSE ATTENDANT", "MEAT CUTTER", "MECHANIC REPAIRMAN", "MECHANICAL ENGINEER", "MECHANICAL REPAIRMAN", "MECHANICS", "MEDICAL CLERK", "MEDICAL REPRESENTATIVE", "MEDICAL SPECIALIST", "MEDICAL TECHNICIAN", "MERCHANDISER", "MESSENGER", "METER READERS CLERK", "MIDWIVES", "MINER", "MINISTER", "MISSIONARY", "MODEL", "MOTORCYCLE TAXI DRIVER (ANGKAS/GRAB/JOYRIDE)", "MUSICIAN", "NEW WORKERS SEEKING EMPLOYMENT", "NEW, VENDOR, NEWSBOARDS, NEWSBOY", "NGO", "NONE", "NUN", "NURSE", "NURSERY WORKER", "NURSING AIDE", "NUTRITIONIST", "OFFICER CLERK", "OFFICERS", "OPTOMETRIST", "OTHER AGRICULTURAL SCIENTIST", "OTHER BIOLOGICAL SCIENTIST", "OTHER ENGINEER, NEC", "OTHER PROF OCCUPATIONS N.E.C.", "OTHER WORKERS IN LEGAL OCCUPATION N.E.C.", "OVERSEAS FILIPINO WORKER", "PACKERS", "PAINTER", "PATHOLOGIST", "PDEA AGENT", "PEDDLER", "PEDICAB DRIVER", "PENSIONER", "PERSONNEL SPECIALIST", "PHARMACIST", "PHIL. ARMY", "PHILIPPINE AIR FORCE", "PHILIPPINE NAVY", "PHILLIPINE MARINE", "PHOTOGRAPHER", "PHYSICAL THERAPIST", "PHYSICIAN", "PILOT", "PIPE FITTER", "PLUMBER", "POLICE AIDE - CVO", "POLICE OFFICER", "POLITICAL SCIENTIST", "PORTER", "POTTER", "POULTRY WORKER/LIVESTOCK", "PRESIDENT, PRIVATE COMPANY", "PRIEST", "PRINCIPAL", "PRISON GUARD/JAIL GUARD", "PRIVATE DETECTIVE", "Private Employee/Corporate Employee", "PROFESSOR", "PROGRAMMER", "PROSECUTOR", "PSYCHOLOGIST", "PURCHASER", "QUARRYMAN", "RADIO ANNOUNCER", "RADIO COMMUNICATION OPERATOR", "RADIOLOGIST", "REAL ESTATE AGENT", "REAL ESTATE BROKER", "RECEPTIONIST", "REPAIRMAN", "REPORTER", "RESEARCH TECHNICIANS", "RESEARCHER", "RETAILMAN", "RETIRED EMPLOYEE", "ROOM BOY/GIRL", "RUBBER PLANTATION WORKER", "RUBBER TREE TAPPER", "SAILOR", "SALES CONSULTANT", "SALES REPRESENTATIVE", "SALESMAN N.E.C.", "SALESMAN OF SECURITIES", "SALESMAN, BUSINESS SERVICES", "SAND AND GRAVEL WORKER", "SCAVENGER", "SCHOOL ADMINISTRATOR", "SCHOOL SUPERVISOR", "SCULPTOR", "SEAMAN", "SECONDARY TEACHER", "SECRETARIAT", "SECURITY GUARD", "SECURITY OFFICER", "SELF-EMPLOYED", "SERVICE CREW", "SEWER TEXTILE PRODUCTS", "SHELLFISH AND OYSTER GATHERER", "SHERIFF/DEPUTY", "SHIP OFFICER", "SHOEMAKER", "SIDEWALK VENDOR", "SINGER", "SLAUGHTER HOUSE WORKER", "SOCIAL WELFARE WORKERS", "SOLDIER/MILITARY", "SPORTSMAN", "STATISTICIAN", "STENOGRAPHER", "STOREKEEPER", "STREET SWEEPER", "STUDENT", "SUPERVISOR", "SUPERVISOR, TRANSPORT", "SURGEON", "SURVEYOR", "SYSTEM ANALYST", "TAILOR", "TAMBAY", "TAXI DRIVER", "TEACHER", "TECHNICIAN", "TELEGRAPH OPERATOR", "TELEPHONE OPERATOR", "TOURIST", "TRADERS MERCHANT BUY AND SELL", "TRAFFIC CONTROLLER", "TRANSPORT WORKER", "TRAVELLING SALESMAN", "TREASURER", "TRICYCLE DRIVER", "TRUCK DRIVER", "UPHOLSTERER", "USHER ENTERTAINER", "VENDOR", "VETERINARIAN", "VULCANIZER", "WAITER", "WAITRESS", "WARE HOUSEMAN", "WATCH REPAIRER/CLOCK REPAIRER", "WATCHMAN/GUARDS", "WELDER", "WHOLESALE", "WINE MAKER", "WOOD CARVER", "WOOD WORKER", "WOOD WORKING MACHINE SETTER", "WORKER IN COMMUNICATION", "WORKER NOT REPORTING ANY OCCUPATION", "WORKING PROPRIETOR", "WRITERS"]

            sus_occupation = st.selectbox("Occupation",occupation_list,index=None, key=generate_key("sus_occupation", index))

            sector_list = ["ABU SAYAF", "AFP", "FARMER", "LABOR", "MEDIA", "MEDICAL", "MILF", "MNLF", "OFW", "OUT OF SCHOOL", "PASTORAL", "PEASANTS", "PNP", "POLITICIAN", "PROFESSIONL", "TRANSPORT", "YOUTH"]
            sus_sector = st.selectbox("Sector/Affliation",sector_list,index=None, key=generate_key("sus_sector", index))

        with col23:
            civil_statuses = ["Single", "Married", "Divorced", "Separated", "Widowed", "Annulled", "Legitimated"]
            sus_civil_status = st.selectbox("Civil Status",civil_statuses,index=None, key=generate_key("sus_civil_status", index))

            ethnic_list = ["BAJAO", "BATANGUEñO", "BICOL", "BULAKEñO", "CAGAYANON", "CEBUANA", "CEBUANO", "CHABACANA", "IGOROT", "ILOCANO", "ILOKANO", "ILONGGO", "ILONGO/HILIGAYNON", "IRANON", "JAMAMAPUN", "KALAGAN", "MAGUINDANAON", "MANGYAN", "MARANAO", "MUSLIM", "OTHERS", "PAMPANGA", "PANGASINAN", "SAMAL", "SIBUYAN MANGYAN TAGA-BUKID", "TAGALOG", "TAGBANWA", "TAO'T BATO", "TAUSUG", "WARAY", "ZAMBAL"]
            sus_ethnic = st.selectbox("Ethnic Group",ethnic_list,index=None, key=generate_key("sus_ethnic", index))

        # Create a dictionary of the data
        data = {
            "pro": pro,
            "ppo_cpo": ppo_cpo,
            "mps_cps": mps_cps,
            "sus_fname": sus_fname,
            "sus_midname": sus_midname,
            "sus_lname": sus_lname,
            "sus_qlfr": sus_qlfr,
            "sus_alias": sus_alias,
            "sus_gndr": sus_gndr,
            "sus_age": sus_age,
            "sus_distprov": sus_distprov,
            "sus_cityMun": sus_cityMun,
            "sus_brgy": sus_brgy,
            "sus_strName": sus_strName
        }

        # Mapping of field names to user-friendly names
        field_name_mapping = {
            "pro": "PRO",
            "ppo_cpo": "PPO",
            "mps_cps": "Station",
            "sus_fname": "Suspect's First Name",
            "sus_midname": "Suspect's Middle Name",
            "sus_lname": "Suspect's Last Name",
            "sus_qlfr": "Qualifier",
            "sus_alias": "Alias",
            "sus_gndr": "Gender",
            "sus_age": "Age",
            "sus_distprov": "District/Province",
            "sus_cityMun": "City/Municipality",
            "sus_brgy": "Barangay",
            "sus_strName": "House No./Street Name"
        }

        # Validate the data using Pydantic
        suspect_data = ""
        try:
            suspect_data = SuspectData_Validation(**data)
            # Data is valid, proceed with database operations
            return suspect_data
        except ValidationError as e:
            for error in e.errors():
                field = error['loc'][0]
                message = error['msg']
                user_friendly_field = field_name_mapping.get(field, field)
                st.error(f"Error in {user_friendly_field}: {message}")
        finally:
            if suspect_data:
                return dict(suspect_data)
    

def addSuspect(mps_cps, ppo_cpo, pro):

    # Initialize session state for the number of victims
    if 'suspect_count' not in st.session_state:
        st.session_state.suspect_count = 1

    victim_data_list = []

    # Add a victim for each count in the session state
    for i in range(st.session_state.suspect_count):
        victim_data = SuspectDetails(mps_cps, ppo_cpo, pro, i)
        if victim_data:
            victim_data_list.append(victim_data)

    # Buttons to add or remove victims
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Add Another Suspect", use_container_width=True, type="primary",key="suspect_btn1"):
            st.session_state.suspect_count += 1
            st.rerun()  # Rerun the app to show the new victim form

    with col2:
        if st.button("Remove Last Suspect", use_container_width=True, type="primary",key="suspect_btn2"):
            if st.session_state.victim_count > 1:
                st.session_state.victim_count -= 1
                st.rerun()  # Rerun the app to remove the last victim form