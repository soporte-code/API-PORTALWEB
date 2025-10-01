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
            
            cuartel_id = 1020200501
            
            print(f'\n=== PROBAR ENDPOINT SIMPLE ===')
            
            # Probar endpoint básico de cuarteles primero
            try:
                cuarteles_response = requests.get(f'{base_url}/api/cuarteles', headers=headers)
                print(f'Status Cuarteles: {cuarteles_response.status_code}')
                if cuarteles_response.status_code == 200:
                    result = cuarteles_response.json()
                    print(f'Total cuarteles: {len(result.get("data", {}).get("cuarteles", []))}')
                    # Buscar nuestro cuartel específico
                    cuarteles = result.get("data", {}).get("cuarteles", [])
                    nuestro_cuartel = next((c for c in cuarteles if c.get('id') == cuartel_id), None)
                    if nuestro_cuartel:
                        print(f'Cuartel encontrado: {nuestro_cuartel.get("nombre")}')
                    else:
                        print(f'Cuartel {cuartel_id} no encontrado en la lista')
                else:
                    print(f'Error Cuarteles: {cuarteles_response.text}')
            except Exception as e:
                print(f'Error Cuarteles: {e}')
                
        else:
            print('No se encontró token en la respuesta')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')
