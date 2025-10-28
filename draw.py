import yaml
import os
import hashlib
import time
import json
import argparse
from collections import defaultdict
from matcher import SecretSantaMatcher
from mail_utils import EmailHandler

def load_config(yaml_path):
    """Load configuration from YAML file"""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def load_mail_contacts(filename):
    """Load email contact information from JSON file"""
    with open(filename, 'r') as file:
        return json.load(file)

def generate_emails(all_pairings, config, draw_id):
    """Generate emails for all participants"""
    email_handler = EmailHandler(config)
    emails = defaultdict(list)
    total_rounds = len(all_pairings)
    
    # Generate assignment texts for each participant
    for round_num, round_data in enumerate(all_pairings, 1):
        for giver, receiver in round_data['pairing'].items():
            assignment = email_handler.format_assignment(
                receiver, round_num, total_rounds, round_data['budget']
            )
            emails[giver].append(assignment)
    
    # Generate complete emails
    return {
        name: email_handler.generate_email(name, assignments, draw_id)
        for name, assignments in emails.items()
    }

def generate_summary(all_pairings):
    """Thank you perplexity for the help"""
    participants = set()
    for round_data in all_pairings:
        participants.update(round_data['pairing'].keys())
    participants = sorted(participants)
    
    col_width = 20 
    
    header = f"{'Participant':<{col_width}}"
    for round_num, round_data in enumerate(all_pairings, 1):
        budget = round_data['budget']
        header += f"Round {round_num} ({budget})".ljust(col_width)
    lines = [header]
    lines.append("-" * len(header))
    
    # Prepare rows
    for name in participants:
        row = f"{name:<{col_width}}"
        for round_num, round_data in enumerate(all_pairings, 1):
            pairing = round_data['pairing']
            if name in pairing:
                val = pairing[name]
            else:
                val = "-"
            row += f"{val:<{col_width}}"
        lines.append(row)
    
    return "\n".join(lines)


def run_draw():
    """Main function to run the Secret Santa draw"""
    DRAW_ID = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    SENDER_MAIL = args.gmail_sender
    SENDER_PW = args.gmail_password  #might have to be an "app password" for Gmail
    
    # Load configuration and contacts
    config = load_config('data/config.yaml')
    mail_adresses = load_mail_contacts('data/contact_information.json')
    
    # Initialize handlers
    matcher = SecretSantaMatcher(avoid_bidirectional=True)
    email_handler = EmailHandler(config)
    
    # Generate pairings and emails
    all_pairings = matcher.generate_pairings(config['rounds'])
    emails = generate_emails(all_pairings, config, DRAW_ID)
    
    if args.debug:
        # Save all mails as HTML files in "debug" folder
        for name, content in emails.items():
            with open(f"debug/{name}.html", "w") as f:
                f.write(content)
        if args.debug_email_user and args.debug_email_user in mail_adresses:
            email_handler.send_email(
                SENDER_MAIL, 
                SENDER_PW, 
                mail_adresses[args.debug_email_user], 
                emails[args.debug_email_user]
            )
        # Save summary as text file
        summary = generate_summary(all_pairings)
        with open("debug/summary.txt", "w") as f:
            f.write(summary)
        print(f"Summary Draw [{DRAW_ID}]:\n{summary}")
        print("\nDebug files created.")
    else:
        print("Draw ID:", DRAW_ID)
        # Send all mails
        for name, content in emails.items():
            email_handler.send_email(
                SENDER_MAIL, 
                SENDER_PW, 
                mail_adresses[name], 
                content
            )
    
    print("Draw completed.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Secret Santa draw.")
    parser.add_argument('--debug', action='store_true', help="Run in debug mode.")
    parser.add_argument('--debug_email_user', type=str, help="Debug Mail. Enter User Mail shall be sent to.", default=None)
    parser.add_argument('--gmail_sender', type=str, help="Gmail Sender Mail.", default=os.getenv("SENDER_MAIL"))
    parser.add_argument('--gmail_password', type=str, help="Gmail Sender Password.", default=os.getenv("SENDER_PW"))
    args = parser.parse_args()

    run_draw()
