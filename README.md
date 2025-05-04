# Monte Carlo Simulator Module

Author: map3fz
Date: May 4, 2025

This module creates a Monte Carlo simulator with three interrelated classes that work together to simulate random events, gather data, and analyze outcomes.

## Overall Structure

The module consists of three main classes that follow this relationship:
Die → Game → Analyzer
This means:

Games use Die objects
Analyzers use Game objects

## Die Class
The Die class simulates a die with any number of sides (faces) and customizable weights.

```python
### Creating and Using Die Objects
import numpy as np
from montecarlo.montecarlo import Die

# Create a fair die with 6 sides
faces = np.array([1, 2, 3, 4, 5, 6])
my_die = Die(faces)

# Change the weight of one face
my_die.change_weight(6, 2.5)

# Roll the die 10 times
results = my_die.roll(10)
print(results)

# Show the current state of the die
die_state = my_die.show()
print(die_state)

```

### Key Methods
init(faces)

Takes a NumPy array of unique values (strings or numbers)
Creates an internal DataFrame storing faces as the index and weights (all initialized to 1.0)
Performs validation to ensure faces is a NumPy array with unique values

change_weight(face, weight)

Changes the weight of a specific face
Validates that the face exists and weight is numeric
Weights determine probability when rolling (higher weights = more likely)

roll(n=1)

Rolls the die n times (default is once)
Uses np.random.choice with weights converted to probabilities
Returns a Python list of results

show()

Returns a copy of the internal DataFrame
Shows current faces and their weights

## Game Class
The Game class uses one or more Die objects to simulate a game of chance.
```python
### Creating and Using Game objs
from montecarlo.montecarlo import Game

# Create multiple dice
die1 = Die(np.array([1, 2, 3, 4, 5, 6]))
die2 = Die(np.array([1, 2, 3, 4, 5, 6]))

# Create a game with both dice
my_game = Game([die1, die2])

# Play the game 1000 times
my_game.play(1000)

# Show the results in wide format
results_wide = my_game.show()
print(results_wide.head())

# Show the results in narrow format
results_narrow = my_game.show('narrow')
print(results_narrow.head())
```
### Key Methods
init(dice)

Takes a list of Die objects
Initializes _results to None (will store game outcomes later)

play(n_rolls)

Plays the game by rolling all dice n_rolls times
Creates a DataFrame where:

Rows represent each roll (indexed from 0 to n_rolls-1)
Columns represent each die (indexed from 0 to number of dice-1)
Values show which face was rolled



show(form='wide')

Shows results in either 'wide' or 'narrow' format
Wide format: original DataFrame (roll × die matrix)
Narrow format: MultiIndex DataFrame with roll and die as index, and outcome as column

## Analyzer Class
The Analyzer class performs statistical analysis on game results.
```python
### Creating and Using Analyzer objs
from montecarlo.montecarlo import Analyzer

# Create an analyzer for the game
my_analyzer = Analyzer(my_game)

# Count the number of jackpots
jackpot_count = my_analyzer.jackpot()
print(f"Number of jackpots: {jackpot_count}")

# Get face counts per roll
face_counts = my_analyzer.face_counts_per_roll()
print(face_counts.head())

# Get combination counts
combo_counts = my_analyzer.combo_count()
print(combo_counts.head())

# Get permutation counts
perm_counts = my_analyzer.permutation_count()
print(perm_counts.head())
```
### Key Methods
init(game)

Takes a Game object
Validates that the input is actually a Game object

jackpot()

Counts how many rolls resulted in all dice showing the same face
Uses the DataFrame's nunique() method to identify when all values in a row are identical

face_counts_per_roll()

Counts how many times each face appears in each roll
Returns a DataFrame with:

Rows as roll numbers
Columns as possible face values
Values as counts of each face in that roll



combo_count()

