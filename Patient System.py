import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import requests

config = {
    'user': 'root',
    'password': '***********',
    'host': '*********',
    'port': 3306,
    'database': 'patient'
}

def create_connection():
    """Create a connection to the MySQL database."""
    db = mysql.connector.connect(**config)
    return db

def create_patients_table(db):
    """Create the patients table in the database."""
    cursor = db.cursor()

    create_patients_table_query = """
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        age INT,
        contact_number VARCHAR(15),
        address VARCHAR(255),
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        email VARCHAR(255)
    )
    """
    cursor.execute(create_patients_table_query)
    db.commit()
    st.write("Patients table created successfully.")

def create_appointments_table(db):
    """Create the appointments table in the database."""
    cursor = db.cursor()

    create_appointments_table_query = """
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        appointment_date DATE,
        appointment_time TIME,
        doctor_name VARCHAR(255),
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
    """
    cursor.execute(create_appointments_table_query)
    db.commit()
    st.write("Appointments table created successfully.")

def insert_patient_record(db, name, age, contact_number, email, address):
    """Insert a new patient record into the 'patients' table."""
    cursor = db.cursor()

    insert_patient_query = """
    INSERT INTO patients (name, age, contact_number, email, address)
    VALUES (%s, %s, %s, %s, %s)
    """
    patient_data = (name, age, contact_number, email, address)

    cursor.execute(insert_patient_query, patient_data)
    db.commit()
    st.write("Patient record inserted successfully.")

def fetch_all_patients(db):
    """Fetch all records from the 'patients' table."""
    cursor = db.cursor()

    select_patients_query = "SELECT * FROM patients"
    cursor.execute(select_patients_query)
    patients = cursor.fetchall()

    return patients

def fetch_patient_by_id(db, patient_id):
    """Fetch a patient's record from the 'patients' table based on ID."""
    cursor = db.cursor()

    select_patient_query = "SELECT * FROM patients WHERE patient_id = %s"
    cursor.execute(select_patient_query, (patient_id,))
    patient = cursor.fetchone()

    return patient

def delete_patient_record(db, delete_option, delete_value):
    """Delete a patient record from the 'patients' table based on ID, name, or contact number."""
    cursor = db.cursor()

    if delete_option == "Patient ID":
        delete_patient_query = "DELETE FROM patients WHERE patient_id = %s"
    elif delete_option == "Name":
        delete_patient_query = "DELETE FROM patients WHERE name = %s"


    cursor.execute(delete_patient_query, (delete_value,))
    db.commit()
    st.write("Patient record deleted successfully.")

def insert_appointment_record(db, patient_id, appointment_date, appointment_time, doctor_name, notes):
    """Insert a new appointment record into the 'appointments' table."""
    cursor = db.cursor()

    appointment_time = appointment_time.strftime("%H:%M:%S")
    appointment_date = appointment_date.strftime("%Y-%m-%d")
    insert_appointment_query = """
    INSERT INTO appointments (patient_id, appointment_date, appointment_time, doctor_name, notes)
    VALUES (%s, %s, %s, %s, %s)
    """
    appointment_data = (patient_id, appointment_date, appointment_time, doctor_name, notes)

    cursor.execute(insert_appointment_query, appointment_data)
    db.commit()
    st.write("Appointment record added successfully.")

def show_all_appointments(db):
    """Fetch and display all appointment records."""
    cursor = db.cursor()

    select_query = """
    SELECT appointment_id, patient_id, appointment_date, appointment_time, doctor_name, notes FROM appointments
    """
    cursor.execute(select_query)
    records = cursor.fetchall()

    if records:
        st.subheader("All Appointment Records")
        df = pd.DataFrame(records, columns=['appointment_id', 'Patient ID', 'Appointment Date', 'Appointment Time', 'Doctor Name', 'Notes'])
        df['Appointment Time'] = df['Appointment Time'].apply(
            lambda x: x.strftime('%H:%M') if isinstance(x, datetime) else str(x))

        st.dataframe(df)
    else:
        st.write("No appointments found")


def edit_appointment(db):
    pass


def search_appointment(db):
    """Search for an appointment based on appointment_ID, Patient ID, or Doctor Name."""
    search_option = st.selectbox("Select search option", ["appointment_id", "Patient ID", "Doctor Name"], key="search_option")
    search_value = st.text_input("Enter search value", key="search_value")

    appointment = None

    if st.button("Search"):
        if search_option == "appointment_ID":
            appointment = fetch_appointment_by_id(db, search_value)
        elif search_option == "Patient ID":
            appointment = fetch_appointment_by_patient_id(db, search_value)
        elif search_option == "Doctor Name":
            appointment = fetch_appointment_by_doctor_name(db, search_value)

        if appointment:
            st.subheader("Appointment Details")
            df = pd.DataFrame([appointment], columns=['appointment_ID', 'Patient ID', 'Appointment Date', 'Appointment Time', 'Doctor Name', 'Notes'])
            st.dataframe(df)
            st.session_state.edit_appointment = appointment
        else:
            st.write("Appointment not found")

    if 'edit_appointment' in st.session_state:
        edit_appointment(db)

