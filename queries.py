select_challenges = "SELECT challenge_id, challenge_title from Challenge LIMIT 7;"
insert_active_challenge = ("INSERT INTO ActiveChallenge (owner_id, challenge_id, creation_date, end_date, is_finished)"
                           " VALUES ({user_id}, {challenge_id}, '{creation_date}', '{end_date}', 'f');")
check_if_challenge_taken = "SELECT 1 FROM ActiveChallenge WHERE challenge_id={challenge_id} AND owner_id={user_id};"