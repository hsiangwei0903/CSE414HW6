CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

--note that the Schedule.py can filter out invalid creation of appointment so we can skip foreign key constraint here

CREATE TABLE Appointments (
    appointmentID int,
    Time date,
    Caregiver varchar(255),
    Patient varchar(255),
    Vaccine varchar(255)
    PRIMARY KEY (appointmentID)
);
