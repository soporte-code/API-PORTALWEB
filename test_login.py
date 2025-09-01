import requests
import json

# URL del endpoint de login
url = "http://localhost:5000/api/auth/login"

# Headers
headers = {
    "Content-Type": "application/json"
}

# Datos de prueba
data = {
    "usuario": "212121",
    "clave": "212121"
}

print("🔍 Probando login con usuario: 212121")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=data)
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ Login exitoso!")
        result = response.json()
        print(f"Token: {result.get('access_token', 'No token')[:50]}...")
        print(f"Usuario: {result.get('usuario')}")
        print(f"Nombre: {result.get('nombre')}")
    else:
        print("❌ Error en login!")
        print(f"Response: {response.text}")
        
        # Intentar parsear el JSON de error
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print("No se pudo parsear la respuesta como JSON")
            
except Exception as e:
    print(f"❌ Error en la petición: {e}")

print("\n🔍 Probando con diferentes formatos de datos...")

# Probar con diferentes nombres de campos
test_cases = [
    {"usuario": "212121", "clave": "212121"},
    {"username": "212121", "password": "212121"},
    {"email": "212121", "pass": "212121"}
]

for i, test_data in enumerate(test_cases, 1):
    print(f"\n--- Test {i}: {list(test_data.keys())} ---")
    try:
        response = requests.post(url, headers=headers, json=test_data)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("✅ Éxito!")
    except Exception as e:
        print(f"Error: {e}")
