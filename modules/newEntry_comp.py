import streamlit as st
from datetime import date
import requests
from config.database import api_endpoint

# Fomat the dates
def dateseq():
    # Get the current date
    current_date = date.today()

    # Format the date to 'YYYYMM'
    formatted_date = current_date.strftime('%Y%m')

    return formatted_date

# Function to fetch seq by mps_cps
st.cache_data(ttl="60m")
def fetch_seq_by_mps_cps(mps_cps):
    try:
        response = requests.get(f"{api_endpoint}/stations/{mps_cps}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

# Function to get the next entry number (placeholder)
def get_next_entry_number(mps_cps):
    try:
        response = requests.get(f"{api_endpoint}/next_entry_number/{mps_cps}")
        response.raise_for_status()
        return response.json()["next_entry_number"]
    except requests.exceptions.RequestException as e:
        # st.error(f"Error fetching the next entry number: {e}")
        return 1



def newEntry(mps_cps):
    
    # Get the Blotter Sequence

    # Fetch the station sequence from the backend
    station_sequences = fetch_seq_by_mps_cps(mps_cps)


    if not station_sequences:
        st.error(f"No data found for mps_cps: {mps_cps}")
        return

    # Assuming we take the first result
    seq = station_sequences[0]['seq'] if station_sequences else ''

    # Get the Blotter Sequence
    entrySeq, dateMon, entryNum = st.columns(3)

    entrySeq_value = entrySeq.text_input("Station Code", seq, disabled=True,key="entrySeq")
    dateMon_value = dateMon.text_input("Year|Month Encoded", dateseq(), disabled=True,key="dateMon")

    # Auto-suggest for the next entry number
    next_value = get_next_entry_number(mps_cps)
    entryNum_value = entryNum.text_input("Entry Number", value=next_value)

    combined_value = f"{entrySeq_value}-{dateMon_value}-{entryNum_value}"

    # Store the combined_value in the session state
    st.session_state.combined_value = combined_value

    if st.button("New Entry", type="primary", use_container_width=True):
        # Check if the entry number already exists
        response = requests.get(f"{api_endpoint}/check_entry/{combined_value}")
        if response.status_code == 200:
            result = response.json()
            if result.get("exists"):
                st.error(f"Entry number {combined_value} already exists.")
                return
        
        # If the entry number does not exist, proceed with creating a new entry
        response = requests.post(f"{api_endpoint}/temp-entries/", json={"combined_value": st.session_state.combined_value})
        if response.status_code == 200:
            st.session_state.temp_entry_id = response.json()["id"]
            # print(st.session_state.combined_value)
            st.switch_page("pages/entry_form.py")
        else:
            st.error("Failed to store the entry")

    return combined_value
    