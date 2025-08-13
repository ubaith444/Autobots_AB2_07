import random
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.neighbors import KNeighborsClassifier

class BloodBankSystem:
    def __init__(self):
        self.blood_requests = {"A+": [], "A-": [], "B+": [], "B-": [], "O+": [], "O-": [], "AB+": [], "AB-": []}
        self.donors = {"A+": [], "A-": [], "B+": [], "B-": [], "O+": [], "O-": [], "AB+": [], "AB-": []}
        self.notifications = {}
        self.cred = credentials.Certificate(r'C:\Users\selvin david\Downloads\autobots-669b0-firebase-adminsdk-fbsvc-9d1fc1f7f6.json')
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
        self.knn = KNeighborsClassifier(n_neighbors=3)
        self.train_model()

    def train_model(self):
        sample_data = [[25, 1], [30, 0], [35, 1], [40, 0]]
        sample_labels = ["A+", "O-", "B+", "AB-"]
        self.knn.fit(sample_data, sample_labels)

    def request_blood(self, blood_type, patient_name):
        if blood_type in self.blood_requests:
            self.blood_requests[blood_type].append(patient_name)
            self.notify(patient_name, f"Your blood request for {blood_type} has been received and is pending.")
        else:
            print("Invalid blood type.")

    def donate_blood(self, blood_type, donor_name, age, health_status):
        if blood_type in self.donors:
            if self.detect_fraud(donor_name):
                print("Potential fraud detected. Donation rejected.")
                return
            self.donors[blood_type].append(donor_name)
            self.notify(donor_name, f"Thank you for donating blood for {blood_type}.")
        else:
            print("Invalid blood type.")

    def detect_fraud(self, donor_name):
        donor_ref = self.db.collection("donors").document(donor_name).get()
        if donor_ref.exists:
            return True
        return False

    def smart_donor_recommendation(self, age, health_status):
        blood_prediction = self.knn.predict([[age, health_status]])
        return blood_prediction[0]

    def notify(self, name, message):
        if name not in self.notifications:
            self.notifications[name] = []
        self.notifications[name].append(message)

    def view_notifications(self, name):
        return self.notifications.get(name, ["No notifications found."])

    def chatbot(self, query):
        responses = {
            "How to donate?": "To donate blood, visit our nearest center and register.",
            "Eligibility criteria?": "You must be 18+, healthy, and weigh at least 50kg.",
        }
        return responses.get(query, "I don't understand. Please ask another question.")

    def display_status(self):
        print("\nBlood Requests:")
        for blood_type, requests in self.blood_requests.items():
            print(f"{blood_type}: {len(requests)} requests")
        print("\nBlood Donors:")
        for blood_type, donors in self.donors.items():
            print(f"{blood_type}: {len(donors)} donors")

def main():
    system = BloodBankSystem()
    while True:
        print("\n1. Request Blood")
        print("2. Donate Blood")
        print("3. Fulfill Blood Request")
        print("4. Display Status")
        print("5. View Notifications")
        print("6. Chatbot Assistance")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            blood_type = input("Enter blood type: ")
            patient_name = input("Enter patient name: ")
            system.request_blood(blood_type, patient_name)
        elif choice == '2':
            blood_type = input("Enter blood type: ")
            donor_name = input("Enter donor name: ")
            age = int(input("Enter donor age: "))
            health_status = int(input("Enter health status (1-Good, 0-Poor): "))
            system.donate_blood(blood_type, donor_name, age, health_status)
        elif choice == '3':
            blood_type = input("Enter blood type to fulfill request: ")
            system.fulfill_request(blood_type)
        elif choice == '4':
            system.display_status()
        elif choice == '5':
            name = input("Enter name: ")
            print(system.view_notifications(name))
        elif choice == '6':
            query = input("Ask chatbot: ")
            print(system.chatbot(query))
        elif choice == '7':
            print("Exiting system...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
