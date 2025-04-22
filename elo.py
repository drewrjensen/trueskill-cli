def update_elo(player_rating, opponent_rating, result, k=32):
  expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
  new_rating = player_rating + k * (result - expected_score)
  return new_rating