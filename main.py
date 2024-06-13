from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from typing import Annotated,  List, Optional
from uuid import UUID
import bcrypt
import config.models as models
from config.database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, time
from modules import dataValidation as dv
import pandas as pd
from sqlalchemy.orm import aliased


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# Error Logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception("Exception occurred while processing request")
        response = JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"}
        )
    return response

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


# ============================================
# Pydantic Classes
# ============================================
class UserBaseModel(BaseModel):
    id: UUID
    username: str
    password: str
    is_logged_in: bool = False
    failed_login_attempts: int

class UserLoginModel(BaseModel):
    username: str
    password: str

# Pydantic schema for Station_Sequence model
class StationSequence(BaseModel):
    seq: str
    mps_cps: str
    ppo_cpo: str

    class Config:
        from_attributes = True

# Pydantic model for TempEntry
class TempEntryCreate(BaseModel):
    combined_value: str

class TempEntryResponse(BaseModel):
    id: int
    combined_value: str

    class Config:
        from_attributes = True
# Pydantic model for TempEntry



# Pydantic model for TempEntry for Editing
class TempEntryEdit(BaseModel):
    entry_number: str

class TempEntryEditResponse(BaseModel):
    id: int
    entry_number: str

    class Config:
        from_attributes = True
# Pydantic model for TempEntry for Editing



class Brgy_Value(BaseModel):
    id: int
    brgy: str

class City_Mun_Value(BaseModel):
    id: int
    city_mun: str

class Province_Value(BaseModel):
    id: int
    province: str

class Province_City_Mun_Value_ResponseModel(BaseModel):
    brgy_values: List[Brgy_Value]
    city_mun_value: Optional[City_Mun_Value]
    province_value: Optional[Province_Value]


class Offense_Classification(BaseModel):
    id: int
    incidents: str
    classification: str



class CaseDetailsModel(BaseModel):
    entry_number: str
    pro: str
    ppo_cpo: str
    mps_cps: str
    offense: str
    offense_class: str
    case_status: str
    check: bool

    narrative: str
    date_reported: date
    time_reported: Optional[time] = None
    date_committed: Optional[date] = None
    time_committed: Optional[time] = None

# Define the Pydantic model for the response data
class CaseData(BaseModel):
    entry_number: str
    pro: str
    ppo_cpo: str
    mps_cps: str
    offense: str
    case_status: str
    date_reported: date
    time_reported: time
    date_committed: date
    time_committed: time
    victim_details: str
    suspect_details: str





# ============================================
# END of Pydantic Classes
# ============================================


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Get all USERS
@app.get("/users/")
async def get_users(db: db_dependency):
    users = db.query(models.UserBase).all()
    return users

@app.post("/login/")
async def login(user: UserLoginModel, db: db_dependency):
    db_user = db.query(models.UserBase).filter(models.UserBase.username == user.username).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not verify_password(user.password, db_user.password):
        db_user.failed_login_attempts += 1
        db.add(db_user)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    db_user.is_logged_in = True
    db_user.failed_login_attempts = 0  # Reset on successful login
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Login successful", "user": db_user}


# Endpoint to fetch `seq` by `mps_cps`
@app.get("/stations/{mps_cps}", response_model=List[StationSequence])
async def read_station_by_mps_cps(mps_cps: str, db: Session = Depends(get_db)):
    station_sequence = db.execute(select(models.Station_Sequence).where(models.Station_Sequence.mps_cps == mps_cps)).scalars().all()
    
    if not station_sequence:
        raise HTTPException(status_code=404, detail="Station sequence not found")

    return station_sequence



