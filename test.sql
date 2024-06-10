USE school;
CREATE TABLE Patient (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    address VARCHAR(255),
    phone_number VARCHAR(20)
);

CREATE TABLE Doctor (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100)
);

CREATE TABLE MedicalRecord (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    date_of_visit DATE,
    diagnosis TEXT,
    prescription TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);


CREATE TABLE Disease (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);


CREATE TABLE Medicine (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    manufacturer VARCHAR(100),
    dosage VARCHAR(50),
    usage_instructions TEXT
);


CREATE TABLE MedicalRecord_Disease (
    record_id INT,
    disease_id INT,
    PRIMARY KEY (record_id, disease_id),
    FOREIGN KEY (record_id) REFERENCES MedicalRecord(record_id),
    FOREIGN KEY (disease_id) REFERENCES Disease(disease_id)
);


CREATE TABLE MedicalRecord_Medicine (
    record_id INT,
    medicine_id INT,
    PRIMARY KEY (record_id, medicine_id),
    FOREIGN KEY (record_id) REFERENCES MedicalRecord(record_id),
    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id)
);
