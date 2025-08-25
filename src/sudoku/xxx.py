
possible = [1, 3, 5, 7]
suggestion = [1, 3, 5]

xxx = all(v in possible for v in suggestion)
print(xxx)
