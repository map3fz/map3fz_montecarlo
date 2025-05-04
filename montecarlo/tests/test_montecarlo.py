import unittest
import numpy as np
import pandas as pd
from montecarlo.montecarlo import Die, Game, Analyzer

class TestDie(unittest.TestCase):
    """
    Test cases for the Die class.
    """
    def setUp(self):
        """Set up test fixtures before each test."""
        #create a die with numeric faces
        self.numeric_faces = np.array([1, 2, 3, 4, 5, 6])
        self.numeric_die = Die(self.numeric_faces)

        # create a die with string faces
        self.string_faces = np.array(['A', 'B', 'C', 'D'])
        self.string_die = Die(self.string_faces)

    def test_init(self):
        """Test that intialization works correctly."""
        #Check that the die has the correct number of faces
        self.assertEqual(len(self.numeric_die.show()), 6)
        self.assertEqual(len(self.string_die.show()), 4)

        # check for weight initialization
        np.testing.assert_array_equal(self.numeric_die.show()['weights'].values, np.ones(6))
        np.testing.assert_array_equal(self.string_die.show()['weights'].values, np.ones(4))

        # Test Type error raises for not a NumPy array
        with self.assertRaises(TypeError):
            Die([1, 2, 3, 4])

        # Test ValueError raises for not distinct faces
        with self.assertRaises(ValueError):
            Die(np.array([1, 2, 3, 3, 4]))
    def test_change_weights(self):
        """Test that changing weights works correctly."""
        # Change a weight and make sure it is updated
        self.numeric_die.change_weight(1, 2.5)
        self.assertEqual(self.numeric_die.show().loc[1,'weights'], 2.5)

        # Test Index Error raises for invalid face
        with self.assertRaises(IndexError):
            self.numeric_die.change_weight(10, 2.0)

        # Test that TypeError is raised for invalid weight
        with self.assertRaises(TypeError):
            self.numeric_die.change_weight(2, "heavy")

    def test_roll(self):
        """Test that rolling returns a list of Length 1.."""
        result = self.numeric_die.roll()
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], self.numeric_faces)

        # Test rolling multiple times
        n_rolls = 10
        results = self.numeric_die.roll(n_rolls)
        self.assertEqual(len(results), n_rolls)
        # check that all results are valid faces
        for r in results:
            self.assertIn(r, self.numeric_faces)

    def test_show(self):
        """Test that show() returns the correct dataframe."""
        df = self.numeric_die.show()
        # check that it is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)
        # Check that it has the right index (faces should be index)
        np.testing.assert_array_equal(df.index.values, self.numeric_faces)
        # Check that it has a 'weights' column
        self.assertIn('weights', df.columns)

class TestGame(unittest.TestCase):
    """
    Test cases for the Game class.
    This could be expedited by adding a Global Constant for certain values like n_rolls and for faces.
    This is not done to ensure each function is working as intended within it's own scope
    """

    def setUp(self):
        """Set up test fixtures before each test."""

        # Create some ice
        faces = np.array([1, 2, 3, 4, 5, 6])
        self.die1 = Die(faces)
        self.die2 = Die(faces)

        # Create a weighted die
        self.die3 = Die(faces)
        self.die3.change_weight(6, 10)

        # Create a fair two dice game
        self.fair_game = Game([self.die1, self.die2])

        # Create a game with one fair die and one weighted die
        self.mixed_game = Game([self.die1, self.die3])

    def test_init(self):
        """Test that initialization works correctly."""
        # Check game has right number of dice
        self.assertEqual(len(self.fair_game._dice), 2)
        self.assertEqual(len(self.mixed_game._dice), 2)

    def test_play(self):
        """Test that play() works correctly."""
        # Play a game and check the results
        n_rolls = 5
        self.fair_game.play(n_rolls)
        results = self.fair_game.show()

        # check for n_rolls rows
        self.assertEqual(len(results), n_rolls)

        # Check for 2 columns (Should be one for each die if change params)
        self.assertEqual(len(results.columns), 2)

        # Check that all results have valid faces
        for col in results.columns:
            for val in results[col]:
                self.assertIn(val, [1, 2, 3, 4, 5, 6]) # should change to match faces from SetUp

    def test_show(self):
        """Test that show() returns the correct dataframe again."""
        # play a game again
        n_rolls = 5
        self.fair_game.play(n_rolls)

        # Test for wide format
        wide_results = self.fair_game.show()
        self.assertIsInstance(wide_results, pd.DataFrame)
        self.assertEqual(len(wide_results.columns), 2)
        self.assertEqual(len(wide_results), n_rolls)

        # Test narrow format
        narrow_results = self.fair_game.show('narrow')
        self.assertIsInstance(narrow_results, pd.DataFrame)
        self.assertEqual(len(narrow_results), n_rolls * 2) # 2 dice, n_rolls each

        #Test invalid format
        with self.assertRaises(ValueError):
            self.fair_game.show('invalid')

