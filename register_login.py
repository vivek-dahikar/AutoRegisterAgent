from flask import Flask, request, jsonify
from langchain_ollama import OllamaLLM
import hashlib

app = Flask(__name__)

llm = OllamaLLM(model="llama3.2")

# In-memory user database (for simplicity)
users_db = {}

# Helper function to hash passwords
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Signup endpoint - AI validates and saves user credentials
@app.route("/signup", methods=["POST"])
def signup():
    try:
        # Get data from the request
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")        
        
        # AI prompt to validate signup
        prompt = f"""
        The current user database is: {users_db}.
        The following are the user credentials: username={username}, password={password}.
        Please validate the username and password.
        - Check if the username already exists.
        - Ensure the password is has 3 digit (e.g. 123).
        If the credentials are valid, say 'valid'. Otherwise, provide suggestions or errors.
        """
        
        # AI validation via LLaMA model
        ai_response = llm.invoke(prompt)
        
        # Process AI response
        if "valid" in ai_response.lower() and username not in users_db:
            # Hash password before saving
            users_db[username] = {"password": hash_password(password)}
            return jsonify({"message": "User registered successfully!"})
        else:
            return jsonify({"error": f"Invalid credentials or username already taken. AI Response: {ai_response}"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Login endpoint - AI validates login credentials
@app.route("/login", methods=["POST"])
def login():
    try:
        # Get data from the request
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        # AI prompt to validate login
        prompt = f"""
        The current user database is: {users_db}.
        The following are the login credentials: username={username}, password={password}.
        Please validate if these credentials match any existing user records.
        If they match, say 'valid'. If not, say 'invalid' and provide feedback.
        """
        
        # AI validation via LLaMA model
        ai_response = llm.invoke(prompt)
        
        # Check if AI confirms the credentials
        if "valid" in ai_response.lower() and username in users_db and users_db[username]["password"] == hash_password(password):
            return jsonify({"message": "Login successful!"})
        else:
            return jsonify({"error": f"Invalid credentials. AI Response: {ai_response}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define the POST endpoint for processing prompts
@app.route("/process", methods=["POST"])
def process_prompt():
    try:
        # Get the 'prompt' from the JSON body
        data = request.get_json()
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "Prompt field is required"}), 400
        
        # Get the response from the LLaMA model
        response = llm.invoke(prompt)
        
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
