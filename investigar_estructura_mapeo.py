import requests
import json

# URL base
base_url = 'https://api-portalweb-927498545444.us-central1.run.app'

# Datos de login
login_data = {
    'username': 'fsoto',
    'password': '212121'
}

print('=== INVESTIGAR ESTRUCTURA TABLA MAPEO ===')
try:
    # Login
    login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
    print(f'Login Status: {login_response.status_code}')
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('access_token')
        
        if token:
            print('Login EXITOSO')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Probar consulta simple para ver qué columnas existen
            print(f'\n--- PROBAR CONSULTA SIMPLE ---')
            try:
                # Crear un endpoint temporal para debug
                debug_query = """
                    SELECT rm.* 
                    FROM mapeo_fact_registromapeo rm 
                    LIMIT 1
                """
                
                # Usar el endpoint de debug de pautas si existe
                debug_response = requests.get(f'{base_url}/api/pautas/debug-tablas', headers=headers)
                print(f'Status Debug: {debug_response.status_code}')
                if debug_response.status_code == 200:
                    print('Debug disponible:', debug_response.text[:200])
                else:
                    print('Debug no disponible')
                    
            except Exception as e:
                print(f'Error Debug: {e}')
                
        else:
            print('No se obtuvo token')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')

print('\n=== RESUMEN ===')
print('Investigación de estructura de tabla completada.')
