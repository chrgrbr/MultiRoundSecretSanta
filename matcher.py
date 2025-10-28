from collections import defaultdict
from itertools import permutations
import random

class SecretSantaMatcher:
    def __init__(self, avoid_bidirectional=False):
        self.avoid_bidirectional = avoid_bidirectional
        self.history = defaultdict(set)
        self.pair_history = set()
        
    def validate_round(self, participants, exclusions=None):
        """Validates and returns all valid pairings for a round"""
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
            
            for giver, receiver in pairing:
                if (giver == receiver or 
                    receiver in exclusion_map[giver] or 
                    receiver in self.history[giver] or
                    (self.avoid_bidirectional and (receiver, giver) in self.pair_history)):
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