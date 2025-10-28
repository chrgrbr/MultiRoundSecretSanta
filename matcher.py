from collections import defaultdict
from itertools import permutations
import random

class SecretSantaMatcher:
    def __init__(self, prevent_reciprocal_pairs=False):
        """
        Initialize the Secret Santa matcher.
        
        Args:
            prevent_reciprocal_pairs (bool): If True, prevents reciprocal gift-giving pairs.
                For example, if Alex gives to Beth, Beth cannot give to Alex.
                This can help make the gift exchange more interesting by ensuring
                wider interaction between participants across rounds.
        """
        self.prevent_reciprocal_pairs = prevent_reciprocal_pairs
        self.history = defaultdict(set)  # Tracks who has given to whom across rounds
        self.pair_history = set()  # Tracks all giver-receiver pairs for reciprocal prevention
        
    def validate_round(self, participants, exclusions=None):
        """
        Validates and returns all valid pairings for a round.
        
        A valid pairing must satisfy these rules:
        - No one gives a gift to themselves
        - Respects provided exclusions (e.g., family members)
        - No one gives to the same person twice across rounds
        - If prevent_reciprocal_pairs is True, prevents mutual gift-giving
        """
        exclusion_map = defaultdict(set)
        
        if exclusions:
            for giver, excluded in exclusions.items():
                for receiver in excluded:
                    exclusion_map[giver].add(receiver)
                    exclusion_map[receiver].add(giver)
        
        valid = []
        for perm in permutations(participants):
            valid_pairing = True
            pairing = list(zip(participants, perm))
            pairing_set = set(pairing)

            for giver, receiver in pairing:
                # Check all pairing rules
                # Also check for reciprocal pairs inside the same candidate pairing
                reciprocal_in_current = (receiver, giver) in pairing_set
                reciprocal_in_history = (receiver, giver) in self.pair_history

                is_invalid = (
                    giver == receiver or                     # Can't give to self
                    receiver in exclusion_map[giver] or      # Respect exclusions
                    receiver in self.history[giver] or       # No repeat receivers across rounds
                    (self.prevent_reciprocal_pairs and      # Optional: prevent reciprocal pairs
                     (reciprocal_in_current or reciprocal_in_history))
                )

                if is_invalid:
                    valid_pairing = False
                    break

            if valid_pairing:
                valid.append(pairing)
        
        return valid
    
    def generate_pairings(self, rounds):
        """Generates pairings for all rounds"""
        all_pairings = []
        
        for round_num, round_config in enumerate(rounds, 1):
            valid = self.validate_round(
                round_config['participants'],
                round_config.get('exclusions', {})
            )
            
            if not valid:
                raise ValueError(f"No valid pairings for round {round_num}")
            
            chosen = random.choice(valid)
            all_pairings.append({
                'pairing': dict(chosen),
                'budget': round_config['budget']
            })

            # Update history
            for giver, receiver in chosen:
                self.history[giver].add(receiver)
                self.pair_history.add((giver, receiver))
                
        return all_pairings