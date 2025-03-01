import datetime
import pymongo
import hashlib
import random
import smtplib
from bson.objectid import ObjectId
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blood_donation"]
users_collection = db["users"]
donations_collection = db["donations"]
requests_collection = db["requests"]  # New collection for blood requests
activity_collection = db["user_activity"]
otp_collection = db["otp"]

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to generate user ID
def generate_user_id(username):
    return "USR" + str(ObjectId())[:6]

# Function to log user activity
def log_activity(username, action):
    activity_collection.insert_one({
        "username": username,
        "action": action,
        "timestamp": datetime.datetime.now()
    })

SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"

def send_otp(email):
    otp = str(random.randint(100000, 999999))  # Generate random 6-digit OTP

    subject = "Your Blood Donation System OTP"
    message = f"Your OTP for verification is: {otp}"

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()
        
        # Save OTP in MongoDB
        otp_collection.insert_one({"email": email, "otp": otp})
        print(f"✅ OTP Sent to {email}: {otp}")
        return otp
    except Exception as e:
        print(f"❌ Failed to send OTP: {e}")
        return None
      
# Register a new user
def register_user():
    username = input("Enter Username: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone Number: ")
    location = input("Enter Location: ")
    age = input("Enter Age: ")
    disease = input("Do you have any disease? (Yes/No): ").strip().lower()
    password = input("Enter Password: ")
    blood_group = input("Enter Blood Group: ").upper()
    
    otp = send_otp(email)
    user_otp = input("Enter the OTP sent to your email: ")

    if not otp_collection.find_one({"email": email, "otp": user_otp}):
        print("Invalid OTP. Registration Failed!")
        return

    hashed_password = hash_password(password)
    user_id = generate_user_id(username)

    users_collection.insert_one({
        "id": user_id,
        "username": username,
        "email": email,
        "phone": phone,
        "location": location,
        "age": age,
        "disease": disease,
        "password": hashed_password,
        "blood_group": blood_group,
        "reward_points": 0
    })
    
    log_activity(username, "Register")
    print(f"Registration Successful! Your User ID: {user_id}")

# Donate blood
def donate_blood():
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    user = users_collection.find_one({"username": username})

    if not user or user["password"] != hash_password(password):
        print("Invalid Credentials!")
        return

    if user["disease"] == "yes":
        print("You are not eligible to donate blood due to health conditions.")
        return

    blood_group = user["blood_group"]
    location = user["location"]
    today = datetime.date.today().isoformat()

    donations_collection.insert_one({
        "username": username,
        "blood_group": blood_group,
        "location": location,
        "donation_date": today
    })

    new_points = user["reward_points"] + 10
    users_collection.update_one({"username": username}, {"$set": {"reward_points": new_points}})

    log_activity(username, "Donate Blood")
    print(f"Thank you for donating! 10 points added. Your total points: {new_points}")

# Check donation history
def check_donation_history():
    username = input("Enter Username: ")
    donations = donations_collection.find({"username": username})
    
    print("Donation History:")
    for donation in donations:
        print(donation)
    
    log_activity(username, "Check Donation History")

# Search nearby donors
def search_nearby_donors():
    location = input("Enter your location: ")
    blood_group = input("Enter required blood group: ").upper()
    
    donors = users_collection.find({"location": location, "blood_group": blood_group})
    
    print("Nearby Donors:")
    for donor in donors:
        print(donor["username"], "|", donor["phone"])
    
    log_activity(location, "Search Nearby Donors")

# Request Blood
def request_blood():
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    user = users_collection.find_one({"username": username})

    if not user or user["password"] != hash_password(password):
        print("Invalid Credentials!")
        return

    blood_group = input("Enter required blood group: ").upper()
    location = input("Enter your location: ")
    blood_units = int(input("Enter required blood units: "))

    request_data = {
        "username": username,
        "blood_group": blood_group,
        "location": location,
        "blood_units": blood_units,
        "status": "Pending",
        "request_date": datetime.date.today().isoformat()
    }

    requests_collection.insert_one(request_data)
    log_activity(username, "Request Blood")
    print("Blood request submitted successfully!")

# Check Blood Requests
def check_blood_requests():
    print("Active Blood Requests:")
    requests = requests_collection.find({"status": "Pending"})
    for request in requests:
        print(f"Username: {request['username']} | Blood Group: {request['blood_group']} | Location: {request['location']} | Units: {request['blood_units']} | Status: {request['status']}")

# Predict blood demand (Placeholder AI Function)
def predict_blood_demand():
    print("Predicting blood demand using AI...")
    # Placeholder logic for AI model
    log_activity("system", "Predict Blood Demand")
    return "Prediction Completed!"

# Train AI model for blood demand (Placeholder)
def train_blood_demand_model():
    print("Training AI model for blood demand prediction...")
    # Placeholder logic for training AI model
    log_activity("system", "Train Blood Demand Model")
    return "Training Completed!"

# View user activity log
def view_activity_log():
    username = input("Enter Username to view activity: ")
    activities = activity_collection.find({"username": username})
    
    print("User Activity Log:")
    for activity in activities:
        print(activity)

# Main menu
def main():
    while True:
        print("\nBlood Donation System")
        print("1. Register User")
        print("2. Donate Blood")
        print("3. Check Donation History")
        print("4. Search Nearby Donors")
        print("5. Request Blood")  # New Option
        print("6. Check Blood Requests")  # New Option
        print("7. Predict Blood Demand (AI)")
        print("8. Train AI Blood Demand Model")
        print("9. View User Activity Log")
        print("10. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            register_user()
        elif choice == "2":
            donate_blood()
        elif choice == "3":
            check_donation_history()
        elif choice == "4":
            search_nearby_donors()
        elif choice == "5":
            request_blood()  # New Feature
        elif choice == "6":
            check_blood_requests()  # New Feature
        elif choice == "7":
            predict_blood_demand()
        elif choice == "8":
            train_blood_demand_model()
        elif choice == "9":
            view_activity_log()
        elif choice == "10":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()
