import random
import yaml
import json
from mail_utils import send_email, move_email_to_archive


MAX_ATTEMPTS = 20

def load_data(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)
    
def load_mail_contacts(filename): 
    with open(filename, 'r') as file:
        return json.load(file)
    

def draw(names, exclusions=None, previous_pairings=None):
    attempts =0
    if exclusions is None:
        exclusions = {}
    if previous_pairings is None:
        previous_pairings = {}
        
    receivers = names[:]
    givers = names[:]
    random.shuffle(receivers)
    pairs = {}
    
    for giver in givers:
        receiver = random.choice(receivers)
        while receiver == giver \
            or (giver in exclusions and receiver in exclusions[giver]) \
            or (previous_pairings.get(giver) == receiver) \
            or (previous_pairings.get(receiver) == giver):
            receiver = random.choice(receivers)
            if attempts > MAX_ATTEMPTS: #RECURSIVE DOOM
                return draw(names, exclusions, previous_pairings)
            else:
                attempts += 1 
        pairs[giver] = receiver
        receivers.remove(receiver)
    
    return pairs

def emails_for_pairings(pairings, stage):
    emails = []
    for giver, receiver in pairings.items():
        emails.append(
            (giver, receiver, f"Runde {stage}: {giver}, du hast {receiver} gezogen!")
        )
    return emails



def main():
    data = load_data("secret_santa.yaml")
    mail_contacts = load_mail_contacts("mail_contacts.json")

    previous_pairings = {}
    final_pairings = []
    
    for i, draw_info in enumerate(data["draws"], start=1):
        participants = draw_info["participants"]
        exclusions = draw_info.get("exclusions", {})
        pairs = draw(participants, exclusions, previous_pairings)
        print(f"Draw {i}:")
        for giver, receiver in pairs.items():
            print(f"{giver} -> {receiver}")
        previous_pairings.update(pairs)
        final_pairings.append(pairs)

    emails = []
    for i, pairings in enumerate(final_pairings, start=1):
        emails.extend(emails_for_pairings(pairings, i))
    print("Sending emails...")
    
    for giver, receiver, body in emails:
        send_email(mail_contacts[giver], body, body)
        move_email_to_archive(mail_contacts[giver])

if __name__ == "__main__":
    main()
