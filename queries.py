check_if_registered_query = "SELECT 1 FROM Participant WHERE user_id={user_id};"
select_challenges = "SELECT id, title from UserCreatedChallenge WHERE owner_id={user_id} OR owner_id=0 ORDER BY id DESC LIMIT 5 OFFSET {offset};"
select_total_challenges =  "SELECT COUNT(id) FROM UserCreatedChallenge WHERE owner_id={owner_id} OR owner_id=0;"
insert_active_transaction = """BEGIN;
WITH make_active AS (
    INSERT INTO ActiveChallenge (owner_id, challenge_id, creation_date, end_date, is_finished) VALUES ({user_id}, {challenge_id}, '{creation_date}', '{end_date}', 'f')
     RETURNING active_challenge_id AS challenge_id, owner_id
)
INSERT INTO ChallengeParticipant (user_id, challenge_id, is_kicked) SELECT owner_id, challenge_id, 'f' FROM make_active;
COMMIT; 
"""
check_if_challenge_taken = "SELECT 1 FROM ActiveChallenge WHERE challenge_id={challenge_id} AND owner_id={user_id};"
insert_new_user_challenge = "INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES ({owner_id}, '{title}', '{description}', '{creation_date}') RETURNING id;"
select_challenges_query = \
"""SELECT title, description, ActiveChallenge.owner_id as owner_id, end_date
    FROM (ActiveChallenge JOIN UserCreatedChallenge ON ActiveChallenge.challenge_id=UserCreatedChallenge.id)
        JOIN ChallengeParticipant ON ActiveChallenge.active_challenge_id=ChallengeParticipant.challenge_id
    WHERE ChallengeParticipant.user_id={user_id} LIMIT 5 OFFSET {offset};"""
select_username_by_id = "SELECT username FROM Participant WHERE user_id={user_id};"
total_user_challenges = "SELECT COUNT(challenge_id) FROM ChallengeParticipant WHERE user_id={user_id};"