Counts unique combinations of faces (order doesn't matter)
Creates sorted tuples of each roll's values
Returns frequency counts of each combination

permutation_count()

Counts unique permutations of faces (order matters)
Similar to combo_count() but without sorting
Typically has more unique outcomes than combo_count()

## API Description
### Die Class
A die has N sides (faces) and W weights, and can be rolled to select a face.

### Methods:

- __init__(faces): Initialize a die with the given faces (NumPy array).
- change_weight(face, weight): Change the weight of a single side.
- roll(n=1): Roll the die one or more times and return results as a list.
- show(): Return a copy of the private die data frame showing the current state.

### Game Class
A game consists of rolling one or more similar dice (Die objects) one or more times.

### Methods:

- __init__(dice): Initialize a game with a list of dice.
- play(n_rolls): Play the game by rolling all dice n_rolls times.
- show(form='wide'): Return the results of the most recent play in wide or narrow format.

### Analyzer Class
An Analyzer takes the results of a game and computes various statistical properties.
### Methods:

- __init__(game): Initialize with a Game object.
- jackpot(): Count how many times the game resulted in a jackpot (all faces the same).
- face_counts_per_roll(): Compute how many times each face appears in each roll.
- combo_count(): Count distinct combinations of faces rolled (order-independent).
- permutation_count(): Count distinct permutations of faces rolled (order-dependent).

## How Classes Work Together

- You create one or more Die objects with specific faces
- You can adjust weights of specific faces to simulate biased dice
- You pass a list of Die objects to create a Game
- You play the Game to generate results
- You pass the Game to an Analyzer to compute statistics
- Analyzer methods reveal patterns in the random outcomes

This module effectively simulates random processes, collects data, and performs statistical analysis which is the goal of the Monte Carlo method.

# Monte Carlo Simulator Test File

The test suite for this Monte Carlo simulator package verifies the correctness of all implemented classes and methods through systematic unit testing. The test module contains three test classes that correspond to the three main classes in our package.

Each test class follows a methodical approach to validation, first establishing test fixtures in the setUp method, then testing individual components through specialized test methods.

## TestDie Class
The TestDie class confirms that our Die implementation functions correctly across all scenarios. It creates test dice with both numeric and string faces, then methodically tests:

- Initialization: Verifies the constructor creates dice with the correct number of faces and properly initialized weights of 1.0 for each face. It also checks error handling for invalid inputs like non-NumPy arrays and non-unique faces.
- Weight Modification: Ensures that changing weights for specific faces works correctly and validates that only legitimate faces can have their weights altered. The tests also confirm that only numeric weights are accepted.
- Rolling Functionality: Validates that the roll method returns results of the proper length and that all outcomes are valid faces from the die. Both single and multiple roll scenarios are tested.
- State Inspection: Verifies that the show method returns a properly structured DataFrame containing all die information.

## TestGame Class
The TestGame class validates that games properly manage collections of dice and their results. It creates various test games with combinations of fair and weighted dice, then tests:

- Game Creation: Confirms games are properly initialized with the correct number of dice.
- Play Execution: Verifies that the play method generates results with the expected dimensions and that all values are valid faces from the dice.
- Results Formatting: Tests both wide and narrow format options for displaying results, ensuring they maintain the correct structure and dimensions.
- Error Handling: Confirms the class properly handles invalid format specifications and unplayed games.

## TestAnalyzer Class
The TestAnalyzer class examines the statistical analysis capabilities. It creates controlled test games with predetermined outcomes for deterministic testing, then validates:

- Jackpot Detection: Confirms the analyzer correctly identifies rolls where all dice show the same face.
- Face Counting: Verifies that the analyzer accurately tallies each face's appearance in every roll.
- Combination Analysis: Tests that order-independent combinations are properly counted and categorized.
- Permutation Analysis: Ensures that order-dependent permutations are correctly identified and counted.
- Unplayed Game Handling: Validates that the analyzer safely handles analysis requests for games that haven't been played.

The test module also includes a main block that allows the tests to be executed directly from the command line, producing a comprehensive report of the package's functionality and reliability.
