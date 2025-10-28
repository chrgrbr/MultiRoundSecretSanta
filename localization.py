class Translations:
    TRANSLATIONS = {
        'en': {
            'round': 'Round',
            'assignment_singular': 'is your Secret Santa assignment',
            'assignment_plural': 'are your Secret Santa assignments',
            'budget': 'Budget',
            'greeting': 'Hello {}!',
            'footer': 'Festively compiled by your friendly neighborhood bot',
        },
        'de': {
            'round': 'Runde',
            'assignment_singular': 'ist dein Wichtelauftrag',
            'assignment_plural': 'sind deine Wichtelaufträge',
            'budget': 'Budget',
            'greeting': 'Hey {}!',
            'footer': 'Beste automatisierte Grüße',
        }
    }
    
    def __init__(self, language='en'):
        self.language = language
        if language not in self.TRANSLATIONS:
            raise ValueError(f"Language '{language}' is not supported. Available languages: {list(self.TRANSLATIONS.keys())}")
        self.texts = self.TRANSLATIONS[language]
    
    def get_assignment_text(self, is_singular):
        """Get the appropriate assignment text based on count"""
        key = 'assignment_singular' if is_singular else 'assignment_plural'
        return self.texts[key]
    
    def format_round(self, round_num):
        """Format the round number text"""
        return f"{self.texts['round']} {round_num}"
    
    def format_budget(self, budget):
        """Format the budget text"""
        return f"({self.texts['budget']}: {budget})"
    
    def format_greeting(self, name):
        """Format the greeting"""
        return self.texts['greeting'].format(name)
    
    def get_footer(self):
        """Get the footer text"""
        return self.texts['footer']