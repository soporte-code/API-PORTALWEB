import requests
import json

print("🔍 Debugging login issue...")

# Test simple
try:
    response = requests.post(
        "http://localhost:5000/api/auth/login",
        headers={"Content-Type": "application/json"},
        json={"usuario": "212121", "clave": "212121"},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except requests.exceptions.Timeout:
    print("❌ Timeout - El servidor no responde")
except requests.exceptions.ConnectionError:
    print("❌ Connection Error - No se puede conectar al servidor")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔍 Verificando si el servidor responde...")

# Test de conectividad básica
try:
    response = requests.get("http://localhost:5000/", timeout=5)
    print(f"Server response: {response.status_code}")
except Exception as e:
    print(f"Server not responding: {e}")
