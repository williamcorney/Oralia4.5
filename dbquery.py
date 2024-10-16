import pickle

# Load the existing theory data from the pickle file
with open('theory.pkl', 'rb') as file:
    theory = pickle.load(file)


print (theory["Shells"]["Dominant"])