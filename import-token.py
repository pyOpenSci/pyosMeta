# TODO: This will become automated in a CI workflow
import pickle

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)

with open("../token.pickle", "wb") as f:
    pickle.dump(API_TOKEN, f)
