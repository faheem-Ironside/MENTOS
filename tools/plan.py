# tools/plan.py

# List of allowed user IDs (Only these users can use charge commands)
ALLOWED_USERS = {7362918250,7163839299,7980317129 }  # Add user IDs here

# Function to check if a user is allowed
def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS

# Function to add a user (only the bot owner can do this)
def add_user(user_id):
    ALLOWED_USERS.add(user_id)

# Function to remove a user
def remove_user(user_id):
    ALLOWED_USERS.discard(user_id)