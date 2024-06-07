select_challenges = "SELECT id, title from UserCreatedChallenge WHERE owner_id={user_id} OR owner_id=0 ORDER BY id DESC LIMIT 5 OFFSET {offset};"
select_total_challenges =  "SELECT COUNT(id) FROM UserCreatedChallenge WHERE owner_id={owner_id} OR owner_id=0;"
insert_active_challenge = ("INSERT INTO ActiveChallenge (owner_id, challenge_id, creation_date, end_date, is_finished)"
                           " VALUES ({user_id}, {challenge_id}, '{creation_date}', '{end_date}', 'f');")
check_if_challenge_taken = "SELECT 1 FROM ActiveChallenge WHERE challenge_id={challenge_id} AND owner_id={user_id};"
insert_new_user_challenge = "INSERT INTO UserCreatedChallenge (owner_id, title, description, creation_date) VALUES ({owner_id}, '{title}', '{description}', '{creation_date}') RETURNING id;"