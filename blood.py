import firebase_admin
from firebase_admin import credentials, firestore, auth
import hashlib
import datetime
import random
import smtplib
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

cred = credentials.Certificate(r'C:\Users\selvin david\Downloads\autobots-669b0-firebase-adminsdk-fbsvc-9d1fc1f7f6.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id(username):
    return hashlib.md5(username.encode()).hexdigest()[:10]

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    sender_email = "your-email@gmail.com"
    sender_password = "your-app-password"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        message = f"Subject: Blood Donation OTP\n\nYour OTP code is: {otp}"
        server.sendmail(sender_email, email, message)
        server.quit()
    except Exception as e:
        print("Error Sending OTP:", e)
    
    return otp

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

    if user_otp != otp:
        print("Invalid OTP. Registration Failed!")
        return

    hashed_password = hash_password(password)
    user_id = generate_user_id(username)

    db.collection("users").document(username).set({
        "id": user_id,
        "email": email,
        "phone": phone,
        "location": location,
        "age": age,
        "disease": disease,
        "password": hashed_password,
        "blood_group": blood_group,
        "reward_points": 0
    })
    print(f"Registration Successful! Your User ID: {user_id}")

def donate_blood():
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()

    if not user_doc.exists or user_doc.to_dict()["password"] != hash_password(password):
        print("Invalid Credentials!")
        return

    if user_doc.to_dict()["disease"] == "yes":
        print("You are not eligible to donate blood due to health conditions.")
        return

    blood_group = user_doc.to_dict()["blood_group"]
    location = user_doc.to_dict()["location"]
    today = datetime.date.today().isoformat()

    db.collection("blood_donations").add({
        "username": username,
        "blood_group": blood_group,
        "location": location,
        "donation_date": today
    })

    new_points = user_doc.to_dict()["reward_points"] + 10
    user_ref.update({"reward_points": new_points})

    print(f"Thank you for donating! 10 points added. Your total points: {new_points}")

def check_donation_history():
    username = input("Enter Username: ")
    donations = db.collection("blood_donations").where("username", "==", username).stream()

    print(f"\nDonation History for {username}:")
    found = False
    for donation in donations:
        found = True
        data = donation.to_dict()
        print(f"- Blood Group: {data['blood_group']}, Date: {data['donation_date']}, Location: {data['location']}")

    if not found:
        print("No donation records found.")

def search_nearby_donors():
    location = input("Enter Location: ")
    blood_group = input("Enter Required Blood Group: ").upper()
    
    donors = db.collection("users").where("blood_group", "==", blood_group).where("location", "==", location).stream()
    found = False

    print(f"\nAvailable Donors in {location} for {blood_group}:")
    for donor in donors:
        found = True
        data = donor.to_dict()
        print(f"- Name: {donor.id}, Phone: {data['phone']}")

    if not found:
        print("No donors found in your area.")

def predict_blood_demand():
    try:
        model = joblib.load("blood_demand_model.pkl")
    except FileNotFoundError:
        print("AI Model not found! Train the model first.")
        return

    location = input("Enter Location: ")
    blood_group = input("Enter Blood Group: ").upper()
    today = datetime.datetime.today().toordinal()

    predicted_demand = model.predict([[today]])
    print(f"Predicted Demand for {blood_group} in {location}: {int(predicted_demand[0])} units")

def train_blood_demand_model():
    donations = db.collection("blood_donations").stream()
    data = []

    for donation in donations:
        data.append({
            "date": datetime.datetime.strptime(donation.to_dict()["donation_date"], "%Y-%m-%d").toordinal(),
            "blood_group": donation.to_dict()["blood_group"]
        })

    df = pd.DataFrame(data)

    if df.empty:
        print("Not enough data to train the model.")
        return

    X = df[["date"]]
    y = df["blood_group"].value_counts().reindex(df["blood_group"]).fillna(0)

    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, "blood_demand_model.pkl")

    print("AI Blood Demand Prediction Model Trained Successfully!")

def main():
    while True:
        print("\nBlood Donation System")
        print("1. Register")
        print("2. Donate Blood")
        print("3. Check Donation History")
        print("4. Search Nearby Donors")
        print("5. Predict Blood Demand")
        print("6. Train Blood Demand Model")
        print("7. Exit")
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
            predict_blood_demand()
        elif choice == "6":
            train_blood_demand_model()
        elif choice == "7":
            print("Exiting... Thank you!")
            break
        else:
            print("Invalid Choice! Try again.")

if __name__== "_main_":
    main()