class TestAnalyzer(unittest.TestCase):
    """
    Test cases for the Analyzer class.
    """

    def setUp(self):
        """Set up test fixtures before each test."""
        # create dice
        faces = np.array([1, 2, 3, 4, 5, 6])
        self.die1 = Die(faces)
        self.die2 = Die(faces)

        # create a game with two dice
        self.game = Game([self.die1, self.die2])

        # play the game with controlled results
        self.game.play(5)

        # Create an Analyzer
        self.analyzer = Analyzer(self.game)

        # create a game with a known jackpot
        self.jackpot_game = Game([self.die1, self.die2])

        ### Override the _results to force test cases

        # create df with two identical columns to force jackpot
        self.jackpot_game._results = pd.DataFrame({
            0: [1, 2, 3, 4, 5],
            1: [1, 2, 3, 4, 5]
        })
        # create an analyzer for this game
        self.jackpot_analyzer = Analyzer(self.jackpot_game)

    def test_init(self):
        """Test that initialization works correctly."""
        # Game object initialization
        self.assertIsInstance(self.analyzer, Analyzer)

        # Test ValueError properly raised for non-game obj
        with self.assertRaises(ValueError):
            Analyzer("not a game")

    def test_jackpot(self):
        """Test that jackpot works correctly."""
        regular_jackpots = self.analyzer.jackpot()
        self.assertIsInstance(regular_jackpots, int)

        # count jackpots in forced game (should be 5)
        jackpot_count = self.jackpot_analyzer.jackpot()
        self.assertEqual(jackpot_count, 5)

    def test_face_counts_per_roll(self):
        """Test that face_counts_per_roll works correctly returning the corrct df."""
        # get face counts
        face_counts = self.analyzer.face_counts_per_roll()

        # check it is a df
        self.assertIsInstance(face_counts, pd.DataFrame)

        # check that it has the right index (roll numbers)
        self.assertEqual(len(face_counts), len(self.game.show()))

        # check sum of each row equals number of dice
        for _, row in face_counts.iterrows():
            self.assertEqual(row.sum(), len(self.game._dice))

    def test_combo_count(self):
        """Test that combo_count works correctly returning the corrct df."""
        # get combination counts
        combo_counts = self.analyzer.combo_count()

        # check it is a df
        self.assertIsInstance(combo_counts, pd.DataFrame)

        # check for count column
        self.assertIn('count', combo_counts.columns)

        # check that the sum of counts equals the number of rolls
        self.assertEqual(combo_counts['count'].sum(), len(self.game.show()))

    def test_permutations(self):
        """Test that permutations works correctly returning the corrct df."""
        # get permutation count
        perm_counts = self.analyzer.permutation_count()

        # check it is a df
        self.assertIsInstance(perm_counts, pd.DataFrame)

        # check for a 'count' column
        self.assertIn('count', perm_counts.columns)

        # check sum of counts = number of rolls
        self.assertEqual(perm_counts['count'].sum(), len(self.game.show()))

    def test_face_counts_without_play(self):
        """
        Test behavior when game hasn't been played.
        Ensuring no hallucinations for statistics
        """
        # create game without playing
        unplayed_game = Game([self.die1, self.die2])
        unplayed_analyzer = Analyzer(unplayed_game)

        # Test that face_counts_per_roll returns None
        self.assertIsNone(unplayed_analyzer.face_counts_per_roll())

    def test_combo_count_without_play(self):
        """Test behavior when game not in play"""

        """Test behavior when game hasn't been played."""
        # Create a game without playing
        unplayed_game = Game([self.die1, self.die2])
        unplayed_analyzer = Analyzer(unplayed_game)

        # Test that combo_count returns None
        self.assertIsNone(unplayed_analyzer.combo_count())

    def test_permutation_count_without_play(self):
        """Test behavior when game hasn't been played."""
        # Create a game without playing
        unplayed_game = Game([self.die1, self.die2])
        unplayed_analyzer = Analyzer(unplayed_game)

        # Test that permutation_count returns None
        self.assertIsNone(unplayed_analyzer.permutation_count())

if __name__ == '__main__':
    unittest.main()