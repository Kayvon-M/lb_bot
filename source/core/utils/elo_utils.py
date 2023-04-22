import json

# Load config
with open('source/config/config.json') as f:
    config = json.load(f)

kFactor = config['kFactor']


def getExpectedScore(challenger, challenged):
    return 1 / (1 + 10 ** ((challenged - challenger) / 400))


def getNewRating(challenger, challenged, score):
    return round(challenger + kFactor * (score - getExpectedScore(challenger, challenged)))


def getNewRatings(challenger, challenged, result):
    if result == "win":
        return getNewRating(challenger, challenged, 1), getNewRating(challenged, challenger, 0)
    elif result == "loss":
        return getNewRating(challenger, challenged, 0), getNewRating(challenged, challenger, 1)
    elif result == "draw":
        return getNewRating(challenger, challenged, 0.5), getNewRating(challenged, challenger, 0.5)
    else:
        raise Exception("Invalid result: " + result)
