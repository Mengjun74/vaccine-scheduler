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

-- patients table with username, password
CREATE TABLE Patients(
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY(Username)
);
-- one caregiver deal with many appointments and one patient can have many appointments in different time 
CREATE TABLE Appointments(
    ID int,
    CUsername varchar(255),
    Time date,
    vname varchar(255) REFERENCES Vaccines(Name),
    PUsername varchar(255) REFERENCES Patients(Username),
    FOREIGN KEY (Time, CUsername) REFERENCES Availabilities(Time, Username),
	PRIMARY KEY (ID)
);



