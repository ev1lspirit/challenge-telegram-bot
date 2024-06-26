check_if_registered_query = "SELECT 1 FROM Participant WHERE user_id={user_id};"
select_challenges = "SELECT id, title from UserCreatedChallenge WHERE owner_id={user_id} OR owner_id=0 ORDER BY id DESC LIMIT 5 OFFSET {offset};"
select_total_challenges =  "SELECT COUNT(id) FROM UserCreatedChallenge WHERE owner_id={owner_id} OR owner_id=0;"
insert_active_transaction = """BEGIN;
WITH make_active AS (
    INSERT INTO ActiveChallenge (owner_id, challenge_id, creation_date, end_date, join_code) VALUES ({user_id}, {challenge_id}, '{creation_date}', '{end_date}', '{join_code}')
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
select_username_by_id = "SELECT user_id, username FROM Participant WHERE user_id IN ({id_list});"
total_user_challenges = "SELECT COUNT(challenge_id) FROM ChallengeParticipant WHERE user_id={user_id};"
select_full_challenge_info = """SELECT active_challenge_id, ActiveChallenge.owner_id, username, challenge_id, end_date, title 
        FROM (ActiveChallenge JOIN UserCreatedChallenge ON ActiveChallenge.challenge_id=UserCreatedChallenge.id)
            JOIN Participant ON ActiveChallenge.owner_id=Participant.user_id"""
select_challenge_by_code = """{query_body} WHERE ActiveChallenge.join_code='{{join_code}}'""".format(query_body=select_full_challenge_info)
select_expired_challenges = \
    """{query_body} WHERE end_date < timestamp '{{timestamp}}';""".format(query_body=select_full_challenge_info)
select_expired_participants = \
    """SELECT user_id, challenge_id FROM ChallengeParticipant
        WHERE challenge_id IN ({challenge_list});"""
delete_expired_challenges_transaction = \
    """BEGIN;
WITH delete_active AS (
    DELETE FROM ActiveChallenge WHERE active_challenge_id IN ({challenge_id_list}) RETURNING active_challenge_id
)
DELETE FROM ChallengeParticipant WHERE challenge_id IN (SELECT active_challenge_id FROM delete_active);
COMMIT;"""
is_user_joined = "SELECT 1 FROM ChallengeParticipant WHERE user_id={user_id} AND challenge_id={challenge_id};"
prevent_user_from_joining = "INSERT INTO BannedParticipant (initiator_id, receiver_id) VALUES ({initiator_id}, {receiver_id});"
check_if_user_can_join = "SELECT 1 FROM BannedParticipant WHERE initiator_id={initiator_id} AND receiver_id={receiver_id};"