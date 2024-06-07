DROP TABLE IF EXISTS ChallengeParticipant;
DROP TABLE IF EXISTS ActiveChallenge;
DROP TABLE IF EXISTS Participant;
DROP TABLE IF EXISTS UserCreatedChallenge;


CREATE TABLE Participant (
    user_id BIGINT NOT NULL PRIMARY KEY,
    username VARCHAR(45) NOT NULL,
    joined DATE NOT NULL,
    reputation INTEGER CHECK (reputation >= 0) NOT NULL,
    completed_challenge INTEGER CHECK(completed_challenge >= 0) NOT NULL
);

CREATE TABLE UserCreatedChallenge(
    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    creation_date TIMESTAMP NOT NULL,
    max_participants INTEGER DEFAULT 7
);

CREATE TABLE ActiveChallenge (
    active_challenge_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    owner_id BIGINT REFERENCES Participant(user_id),
    challenge_id INTEGER references UserCreatedChallenge(id),
    creation_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_finished BOOLEAN NOT NULL
);

CREATE TABLE ChallengeParticipant (
    participant_id BIGINT REFERENCES Participant(user_id),
    challenge_id INTEGER REFERENCES Challenge(challenge_id),
    is_kicked BOOLEAN NOT NULL,
    PRIMARY KEY (participant_id, challenge_id)
);

INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '����������� ������ � �������', '�������� �������� � ���� ����������� ��������� ������ � ������� ������ ���� � ������� �� ����� 500 �.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '�������� ���', '�������� �������� � ���� ����������� ��� � ������������� ���������� �����', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '����������', '�������� �������� � ���� ����������� �� ����� 2 ������ ������ ���� � ����.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '10 000 �����', '�������� �������� � ���� ���������� ����������� ��������� � 10 000 �����.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '���������', '�������� �������� � ���� ���������� �������� ��������� �� ���������� �� ����� 15 �����.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '��� ������', '�������� �������� � ���� ���������� �� ������� ���������, ���������� ����������� �����.', current_timestamp);
