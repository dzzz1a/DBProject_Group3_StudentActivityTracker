


CREATE TABLE advisor (
  advisorID INT(11) NOT NULL AUTO_INCREMENT,
  advisorName VARCHAR(20),
  advisorEmail VARCHAR(25),
  advisorRole VARCHAR(15),
  advisorPassword VARCHAR(15),
  availableSchedule VARCHAR(100),
  PRIMARY KEY (advisorID)
);

-- --------------------------------------------------------


CREATE TABLE students (
  studentID INT(11) NOT NULL AUTO_INCREMENT,
  studentFirstName VARCHAR(15),
  studentLastName VARCHAR(15),
  studentYear INT(11),
  studentEmail VARCHAR(25),
  studentPassword VARCHAR(15),
  studentAddress VARCHAR(255),
  phoneNumber INT(11),
  PRIMARY KEY (studentID)
);
-- --------------------------------------------------------

CREATE TABLE joins (
  joinsID INT(11) NOT NULL AUTO_INCREMENT,
  studentID INT(11),
  activityID INT(11),
  PRIMARY KEY (joinsID),
  FOREIGN KEY (studentID) REFERENCES students(studentID),
  FOREIGN KEY (activityID) REFERENCES activity(activityID)
);

-- --------------------------------------------------------

CREATE TABLE activity (
  activityID INT(11) NOT NULL AUTO_INCREMENT,
  activityName VARCHAR(30),
  activityCategory VARCHAR(20),
  activityLocation VARCHAR(50),
  activityDetails TEXT,
  activityStartDate DATE,
  activityEndDate DATE,
  activityFrequency VARCHAR(20),
  advisorID INT(11),
  PRIMARY KEY (activityID),
  FOREIGN KEY (advisorID) REFERENCES advisor(advisorID)
);

-- --------------------------------------------------------


CREATE TABLE participation (
  participationID INT(11) NOT NULL AUTO_INCREMENT,
  dateApplied DATE,
  applicationStatus VARCHAR(20),
  approvalDate DATE,
  advisorFeedback TEXT,
  achievements TEXT,
  studentID INT(11),
  activityID INT(11),
  advisorID INT(11),
  PRIMARY KEY (participationID),
  FOREIGN KEY (studentID) REFERENCES students(studentID),
  FOREIGN KEY (activityID) REFERENCES activity(activityID),
  FOREIGN KEY (advisorID) REFERENCES advisor(advisorID)
);
