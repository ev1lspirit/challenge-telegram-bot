DROP TABLE IF EXISTS ChallengeUpdate;
DROP TABLE IF EXISTS ChallengeParticipant;
DROP TABLE IF EXISTS ActiveChallenge;
DROP TABLE IF EXISTS BannedParticipant;
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
    active_challenge_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    owner_id BIGINT REFERENCES Participant(user_id),
    challenge_id INTEGER references UserCreatedChallenge(id),
    creation_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    join_code VARCHAR(40) NOT NULL
);

CREATE TABLE ChallengeParticipant (
    challenge_participant_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES Participant(user_id),
    challenge_id BIGINT REFERENCES ActiveChallenge(active_challenge_id),
    is_kicked BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE BannedParticipant (
    ban_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    initiator_id BIGINT REFERENCES Participant(user_id),
    receiver_id BIGINT REFERENCES Participant(user_id),
    CONSTRAINT not_the_same_user CHECK(initiator_id <> receiver_id)
);

CREATE TABLE ChallengeUpdate (
    update_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    participant_id BIGINT REFERENCES ChallengeParticipant(challenge_participant_id),
    update_date TIMESTAMP NOT NULL,
    update_text TEXT NOT NULL UNIQUE
);

INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '����������� ������ � �������', '�������� �������� � ���� ����������� ��������� ������ � ������� ������ ���� � ������� �� ����� 500 �.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '�������� ���', '�������� �������� � ���� ����������� ��� � ������������� ���������� �����', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '����������', '�������� �������� � ���� ����������� �� ����� 2 ������ ������ ���� � ����.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '10 000 �����', '�������� �������� � ���� ���������� ����������� ��������� � 10 000 �����.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '���������', '�������� �������� � ���� ���������� �������� ��������� �� ���������� �� ����� 15 �����.', current_timestamp);
INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES (0, '��� ������', '�������� �������� � ���� ���������� �� ������� ���������, ���������� ����������� �����.', current_timestamp);
