import numpy as np
import pandas as pd


class Die:
    """
    A die has N sides or faces, and W weights which can be rolled to select a face.

    This class helps represent a die with any number of sides, any sybmbol, (string or nuber)
    with weighting applied on an individual basis.
    """

    def __init__(self, faces):
        """
        Initialize a die with the given faces.

        :param faces: np.ndarray
            A numpy array of faces with distinct values
            These values can be either a string or a number

        Possible error raises:
            TypeError:
                If face is not a numpy array
            ValueError:
                If faces values are not unique
        """
        # checking for numpy array in faces
        if not isinstance(faces, np.ndarray):
            raise TypeError("Faces must be a numpy array")

        # checking for unique values
        if len(faces) != len(np.unique(faces)):
            raise ValueError("Faces must all be unique values")

        # private data frame for faces and weights
        self._df = pd.DataFrame({
            'weights': np.ones(len(faces))
        }, index=faces)

    def change_weight(self, face, weight):
        """

        :param face: any
            The face can be changed. It needs to be in the die array.
        :param weight: int or float
            the new weight. Must be numeric or castable as a numeric

        Possible errors:
        IndexError:
            When face is not in the die array.
        TypeError:
            When weight is not numeric nor castable as numeric
        """
        # checking for valid face
        if face not in self._df.index:
            raise IndexError(f"Face {face} is not a valid face")

        # Check if weight is valid
        try:
            weight = float(weight)  # step converts anything castable to a numeric
        except (ValueError, TypeError):
            raise TypeError("Weight must be a numeric value or castable as one")

        # update weight
        self._df.loc[face, 'weights'] = weight

    def roll(self, n=1):
        """

        :param n: int, optional
            The number of times to roll the die. Will default to 1.
        :return:
            A list of die roll results.
        """
        # Roll die n times
        # randomly sample with replacement from faces
        # probability will be proportional to the weight
        faces = self._df.index
        weights = self._df['weights'].values

        # normalization of weight for probablity
        probabilities = weights / sum(weights)

        # sample with replacement via probabilities
        results = np.random.choice(faces, size=n, p=probabilities, replace=True)

        # Return a python list
        return results.tolist()

    def show(self):
        """
        shows current state of the die

        Returns:
            pd.DataFrame
                A copy of the private data frame.
        """
        return self._df.copy()


class Game:
    """
    Consists of rolling one or more similar dice (from die) one or more times

    Each game is initialized with a list of dice and has methods to play and display the results
    """

    def __init__(self, dice):
        """
        initialize a game with a list of dice
        :param dice: list
            list of pre-instanced die objs
        """
        self._dice = dice
        self._results = None # Allows to hold the all the play results

    def play(self, n_rolls):
        """
        Play the game n_rolls times.
        :param n_rolls: int
            number of times to play
        """

        # Create a results dataframe with roll number as index and one column for each die
        results = {}

        # For each roll, get the outcome of each die
        for roll in range (n_rolls):
            roll_results = {}

            # Roll each die once and record the result
            for i in range (len(self._dice)):
                die = self._dice[i]
                # Rolls the die once and gets the first/only result
                roll_results[i] = die.roll(1)[0]

            # adds the roll's result to the overall results
            results[roll] = roll_results

        # convert results to a pandas data frame
        self._results = pd.DataFrame.from_dict(results, orient='index')

    def show (self, form = 'wide'):
        """
        Shows the results of the most recent play.

        :param form: str, optional
            Format the returned DataFrame. Will be wide or narrow, default to wide.

        :return:
        pd.DataFrame
            A copy of private play DataFrame containing the results of the most recent play.

        :raises:
        ValueError:
            If form is not 'wide' or 'narrow'.
        """
        if self._results is None:
            return None
        if form == 'wide':
            return self._results.copy()
        elif form == 'narrow':
            # convert to narrow form using a MultiIndex
            narrow = self._results.stack().reset_index()
            narrow.columns = ['roll', 'die', 'coutcome']
            return narrow.set_index(['roll', 'die'])
        else:
            raise ValueError("Form must be 'wide' or 'narrow'.")

class Analyzer:
    """
    An Analyzer class -- takes results of a single game and computes several statistics to describe the outcome.
    """
    def __init__(self, game):
        """
        Initialize an Analyzer with a game object..
        :param game:
        Game object that has already been played to be analyzed.

        :raise:
        ValueError:
        If arguement called is not a Game object.
        """
        if not isinstance (game, Game):
            raise ValueError ("Analyzer requires a Game object.")
        self._game = game

    def jackpot(self):
        """
        Identify how many times ha the game resulted in a jackpot.
        A jackpot = result where all faces are the same.

        :return: int
        The number of times ha the game resulted in a jackpot.
        """
        # get the results in wide form
        results = self._game.show()
        if results is None:
            return 0

        # Count jackpots (identifies where all vals in a row are the same)
        jackpot_count = 0
        for _, row in results.iterrows():
            # check if all dice show same face
            if row.nunique() == 1:
                jackpot_count += 1
        return jackpot_count

    def face_counts_per_roll(self):
        """
        Compute how many times a given face is rolled in each play
        :return: pd.DataFrame
            A dataframe containing roll number as index, face vals as columns,
            and count values in the cells.
        """
        # Get the results
        results = self._game.show()
        if results is None:
            return None

        # Get all possible faces across all dice
        all_faces = set()
        for die in self._game._dice:
            all_faces.update(die.show().index)

        # Create a DataFrame to store counts
        face_counts = pd.DataFrame(index = results.index)

        # count each face in each roll
        for face in all_faces:
            face_counts[face] = results.apply(
                lambda row: (row == face).sum(), axis=1
                )
        return face_counts

    def combo_count(self):
        """
        Computes how many distinct combinations of faces rolled, as well as their count.
        These are order-dependent and could contain repetitions, should be addressed by sorted()
        :return: pd.DataFrame
            A df with distinct combinations as MultiIndex and counts as column.
        """
        # Pull results
        results = self._game.show()
        if results is None:
            return None

        # for each roll, make a sorted tuple of the combination
        combos = results.apply(lambda row: tuple(sorted(row)), axis = 1) # axis = 1 param applies to rows

        # Count occurrences of each combo
        combo_counts = combos.value_counts().reset_index()
        combo_counts.columns = ['combination', 'count']

        # Convert to a df with MultiIndex
        combo_df = combo_counts.set_index('combination')

        return combo_df

    def permutation_count(self):
        """
        compute distinct permutation counts. Should have a higher value that combos
        order dependent, could have repeats
        :return: pd.DataFrame
            A df with distinct permutations as MultiIndex and counts as columns.
        """
        results = self._game.show()
        if results is None:
            return None

        # Create a tuple of permutations for each roll
        perms = results.apply(lambda row: tuple(row), axis = 1)

        # count occurrences of each permutation
        perm_counts = perms.value_counts().reset_index()
        perm_counts.columns = ['permutation', 'count']

        # Convert to a df with MultiIndex
        perm_df = perm_counts.set_index('permutation')

        return perm_df