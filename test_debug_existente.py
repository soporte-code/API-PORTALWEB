import requests
import json

# URL base
base_url = 'https://api-portalweb-927498545444.us-central1.run.app'

# Datos de login
login_data = {
    'username': 'fsoto',
    'password': '212121'
}

print('=== AUTENTICACIÓN ===')
try:
    # Login
    login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
    print(f'Status Login: {login_response.status_code}')
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('access_token')
        
        if token:
            print(f'Token obtenido: {token[:50]}...')
            
            # Headers para requests autenticados
            headers = {'Authorization': f'Bearer {token}'}
            
            print(f'\n=== USAR ENDPOINT DEBUG EXISTENTE ===')
            
            # Usar el endpoint de debug de pautas que ya existe
            try:
                debug_response = requests.get(f'{base_url}/api/pautas/debug-tablas', headers=headers)
                print(f'Status Debug Tablas: {debug_response.status_code}')
                if debug_response.status_code == 200:
                    result = debug_response.json()
                    print(f'Debug Response: {json.dumps(result, indent=2, ensure_ascii=False)}')
                else:
                    print(f'Debug Error: {debug_response.text}')
            except Exception as e:
                print(f'Error Debug: {e}')
                
        else:
            print('No se encontró token en la respuesta')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')
