import unittest
from matcher import SecretSantaMatcher
from mail_utils import EmailHandler
from localization import Translations

class TestSecretSantaMatcher(unittest.TestCase):
    def setUp(self):
        self.participants = ['Alice', 'Bob', 'Charlie', 'David']
        self.basic_config = {
            'rounds': [{
                'participants': self.participants,
                'exclusions': {},
                'budget': '50'
            }]
        }
    
    def test_no_self_assignment(self):
        """Test that no one is assigned to give a gift to themselves"""
        matcher = SecretSantaMatcher()
        pairings = matcher.generate_pairings(self.basic_config['rounds'])
        
        for round_data in pairings:
            for giver, receiver in round_data['pairing'].items():
                self.assertNotEqual(giver, receiver, 
                    f"Person {giver} was assigned to give to themselves")
    
    def test_respect_exclusions(self):
        """Test that exclusions are respected in assignments"""
        config = {
            'rounds': [{
                'participants': self.participants,
                'exclusions': {'Alice': ['Bob']},
                'budget': '50'
            }]
        }
        
        matcher = SecretSantaMatcher()
        pairings = matcher.generate_pairings(config['rounds'])
        
        # Check Alice isn't giving to Bob
        self.assertNotEqual(
            pairings[0]['pairing'].get('Alice'), 
            'Bob',
            "Alice was assigned to Bob despite exclusion"
        )
    
    def test_prevent_reciprocal_pairs(self):
        """Test that reciprocal pairs are prevented when enabled"""
        matcher = SecretSantaMatcher(prevent_reciprocal_pairs=True)
        pairings = matcher.generate_pairings(self.basic_config['rounds'])
        
        # Convert pairings to set of tuples for easier checking
        pairs = {(giver, receiver) 
                for round_data in pairings 
                for giver, receiver in round_data['pairing'].items()}
        
        # Check for reciprocal pairs
        for giver, receiver in pairs:
            self.assertFalse(
                (receiver, giver) in pairs,
                f"Reciprocal pair found: {giver}->{receiver} and {receiver}->{giver}"
            )

class TestEmailGeneration(unittest.TestCase):
    def setUp(self):
        self.config = {
            'email': {
                'subject': 'Secret Santa 2025',
                'sender': 'Secret Santa Bot',
                'language': 'en'
            },
            'year': 2025
        }
        self.email_handler = EmailHandler(self.config)
    
    def test_single_assignment_text(self):
        """Test singular form is used for one assignment"""
        assignments = ['<strong>Bob</strong>']
        email = self.email_handler.generate_email('Alice', assignments, 'test123')
        self.assertIn('is your Secret Santa assignment', email,
            "Singular form not used for single assignment")
    
    def test_multiple_assignments_text(self):
        """Test plural form is used for multiple assignments"""
        assignments = ['<strong>Bob</strong>', '<strong>Charlie</strong>']
        email = self.email_handler.generate_email('Alice', assignments, 'test123')
        self.assertIn('are your Secret Santa assignments', email,
            "Plural form not used for multiple assignments")

class TestLocalization(unittest.TestCase):
    def test_english_translations(self):
        """Test English translations are complete and accessible"""
        trans = Translations('en')
        self.assertEqual(
            trans.get_assignment_text(True),
            'is your Secret Santa assignment',
            "Incorrect English singular form"
        )
        self.assertEqual(
            trans.get_assignment_text(False),
            'are your Secret Santa assignments',
            "Incorrect English plural form"
        )
    
    def test_german_translations(self):
        """Test German translations are complete and accessible"""
        trans = Translations('de')
        self.assertEqual(
            trans.get_assignment_text(True),
            'ist dein Wichtelauftrag',
            "Incorrect German singular form"
        )
        self.assertEqual(
            trans.get_assignment_text(False),
            'sind deine Wichtelaufträge',
            "Incorrect German plural form"
        )

class TestDrawRandomness(unittest.TestCase):
    def setUp(self):
        self.participants = ['Alice', 'Bob', 'Charlie', 'David']
        self.config = {
            'rounds': [{
                'participants': self.participants,
                'exclusions': {},
                'budget': '50'
            }]
        }

    def test_draw_is_random(self):
        matcher = SecretSantaMatcher()
        draws = []
        # Run the draw multiple times
        for _ in range(5):
            matcher = SecretSantaMatcher()  # Reset matcher state
            pairings = matcher.generate_pairings(self.config['rounds'])
            # Store the sorted tuple of (giver, receiver) pairs for comparison
            draw_result = tuple(sorted(pairings[0]['pairing'].items()))
            draws.append(draw_result)
        # There should be at least 2 different results in 5 runs
        unique_draws = set(draws)
        self.assertTrue(
            len(unique_draws) > 1,
            "Draw results are not random; all draws produced the same result."
        )

if __name__ == '__main__':
    unittest.main()