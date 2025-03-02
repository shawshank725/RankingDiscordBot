import os
# Function to read .env file
def load_env_file(filepath):
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):  # Ignore empty lines and comments
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
