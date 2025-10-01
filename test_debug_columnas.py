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
            
            print(f'\n=== VERIFICAR COLUMNAS DE TABLAS ===')
            
            # Verificar columnas de general_dim_cuartel
            print(f'\n--- Columnas de general_dim_cuartel ---')
            try:
                debug_response = requests.get(f'{base_url}/api/estimaciones/debug-columnas/general_dim_cuartel', headers=headers)
                print(f'Status Debug Cuartel: {debug_response.status_code}')
                if debug_response.status_code == 200:
                    result = debug_response.json()
                    print(f'Columnas disponibles: {result["data"]["columnas"]}')
                else:
                    print(f'Debug Error: {debug_response.text}')
            except Exception as e:
                print(f'Error Debug Cuartel: {e}')
            
            # Verificar columnas de mapeo_fact_registromapeo
            print(f'\n--- Columnas de mapeo_fact_registromapeo ---')
            try:
                debug_response = requests.get(f'{base_url}/api/estimaciones/debug-columnas/mapeo_fact_registromapeo', headers=headers)
                print(f'Status Debug Mapeo: {debug_response.status_code}')
                if debug_response.status_code == 200:
                    result = debug_response.json()
                    print(f'Columnas disponibles: {result["data"]["columnas"]}')
                else:
                    print(f'Debug Error: {debug_response.text}')
            except Exception as e:
                print(f'Error Debug Mapeo: {e}')
                
        else:
            print('No se encontró token en la respuesta')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')
