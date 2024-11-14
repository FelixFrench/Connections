from itertools import chain
from nltk.corpus import wordnet, words
import random
from tabulate import tabulate
import pickle

class Category:
    """A category is a connection with a set of related clues"""

    def __init__(self, connection: str, clues: set[str]):
        self.Connection = connection
        self.Clues = clues

def GetSynonymCategory(NumSynonyms : int) -> Category:
    """
    Get single category where the connection is a word for which all the clues are synonyms.
        Parameters:
            NumSynonyms (int):    The number of synonyms to have in the category's clues.
        Returns:
            A new category with a connection and a set of synonyms as the clues
    """

    # Run until a word with enough synonyms is found
    NewCategory = None
    while NewCategory is None:

        # Get a random word to use as the connection
        Connection = random.sample(words.words(), 1)[0].lower()

        # Get a list of synonym sets for the connection. Each item in the list relates to a different meaning of the connection
        SynSets = wordnet.synsets(Connection)

        # Get the lemma names (actual words) for each synonym set, all in lower case.
        LemmaNames = [[x.lower() for x in synset.lemma_names()] for synset in SynSets]

        # Join all the synonym lists into a chain, then convert to a set.
        Synonyms = set(chain.from_iterable(LemmaNames))

        # Don't allow the connection word to be counted as a synonym
        if Connection in Synonyms:
            Synonyms.remove(Connection)

        # If this word has at least NumSynonyms synonyms
        if(len(Synonyms) >= NumSynonyms):

            # Choose just NumSynonyms synonyms
            ChosenSyns = set(random.sample(sorted(Synonyms), NumSynonyms))

            # Add this category to the list of categories to return
            NewCategory = Category(Connection, ChosenSyns)
        else:
            print(".", end="")

    return NewCategory

def GetCategories(numCategories : int, cluesPerCategory : int) -> list[Category]:
    """Get a list of categories with different connections.
    Clues may be duplicated between categories!
        Parameters:
            numCategories (int):    The number of categories to return.
            cluesPerCategory (int): The number of clues each category should have.
    """

    print("Loading categories", end="")

    # Populate the list of categories to return
    Categories = []
    while len(Categories) < numCategories:

        NewCategory = GetSynonymCategory(cluesPerCategory)

        # If this connection has already been used, continue.
        if NewCategory.Connection in [cat.Connection for cat in Categories]:
            print(".", end="")
            continue

        print(":", end="")
        Categories += [NewCategory]

    return Categories


def PlayRound(Categories : list[Category], lives : int):
    
    NumCategories = len(Categories)
    WordsPerCategory = len(Categories[0].Clues)

    GridWords = list()
    for cat in Categories:
        GridWords += sorted(cat.Clues)

    # Shuffle the order of the 16 words
    random.shuffle(GridWords)

    print()

    UnfoundCategories = Categories.copy()

    # List of categories which have been found
    FoundCategories = []

    RemainingLives = lives
    while RemainingLives > 0 and len(UnfoundCategories) > 1:

        # Print the 16 words as a GROUPSxWORDS_PER_GROUP grid, with empty rows removed
        Grid = [GridWords[WordsPerCategory*i:WordsPerCategory*i+WordsPerCategory] for i in range(NumCategories)]
        Grid = [Row for Row in Grid if "".join(Row) != ""]
        print(tabulate(Grid))

        # Get the player's guess as a set
        guess = set(input(F"Enter a {WordsPerCategory} word set, seperated by \", \"\n").split(", "))

        # Look for the index of the guess in UnfoundCategories
        FoundIndex = -1
        for i, cat in enumerate(UnfoundCategories):
            if(guess == cat.Clues):
                FoundIndex = i
                break

        # If the guess was correct
        if FoundIndex != -1:
            print(f"Correct!\n")

            # Remove this word and associated syns from the unfound word, and add them to the found words
            FoundCategories += [UnfoundCategories[i]]
            del UnfoundCategories[i]

            # Remove the group that was just guessed from the grid, then display it again
            for i in range(len(GridWords)):
                if GridWords[i] in guess:
                    GridWords[i] = ""

        # If the guess was wrong
        else:
            RemainingLives -= 1
            print(f"Wrong! {RemainingLives} lives remaining\n")

        if(len(UnfoundCategories) == 1):
            print("All categories found!\n")
            FoundCategories += [UnfoundCategories[0]]
            del UnfoundCategories[0]

    ConnectionsFound = 0
    for Cat in FoundCategories + UnfoundCategories:
        if input("What connects the category \"" + ", ".join(Cat.Clues) + "\"? ").lower() == Cat.Connection:
            print("Correct!")
            ConnectionsFound += 1
        else:
            print(f"Wrong! The connection was {Cat.Connection}\n")

    if len(FoundCategories) != 0:
        print("You found:")
        # Print each connection with its synonym words
        print(tabulate([[Cat.Connection, ", ".join(Cat.Clues)] for Cat in FoundCategories]))

    if len(UnfoundCategories) != 0:
        print("You missed:")
        # Print each connection with its synonym words
        print(tabulate([[Cat.Connection, ", ".join(Cat.Clues)] for Cat in UnfoundCategories]))

    return len(FoundCategories) + ConnectionsFound

ROUNDS = 5
LIVES = 3

print("Lets's play connections!")
try:
    with open("leaderboard.pkl", 'rb') as LeaderboardFile:
        Leaderboard = pickle.load(LeaderboardFile)
except:
    Leaderboard = None

if Leaderboard is not None:
    print("Leaderboard: ")
    print(tabulate(sorted([[x, Leaderboard[x]] for x in Leaderboard], key=lambda y: y[1], reverse=True)))
else:
    Leaderboard = dict()
username = input("What's your name? ")

gridsize = int(input("What grid size do you want to play? "))


score = 0
for round in range(ROUNDS):

    print(f"ROUND {round + 1} OF {ROUNDS}")

    Categories = GetCategories(gridsize, gridsize)

    score += PlayRound(Categories, LIVES)

    print()

    if(round < ROUNDS - 1):
        print(f"End of round {round + 1}, current score: {score}")
    print()

print(f"Final score: {score}")

Leaderboard[username] = score

print(tabulate(sorted([[x, Leaderboard[x]] for x in Leaderboard], key=lambda y: y[1], reverse=True)))

with open("leaderboard.pkl", 'wb') as LeaderboardFile:
    pickle.dump(Leaderboard, LeaderboardFile)