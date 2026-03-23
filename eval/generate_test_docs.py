import json
import os
import random
from faker import Faker

def generate_documents(num_docs=50, output_file="eval/synthetic_docs.json"):
    # Fix the seed for reproducible evaluation
    Faker.seed(42)
    random.seed(42)
    fake = Faker('en_US')
    
    # We define robust templates containing diverse PII
    templates = [
        "Please contact {PERSON} at {EMAIL} or call {PHONE}. They work at {ORG} located in {LOCATION}. Registration date is {DATE}. IP logged: {IP}. Paid with card {CREDIT_CARD}.",
        "Patient {PERSON} ({LOCATION}) was admitted on {DATE}. Next of kin email: {EMAIL}. Billing phone: {PHONE}. Network: {IP}.",
        "Employee {PERSON} from {ORG} can be reached at {PHONE}. Address: {LOCATION}. Account {CREDIT_CARD}. Login IP {IP} at {DATE}. Contact {EMAIL}.",
        "The server at {IP} was accessed by {PERSON} on {DATE}. Please update the file for {ORG}. If urgent, call {PHONE} or email {EMAIL}. Location recorded as {LOCATION}. Card on file: {CREDIT_CARD}.",
        "We are processing a refund for {PERSON} to the card {CREDIT_CARD}. Address on file is {LOCATION}. For questions, contact {ORG} at {EMAIL} or {PHONE}. Processed at {DATE} from IP {IP}."
    ]
    
    docs = []
    for i in range(num_docs):
        template = random.choice(templates)
        
        person = fake.name()
        email = fake.email()
        # Clean phone numbers to formats presidio easily catches across standard en
        phone = fake.numerify("###-###-####")
        org = fake.company()
        location = f"{fake.city()}, {fake.country()}"
        # A standard date string to avoid complex temporal variations
        date_time = fake.date_this_decade().strftime("%Y-%m-%d")
        ip = fake.ipv4()
        credit_card = fake.credit_card_number()
        
        text = template.format(
            PERSON=person,
            EMAIL=email,
            PHONE=phone,
            ORG=org,
            LOCATION=location,
            DATE=date_time,
            IP=ip,
            CREDIT_CARD=credit_card
        )
        
        expected_entities = [
            {"type": "PERSON", "value": person},
            {"type": "EMAIL_ADDRESS", "value": email},
            {"type": "PHONE_NUMBER", "value": phone},
            {"type": "ORGANIZATION", "value": org},
            {"type": "LOCATION", "value": location},
            {"type": "DATE_TIME", "value": date_time},
            {"type": "IP_ADDRESS", "value": ip},
            {"type": "CREDIT_CARD", "value": credit_card},
        ]
        
        docs.append({
            "id": i + 1,
            "text": text,
            "expected_entities": expected_entities
        })
        
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
        
    print(f"Generated {num_docs} synthetic documents at {output_file}")

if __name__ == "__main__":
    generate_documents()