def fetch_appointment_by_id(db, appointment_id):
    """Fetch an appointment's record from the 'appointments' table based on ID."""
    cursor = db.cursor()

    select_appointment_query = """
    SELECT appointment_id, patient_id, appointment_date, appointment_time, doctor_name, notes
    FROM appointments
    WHERE appointment_id = %s
    """
    cursor.execute(select_appointment_query, (appointment_id,))
    appointment = cursor.fetchone()

    return appointment

def fetch_appointment_by_patient_id(db, patient_id):
    """Fetch an appointment's record by patient_id."""
    query = """
    SELECT appointment_id, patient_id, appointment_date, appointment_time, doctor_name, notes
    FROM appointments
    WHERE patient_id = %s
    """
    cursor = db.cursor()
    cursor.execute(query, (patient_id,))
    appointment = cursor.fetchone()
    return appointment

def fetch_appointment_by_doctor_name(db, doctor_name):
    """Fetch an appointment's record by doctor_name."""
    query = """
    SELECT appointment_id, patient_id, appointment_date, appointment_time, doctor_name, notes
    FROM appointments
    WHERE doctor_name = %s
    """
    cursor = db.cursor()
    cursor.execute(query, (doctor_name,))
    appointment = cursor.fetchone()
    return appointment

def update_patient_info(db, patient_id, new_name, new_age, new_contact, new_email, new_address):
    """Update a patient's record in the 'patients' table."""
    cursor = db.cursor()

    update_patient_query = """
    UPDATE patients
    SET name = %s, age = %s, contact_number = %s, email = %s, address = %s
    WHERE patient_id = %s
    """
    patient_data = (new_name, new_age, new_contact, new_email, new_address, patient_id)

    cursor.execute(update_patient_query, patient_data)
    db.commit()
    st.write("Patient record updated successfully.")


def fetch_patient_by_contact(db, search_value):
    pass



def update_patient_record(db):
    """Update a patient's record."""
    search_option = st.selectbox("Select search option", ["Patient ID", "Contact Number"], key="search_option")
    search_value = st.text_input("Enter search value", key="search_value")

    if st.button("Search :magic_wand:"):
        if search_option == "Patient ID":
            patient = fetch_patient_by_id(db, search_value)
        elif search_option == "Contact Number":
            patient = fetch_patient_by_contact(db, search_value)

        if patient:
            st.subheader("Patient Details")
            df = pd.DataFrame([patient], columns=['patient_id', 'Name', 'Age', 'Contact Number', 'Email', 'Address', 'Date Added'])
            st.dataframe(df)
            st.session_state.edit_patient = patient
        else:
            st.write("Patient not found")

    if 'edit_patient' in st.session_state:
        edit_patient(db)

def edit_patient(db):
    """Edit a patient's record."""
    patient = st.session_state.edit_patient
    st.subheader("Edit Patient Details")
    new_name = st.text_input("Enter new name", value=patient[1])
    new_age = st.number_input("Enter new age", value=patient[2])
    new_contact = st.text_input("Enter new contact number", value=patient[3])
    new_email = st.text_input("Enter new email", value=patient[4])
    new_address = st.text_input("Enter new address", value=patient[5])

    if st.button("Update :roller_coaster:"):
        update_patient_info(db, patient[0], new_name, new_age, new_contact, new_email, new_address)

def main():
    # Title and sidebar
    st.title("Patient Management System :hospital:")

    db = create_connection()

    menu = ["Home", "Add patient Record", "Show patient Records", "Search and Update Patient", "Delete Patients Record",
            "Add patients Appointments", "Show All Appointments", "Search and Update Patients Appointments"]
    options = st.sidebar.radio("Select an Option :dart:",menu)

    # Functions based on menu selection
    if options == "Home":
        st.write("Welcome to the Patient Management System!")
        st.write("Navigate from sidebar to access database")

    elif options == "Add patient Record":
        st.subheader("Enter patient details")
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=1, max_value=150)
        contact_number = st.text_input("Contact Number")
        email = st.text_input("Email Address")
        address = st.text_area("Address")

        if st.button("Add Record"):
            insert_patient_record(db, name, age, contact_number, email, address)
    elif options == "Show patient Records":
        st.subheader("Patient Records")
        patients = fetch_all_patients(db)
        df = pd.DataFrame(patients, columns=['Patient ID', 'Name', 'Age', 'Contact Number', 'Email', 'Address', 'Date Added'])
        st.dataframe(df)
    elif options == "Search and Update Patient":
        update_patient_record(db)
    elif options == "Delete Patients Record":
        delete_option = st.selectbox("Select delete option", ["Patient ID", "Name", "Contact Number"], key="delete_option")
        delete_value = st.text_input("Enter value to delete", key="delete_value")
        if st.button("Delete Patient Record"):
            delete_patient_record(db, delete_option, delete_value)
    elif options == "Add patients Appointments":
        patient_id = st.number_input("Patient ID", min_value=1)
        appointment_date = st.date_input("Appointment Date")
        appointment_time = st.time_input("Appointment Time")
        doctor_name = st.text_input("Doctor's Name")
        notes = st.text_area("Appointment Notes")

        if st.button("Add Appointment"):
            insert_appointment_record(db, patient_id, appointment_date, appointment_time, doctor_name, notes)
    elif options == "Show All Appointments":
        show_all_appointments(db)
    elif options == "Search and Update Patients Appointments":
        search_appointment(db)

if __name__ == "__main__":
    main()
