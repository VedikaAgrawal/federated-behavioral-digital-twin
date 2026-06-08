from faker import Faker
import random
import datetime

fake_in = Faker('en_IN')
fake_global = Faker() # For international jumps

class TransactionGenerator:
    def __init__(self):
        self.categories = [
            "groceries", "dining", "gas", "electronics", "travel", 
            "fashion", "healthcare", "entertainment"
        ]
    
    def generate_user_profile(self):
        """Creates a 'Persona' for a user (Home base, habits)"""
        # Fixed list of Indian metros for better consistency
        indian_cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
        home_city = random.choice(indian_cities)
        
        return {
            "user_id": fake_in.uuid4(),
            "name": fake_in.name(),
            "home_city": home_city,
            "home_country": "IN",
            "home_lat": float(fake_in.latitude()), 
            "home_lon": float(fake_in.longitude()),
            "avg_spend": random.uniform(500, 5000), # Adjusted for INR-like values
            "preferred_categories": random.sample(self.categories, 3),
            "friends": [fake_in.uuid4() for _ in range(3)] 
        }

    def generate_transaction(self, user_persona, is_fraud=False):
        """Generates a single transaction. 
        If is_fraud=False, matches persona.
        If is_fraud=True, deviates from persona.
        """
        
        timestamp = datetime.datetime.now()
        
        if not is_fraud:
            # Normal Behavior
            # 95% chance it's in the home city (Increased for stability)
            # FORCE home city if user is very new (count < 5)
            if random.random() < 0.95 or user_persona.get('transaction_count', 0) < 5:
                city = user_persona['home_city']
                country = user_persona.get('home_country', 'IN')
                lat = user_persona['home_lat']
                lon = user_persona['home_lon']
            else:
                # Still in India, but a different city
                city = fake_in.city()
                country = "IN" 
                lat = user_persona["home_lat"] + random.uniform(-0.1, 0.1)
                lon = user_persona["home_lon"] + random.uniform(-0.1, 0.1)
            
            # Amount close to average
            amount = random.gauss(user_persona["avg_spend"], user_persona["avg_spend"] * 0.15)
            amount = max(5.0, round(amount, 2))
            
            # Category likely to be preferred
            if random.random() < 0.8:
                category = random.choice(user_persona["preferred_categories"])
            else:
                category = random.choice(self.categories)
                
            merchant = fake_in.company()
            tx_type = "purchase"
            recipient = None
            
            # 25% chance it's a transfer to a friend (increased for visualization)
            if random.random() < 0.25:
                tx_type = "transfer"
                recipient = random.choice(user_persona["friends"])
                category = "transfer"
                merchant = "Bank Transfer"
            
        else:
            # FRAUD Behavior
            fraud_type = random.choice(["high_amount", "location_jump", "strange_cat", "transfer_scam"])
            
            if fraud_type == "high_amount":
                city = user_persona["home_city"]
                country = user_persona["home_country"]
                lat = user_persona["home_lat"]
                lon = user_persona["home_lon"]
                # Increased multiplier to trigger DECLINED consistently
                amount = random.uniform(user_persona["avg_spend"] * 10, user_persona["avg_spend"] * 25)
                amount = round(amount, 2)
                category = "electronics"
                
            elif fraud_type == "location_jump":
                # Use Global Faker to ensure city matches the foreign country
                country = fake_global.country_code()
                while country == "IN":
                     country = fake_global.country_code()
                
                city = fake_global.city() 
                lat = float(fake_global.latitude())
                lon = float(fake_global.longitude())
                amount = random.uniform(1000, 10000)
                category = random.choice(self.categories)
                
            else:
                city = user_persona["home_city"]
                country = user_persona["home_country"]
                lat = user_persona["home_lat"]
                lon = user_persona["home_lon"]
                amount = random.uniform(2000, 15000)
                category = "luxury_jewelry"
                
            # Use diverse Indian merchant names
            # 50% chance for a generic company, 50% for a suspicious looking one
            if random.random() < 0.5:
                merchant = fake_in.company()
            else:
                suspicious_prefixes = ["ShadowIn", "VortexRT", "GlobalBharat", "BharatPay", "KolkataSecure", "MumbaiDirect"]
                merchant = f"{random.choice(suspicious_prefixes)} {fake_in.company_suffix()}"
            tx_type = "purchase"
            recipient = None
            
            if fraud_type == "transfer_scam":
                tx_type = "transfer"
                recipient = fake_in.uuid4()
                category = "transfer"
                merchant = "Wire Transfer"
                amount = random.uniform(1000, 5000)

        # Determine if it's a night transaction (simulated for federated logic)
        hour = timestamp.hour
        is_night = hour < 6 or hour > 22
        
        return {
            "transaction_id": fake_in.uuid4(),
            "timestamp": timestamp,
            "is_night_txn": is_night, # New field for Federated Learning
            "amount": amount,
            "merchant": merchant,
            "city": city,
            "country": country,
            "lat": lat,
            "lon": lon,
            "category": category,
            "type": tx_type,
            "recipient_id": recipient,
            "is_fraud_ground_truth": is_fraud # For verification
        }

    def generate_batch_data(self, user_persona, count=50):
        """Generates a batch of historical transactions for CSV export."""
        batch = []
        for _ in range(count):
            tx = self.generate_transaction(user_persona, is_fraud=False)
            tx["user_id"] = user_persona["user_id"]
            batch.append(tx)
        return batch

    def generate_global_fraud_batch(self, count=10):
        """Generates historical fraud patterns from other 'banks'."""
        patterns = []
        for _ in range(count):
            # Create a temporary persona for another bank's victim
            temp_user = self.generate_user_profile()
            tx = self.generate_transaction(temp_user, is_fraud=True)
            patterns.append({
                "bank_id": random.choice(["HDFC_BANK", "ICICI_BANK", "AXIS_BANK"]),
                "merchant": tx["merchant"],
                "city": tx["city"],
                "category": tx["category"],
                "amount": tx["amount"]
            })
        return patterns
