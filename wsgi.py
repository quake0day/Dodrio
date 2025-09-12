from main import app
import os

if __name__ == "__main__":
    # For development with SSL (if certificates exist)
    cert_file = './4fa581949f17aaa.crt'
    key_file = './darlingtree.key'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # Run with SSL
        app.run(host='0.0.0.0', port=443, ssl_context=(cert_file, key_file))
    else:
        # Run without SSL
        print("SSL certificates not found, running without SSL on port 5000")
        app.run(host='0.0.0.0', port=5000)