# Endpoint to store a new temp entry
@app.post("/temp-entries/", response_model=TempEntryResponse)
async def create_temp_entry(entry: TempEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.TempEntry(combined_value=entry.combined_value)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# Endpoint to delete a temp entry
@app.delete("/temp-entries/{entry_id}", response_model=TempEntryResponse)
async def delete_temp_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.TempEntry).filter(models.TempEntry.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(db_entry)
    db.commit()
    return db_entry

# Endpoint to get all temp entries (optional, for debugging)
@app.get("/temp-entries/", response_model=List[TempEntryResponse])
async def get_temp_entries(db: Session = Depends(get_db)):
    return db.query(models.TempEntry).all()


# Endpoint to get Brgy_Value and City_Mun_Value based on mps_cps
@app.get("/brgy-city-mun/{mps_cps}", response_model=Province_City_Mun_Value_ResponseModel)
async def get_brgy_city_mun(mps_cps: str, db: db_dependency):

    # Query to get Brgy_Value
    brgy_query = select(
        models.Province_Brgy_Details.id,
        models.Province_Brgy_Details.brgy
    ).where(models.Province_Brgy_Details.mps_cps == mps_cps)
    
    brgy_results = db.execute(brgy_query).fetchall()
    brgy_values = [Brgy_Value(id=row[0], brgy=row[1]) for row in brgy_results]

    # Query to get the first City_Mun_Value
    city_mun_query = select(
        models.Province_Brgy_Details.id,
        models.Province_Brgy_Details.mun_city
    ).where(models.Province_Brgy_Details.mps_cps == mps_cps).limit(1)

    city_mun_result = db.execute(city_mun_query).first()

    city_mun_value = None
    if city_mun_result:
        city_mun_value = City_Mun_Value(id=city_mun_result[0], city_mun=city_mun_result[1])

    # Query to get the first Province
    province_query = select(
        models.Province_Brgy_Details.id,
        models.Province_Brgy_Details.province
    ).where(models.Province_Brgy_Details.mps_cps == mps_cps).limit(1)

    province_result = db.execute(province_query).first()

    province_value = None
    if province_result:
        province_value = Province_Value(id=province_result[0], province=province_result[1])

    # Return the results as a dictionary
    return {
        "brgy_values": brgy_values,
        "city_mun_value": city_mun_value,
        "province_value": province_value
    }


# Endpoint to get offense classifications
@app.get("/offense_classifications")
async def get_offense_classifications(db: Session = Depends(get_db)):
    offenses = db.query(models.Offense).all()
    return [{"incidents": offense.incidents} for offense in offenses]




@app.post("/case-details/")
async def create_case_details(case_details: CaseDetailsModel, db: Session = Depends(get_db)):
    # Create a new database object
    db_case_details = models.CaseDetails(
		pro= case_details.pro,
        ppo_cpo= case_details.ppo_cpo,
        mps_cps= case_details.mps_cps,
        entry_number=case_details.entry_number,
        offense=case_details.offense,
        offense_class=case_details.offense_class,
        case_status=case_details.case_status,
        check=case_details.check,
        narrative=case_details.narrative,
        date_reported=case_details.date_reported,
        time_reported=case_details.time_reported,
        date_committed=case_details.date_committed,
        time_committed=case_details.time_committed
    )

    # Add it to the database
    db.add(db_case_details)
    db.commit()
    db.refresh(db_case_details)

    return db_case_details


@app.post("/victim-new-entry/", response_model=dv.New_Entry_VictimData_Validation)
async def enter_victim(victim: dv.New_Entry_VictimData_Validation, db: Session = Depends(get_db)):
    db_victim = models.Victim_Details(**victim.model_dump())
    db.add(db_victim)
    db.commit()
    db.refresh(db_victim)
    return db_victim



@app.post("/suspect-new-entry/", response_model=dv.New_Entry_SuspectData_Validation)
async def enter_victim(suspect: dv.New_Entry_SuspectData_Validation, db: Session = Depends(get_db)):
    db_suspect = models.Suspect_Details(**suspect.model_dump())
    db.add(db_suspect)
    db.commit()
    db.refresh(db_suspect)
    return db_suspect

# UPDATE CASES IN THE DATABASE
@app.put("/update-case-details/{entry_number}")
async def update_case_details(entry_number: str, case_details: CaseDetailsModel, db: Session = Depends(get_db)):
    db_case_details = db.query(models.CaseDetails).filter(models.CaseDetails.entry_number == entry_number).first()
    if db_case_details is None:
        raise HTTPException(status_code=404, detail="Case details not found")

    for key, value in case_details.model_dump().items():
        setattr(db_case_details, key, value)

    db.commit()
    db.refresh(db_case_details)

    return db_case_details

@app.put("/update-victim-details/{entry_number}")
async def update_victim_details(entry_number: str, victim: dv.New_Entry_VictimData_Validation, db: Session = Depends(get_db)):
    db_victim = db.query(models.Victim_Details).filter(models.Victim_Details.entry_number == entry_number).first()
    if db_victim is None:
        raise HTTPException(status_code=404, detail="Victim details not found")

    for key, value in victim.model_dump().items():
        setattr(db_victim, key, value)

    db.commit()
    db.refresh(db_victim)
    
    return db_victim

@app.put("/update-suspect-details/{entry_number}")
async def update_suspect_details(entry_number: str, suspect: dv.New_Entry_SuspectData_Validation, db: Session = Depends(get_db)):
    db_suspect = db.query(models.Suspect_Details).filter(models.Suspect_Details.entry_number == entry_number).first()
    if db_suspect is None:
        raise HTTPException(status_code=404, detail="Suspect details not found")

    for key, value in suspect.model_dump().items():
        setattr(db_suspect, key, value)

    db.commit()
    db.refresh(db_suspect)
    
    return db_suspect



@app.get('/cases')
def get_cases(mps_cps: str, db: Session = Depends(get_db)):
    # Aliases for Victim_Details and Suspect_Details for aggregation
    victims_alias = aliased(models.Victim_Details)
    suspects_alias = aliased(models.Suspect_Details)

    # Subquery to aggregate victim details
    victim_subquery = (
        select(
            victims_alias.entry_number,
            func.string_agg(
                func.concat(
                    victims_alias.vic_fname, ' ', victims_alias.vic_midname, ' ',
                    victims_alias.vic_lname, ' ', victims_alias.vic_qlfr, ' ',
                    victims_alias.vic_alias, ' (', victims_alias.vic_age, '/', victims_alias.vic_gndr, ')'
                ), '; '
            ).label('victim_details')
        )
        .filter(victims_alias.mps_cps == mps_cps)  # Filtering based on mps_cps
        .group_by(victims_alias.entry_number)
        .subquery()
    )

    # Subquery to aggregate suspect details
    suspect_subquery = (
        select(
            suspects_alias.entry_number,
            func.string_agg(
                func.concat(
                    suspects_alias.sus_fname, ' ', suspects_alias.sus_midname, ' ',
                    suspects_alias.sus_lname, ' ', suspects_alias.sus_qlfr, ' ',
                    suspects_alias.sus_alias, ' (', suspects_alias.sus_age, '/', suspects_alias.sus_gndr, ')'
                ), '; '
            ).label('suspect_details')
        )
        .filter(suspects_alias.mps_cps == mps_cps)  # Filtering based on mps_cps
        .group_by(suspects_alias.entry_number)
        .subquery()
    )

    # Main query to select case details and join with victim and suspect details
    query = (
        select(
            models.CaseDetails.entry_number,
            models.CaseDetails.offense,
            models.CaseDetails.case_status,
            models.CaseDetails.date_reported,
            models.CaseDetails.time_reported,
            models.CaseDetails.date_committed,
            models.CaseDetails.time_committed,
            victim_subquery.c.victim_details,
            suspect_subquery.c.suspect_details
        )
        .outerjoin(victim_subquery, models.CaseDetails.entry_number == victim_subquery.c.entry_number)
        .outerjoin(suspect_subquery, models.CaseDetails.entry_number == suspect_subquery.c.entry_number)
        .filter(models.CaseDetails.mps_cps == mps_cps)  # Filtering based on mps_cps
        .order_by(models.CaseDetails.date_encoded.desc())
    )

    # Execute the query
    result = db.execute(query)

    # Fetch all the rows
    rows = result.fetchall()

    # Convert the rows to a DataFrame
    df = pd.DataFrame(rows, columns=[
        "entry_number",
        "offense",
        "case_status",
        "date_reported",
        "time_reported",
        "date_committed",
        "time_committed",
        "victim_details",
        "suspect_details"
    ])

    # Drop the time_reported and time_committed columns if not needed
    df = df.drop(columns=["time_reported", "time_committed"])

    # Rename columns if needed
    df = df.rename(columns={
        "entry_number": "Entry Number",
        "offense": "Offense",
        "case_status": "Case Status",
        "date_reported": "Date Reported",
        "date_committed": "Date Committed",
        "victim_details": "Victim Details",
        "suspect_details": "Suspect Details"
    })

    # Return the DataFrame as a JSON response
    return df

@app.get('/cases-ppo')
def get_cases_ppo(ppo_cpo: str, db: Session = Depends(get_db)):
    # Aliases for Victim_Details and Suspect_Details for aggregation
    victims_alias = aliased(models.Victim_Details)
    suspects_alias = aliased(models.Suspect_Details)

    # Subquery to aggregate victim details
    victim_subquery = (
        select(
            victims_alias.entry_number,
            func.string_agg(
                func.concat(
                    victims_alias.vic_fname, ' ', victims_alias.vic_midname, ' ',
                    victims_alias.vic_lname, ' ', victims_alias.vic_qlfr, ' ',
                    victims_alias.vic_alias, ' (', victims_alias.vic_age, '/', victims_alias.vic_gndr, ')'
                ), '; '
            ).label('victim_details')
        )
        .filter(victims_alias.ppo_cpo == ppo_cpo)  # Filtering based on mps_cps
        .group_by(victims_alias.entry_number)
        .subquery()
    )

    # Subquery to aggregate suspect details
    suspect_subquery = (
        select(
            suspects_alias.entry_number,
            func.string_agg(
                func.concat(
                    suspects_alias.sus_fname, ' ', suspects_alias.sus_midname, ' ',
                    suspects_alias.sus_lname, ' ', suspects_alias.sus_qlfr, ' ',
                    suspects_alias.sus_alias, ' (', suspects_alias.sus_age, '/', suspects_alias.sus_gndr, ')'
                ), '; '
            ).label('suspect_details')
        )
        .filter(suspects_alias.ppo_cpo == ppo_cpo)  # Filtering based on mps_cps
        .group_by(suspects_alias.entry_number)
        .subquery()
    )

    # Main query to select case details and join with victim and suspect details
    query = (
        select(
            models.CaseDetails.entry_number,
            models.CaseDetails.mps_cps,
            models.CaseDetails.offense,
            models.CaseDetails.case_status,
            models.CaseDetails.date_reported,
            models.CaseDetails.time_reported,
            models.CaseDetails.date_committed,
            models.CaseDetails.time_committed,
            victim_subquery.c.victim_details,
            suspect_subquery.c.suspect_details
        )
        .outerjoin(victim_subquery, models.CaseDetails.entry_number == victim_subquery.c.entry_number)
        .outerjoin(suspect_subquery, models.CaseDetails.entry_number == suspect_subquery.c.entry_number)
        .filter(models.CaseDetails.ppo_cpo == ppo_cpo)  # Filtering based on mps_cps
        .order_by(models.CaseDetails.date_encoded.desc())
    )

    # Execute the query
    result = db.execute(query)

    # Fetch all the rows
    rows = result.fetchall()

    # Convert the rows to a DataFrame
    df = pd.DataFrame(rows, columns=[
        "entry_number",
        "mps_cps",
        "offense",
        "case_status",
        "date_reported",
        "time_reported",
        "date_committed",
        "time_committed",
        "victim_details",
        "suspect_details"
    ])

    # Drop the time_reported and time_committed columns if not needed
    df = df.drop(columns=["time_reported", "time_committed"])

    # Rename columns if needed
    df = df.rename(columns={
        "entry_number": "Entry Number",
        "mps_cps": "Station",
        "offense": "Offense",
        "case_status": "Case Status",
        "date_reported": "Date Reported",
        "date_committed": "Date Committed",
        "victim_details": "Victim Details",
        "suspect_details": "Suspect Details"
    })

    # Return the DataFrame as a JSON response
    return df


@app.get('/cases-pro')
def get_cases_pro(pro: str, db: Session = Depends(get_db)):
    # Aliases for Victim_Details and Suspect_Details for aggregation
    victims_alias = aliased(models.Victim_Details)
    suspects_alias = aliased(models.Suspect_Details)

    # Subquery to aggregate victim details
    victim_subquery = (
        select(
            victims_alias.entry_number,
            func.string_agg(
                func.concat(
                    victims_alias.vic_fname, ' ', victims_alias.vic_midname, ' ',
                    victims_alias.vic_lname, ' ', victims_alias.vic_qlfr, ' ',
                    victims_alias.vic_alias, ' (', victims_alias.vic_age, '/', victims_alias.vic_gndr, ')'
                ), '; '
            ).label('victim_details')
        )
        .filter(victims_alias.pro == pro)  # Filtering based on mps_cps
        .group_by(victims_alias.entry_number)
        .subquery()
    )

    # Subquery to aggregate suspect details
    suspect_subquery = (
        select(
            suspects_alias.entry_number,
            func.string_agg(
                func.concat(
                    suspects_alias.sus_fname, ' ', suspects_alias.sus_midname, ' ',
                    suspects_alias.sus_lname, ' ', suspects_alias.sus_qlfr, ' ',
                    suspects_alias.sus_alias, ' (', suspects_alias.sus_age, '/', suspects_alias.sus_gndr, ')'
                ), '; '
            ).label('suspect_details')
        )
        .filter(suspects_alias.pro == pro)  # Filtering based on mps_cps
        .group_by(suspects_alias.entry_number)
        .subquery()
    )

    # Main query to select case details and join with victim and suspect details
    query = (
        select(
            models.CaseDetails.entry_number,
            models.CaseDetails.ppo_cpo,
            models.CaseDetails.mps_cps,
            models.CaseDetails.offense,
            models.CaseDetails.case_status,
            models.CaseDetails.date_reported,
            models.CaseDetails.time_reported,
            models.CaseDetails.date_committed,
            models.CaseDetails.time_committed,
            victim_subquery.c.victim_details,
            suspect_subquery.c.suspect_details
        )
        .outerjoin(victim_subquery, models.CaseDetails.entry_number == victim_subquery.c.entry_number)
        .outerjoin(suspect_subquery, models.CaseDetails.entry_number == suspect_subquery.c.entry_number)
        .filter(models.CaseDetails.pro == pro)  # Filtering based on mps_cps
        .order_by(models.CaseDetails.date_encoded.desc())
    )

    # Execute the query
    result = db.execute(query)

    # Fetch all the rows
    rows = result.fetchall()

    # Convert the rows to a DataFrame
    df = pd.DataFrame(rows, columns=[
        "entry_number",
        "ppo_cpo",
        "mps_cps",
        "offense",
        "case_status",
        "date_reported",
        "time_reported",
        "date_committed",
        "time_committed",
        "victim_details",
        "suspect_details"
    ])

    # Drop the time_reported and time_committed columns if not needed
    df = df.drop(columns=["time_reported", "time_committed"])

    # Rename columns if needed
    df = df.rename(columns={
        "entry_number": "Entry Number",
        "ppo_cpo":"PPO",
        "mps_cps": "Station",
        "offense": "Offense",
        "case_status": "Case Status",
        "date_reported": "Date Reported",
        "date_committed": "Date Committed",
        "victim_details": "Victim Details",
        "suspect_details": "Suspect Details"
    })

    # Return the DataFrame as a JSON response
    return df

@app.get("/check_entry/{entry_number}")
async def check_entry(entry_number: str, db: Session = Depends(get_db)):
    result = db.execute(select(models.CaseDetails).where(models.CaseDetails.entry_number == entry_number)).first()
    if result:
        return {"exists": True}
    else:
        return {"exists": False}
    

# FastAPI endpoint to get the next entry number based on mps_cps
@app.get("/next_entry_number/{mps_cps}")
async def get_next_entry_number(mps_cps: str, db: Session = Depends(get_db)):
    latest_entry = db.query(models.CaseDetails).filter(models.CaseDetails.mps_cps == mps_cps).order_by(models.CaseDetails.date_encoded.desc()).first()
    if not latest_entry:
        raise HTTPException(status_code=404, detail="No entries found for this mps_cps")
    
    latest_entry_number = int(latest_entry.entry_number.split('-')[-1])
    next_entry_number = latest_entry_number + 1
    return {"next_entry_number": next_entry_number}


@app.get('/search_case')
async def get_cases(entry_number: str, mps_cps: str, db: Session = Depends(get_db)):
    # Aliases for Victim_Details and Suspect_Details for aggregation
    victims_alias = aliased(models.Victim_Details)
    suspects_alias = aliased(models.Suspect_Details)

    # Subquery to aggregate victim details
    victim_subquery = (
        select(
            victims_alias.entry_number,
            func.string_agg(
                func.concat(
                    victims_alias.vic_fname, ' ', victims_alias.vic_midname, ' ',
                    victims_alias.vic_lname, ' ', victims_alias.vic_qlfr, ' ',
                    victims_alias.vic_alias, ' (', victims_alias.vic_age, '/', victims_alias.vic_gndr, ')'
                ), '; '
            ).label('victim_details')
        )
        .filter(victims_alias.mps_cps == mps_cps)  # Filtering based on mps_cps
        .group_by(victims_alias.entry_number)
        .subquery()
    )

    # Subquery to aggregate suspect details
    suspect_subquery = (
        select(
            suspects_alias.entry_number,
            func.string_agg(
                func.concat(
                    suspects_alias.sus_fname, ' ', suspects_alias.sus_midname, ' ',
                    suspects_alias.sus_lname, ' ', suspects_alias.sus_qlfr, ' ',
                    suspects_alias.sus_alias, ' (', suspects_alias.sus_age, '/', suspects_alias.sus_gndr, ')'
                ), '; '
            ).label('suspect_details')
        )
        .filter(suspects_alias.mps_cps == mps_cps)  # Filtering based on mps_cps
        .group_by(suspects_alias.entry_number)
        .subquery()
    )

    # Main query to select case details and join with victim and suspect details
    query = (
        select(
            models.CaseDetails.entry_number,
            models.CaseDetails.mps_cps,
            models.CaseDetails.offense,
            models.CaseDetails.case_status,
            models.CaseDetails.date_reported,
            models.CaseDetails.time_reported,
            models.CaseDetails.date_committed,
            models.CaseDetails.time_committed,
            models.CaseDetails.date_encoded,
            victim_subquery.c.victim_details,
            suspect_subquery.c.suspect_details
        )
        .outerjoin(victim_subquery, models.CaseDetails.entry_number == victim_subquery.c.entry_number)
        .outerjoin(suspect_subquery, models.CaseDetails.entry_number == suspect_subquery.c.entry_number)
        .filter(models.CaseDetails.entry_number.like(f"%{entry_number}%"), models.CaseDetails.mps_cps == mps_cps)  # Filtering based on entry_number and mps_cps
        .order_by(models.CaseDetails.date_encoded.desc())
    )

    # Execute the query
    result = db.execute(query)
    cases = result.fetchall()

    if not cases:
        raise HTTPException(status_code=404, detail="Cases not found")

    # Optionally, convert the result to a list of dictionaries
    cases_list = [
        {
            'entry_number': case.entry_number,
            'mps_cps': case.mps_cps,
            'offense': case.offense,
            'date_encoded': case.date_encoded,
            'case_status': case.case_status,
            'date_reported': case.date_reported,
            'time_reported': case.time_reported,
            'date_committed': case.date_committed,
            'time_committed': case.time_committed,
            'victim_details': case.victim_details,
            'suspect_details': case.suspect_details,
        }
        for case in cases
    ]

    return cases_list


@app.get('/count_cases_encoded')
async def get_cases_count(mps_cps: str, db: Session = Depends(get_db)):
    count = db.query(models.CaseDetails).filter(models.CaseDetails.mps_cps == mps_cps).count()
    return {"count": count}

@app.get('/count_cases_encoded-ppo')
async def get_cases_count_ppo(ppo_cpo: str, db: Session = Depends(get_db)):
    count = db.query(models.CaseDetails).filter(models.CaseDetails.ppo_cpo == ppo_cpo).count()
    return {"count": count}

@app.get('/count_cases_encoded-pro')
async def get_cases_count_ppo(pro: str, db: Session = Depends(get_db)):
    count = db.query(models.CaseDetails).filter(models.CaseDetails.pro == pro).count()
    return {"count": count}


# Get Details for Editing Entries

@app.get('/get_victim_details')
async def get_victim_details(entry_number: str, db: Session = Depends(get_db)):
    cases = db.query(models.Victim_Details).filter(models.Victim_Details.entry_number == entry_number).all()
    if not cases:
        raise HTTPException(status_code=404, detail="Cases not found")
    return cases

@app.get('/get_suspect_details')
async def get_suspect_details(entry_number: str, db: Session = Depends(get_db)):
    cases = db.query(models.Suspect_Details).filter(models.Suspect_Details.entry_number == entry_number).all()
    if not cases:
        raise HTTPException(status_code=404, detail="Cases not found")
    return cases

@app.get('/get_case_details')
async def get_case_details(entry_number: str, db: Session = Depends(get_db)):
    cases = db.query(models.CaseDetails).filter(models.CaseDetails.entry_number == entry_number).all()
    if not cases:
        raise HTTPException(status_code=404, detail="Cases not found")
    return cases


# Endpoint to store a new temp entry
@app.post("/temp-edit-entries/", response_model=TempEntryEditResponse)
async def create_edit_temp_entry(entry: TempEntryEdit, db: Session = Depends(get_db)):
    db_entry = models.TempEditEntry(entry_number=entry.entry_number)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# Endpoint to delete a temp entry
@app.delete("/temp-edit-entries/{entry_id}", response_model=TempEntryEditResponse)
async def delete_edit_temp_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.TempEditEntry).filter(models.TempEditEntry.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(db_entry)
    db.commit()
    return db_entry

# Endpoint to get all temp entries (optional, for debugging)
@app.get("/temp-edit-entries/", response_model=List[TempEntryEditResponse])
async def get__edit_temp_entries(db: Session = Depends(get_db)):
    return db.query(models.TempEditEntry).all()