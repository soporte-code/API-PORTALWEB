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
        print(f'Login Response completa: {json.dumps(login_result, indent=2, ensure_ascii=False)}')
        
        # Intentar diferentes estructuras posibles del token
        token = None
        if 'data' in login_result and 'access_token' in login_result['data']:
            token = login_result['data']['access_token']
        elif 'access_token' in login_result:
            token = login_result['access_token']
        elif 'token' in login_result:
            token = login_result['token']
        
        if token:
            print(f'Token obtenido: {token[:50]}...')
            
            # Headers para requests autenticados
            headers = {'Authorization': f'Bearer {token}'}
            
            cuartel_id = 1020200501
            
            print(f'\n=== INFORMACIÓN GENERAL CUARTEL {cuartel_id} ===')
            try:
                info_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/informacion-general', headers=headers)
                print(f'Status Info: {info_response.status_code}')
                print(f'Response: {json.dumps(info_response.json(), indent=2, ensure_ascii=False)}')
            except Exception as e:
                print(f'Error Info: {e}')
            
            print(f'\n=== MAPEOS CUARTEL {cuartel_id} ===')
            try:
                mapeos_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/mapeos', headers=headers)
                print(f'Status Mapeos: {mapeos_response.status_code}')
                print(f'Response: {json.dumps(mapeos_response.json(), indent=2, ensure_ascii=False)}')
            except Exception as e:
                print(f'Error Mapeos: {e}')
                
        else:
            print('No se encontró token en la respuesta')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')