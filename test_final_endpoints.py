import requests
import json

# URL base
base_url = 'https://api-portalweb-927498545444.us-central1.run.app'

print('=== VERIFICAR CONECTIVIDAD ===')
try:
    # Probar endpoint básico sin autenticación
    response = requests.get(f'{base_url}/api/auth/health', timeout=10)
    print(f'Status Health: {response.status_code}')
    if response.status_code == 200:
        print(f'Health Response: {response.text}')
    else:
        print(f'Health Error: {response.text}')
except Exception as e:
    print(f'Error Health: {e}')

print('\n=== PROBAR LOGIN ===')
try:
    # Datos de login
    login_data = {
        'username': 'fsoto',
        'password': '212121'
    }
    
    # Login
    login_response = requests.post(f'{base_url}/api/auth/login', json=login_data, timeout=10)
    print(f'Status Login: {login_response.status_code}')
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f'Login Success: {login_result.get("success")}')
        token = login_result.get('access_token')
        
        if token:
            print(f'Token obtenido: {token[:50]}...')
            
            # Headers para requests autenticados
            headers = {'Authorization': f'Bearer {token}'}
            
            cuartel_id = 1020200501
            
            print(f'\n=== INFORMACIÓN GENERAL CUARTEL {cuartel_id} ===')
            try:
                info_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/informacion-general', headers=headers, timeout=10)
                print(f'Status Info: {info_response.status_code}')
                if info_response.status_code == 200:
                    result = info_response.json()
                    print(f'✅ ÉXITO - Información General:')
                    print(f'Cuartel: {result["data"]["cuartel"]["nombre"]}')
                    print(f'Variedad: {result["data"]["cuartel"]["variedad"]}')
                    print(f'Superficie: {result["data"]["cuartel"]["superficie_productiva"]} ha')
                else:
                    print(f'❌ Error Info: {info_response.text}')
            except Exception as e:
                print(f'❌ Error Info: {e}')
            
            print(f'\n=== MAPEOS CUARTEL {cuartel_id} ===')
            try:
                mapeos_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/mapeos', headers=headers, timeout=10)
                print(f'Status Mapeos: {mapeos_response.status_code}')
                if mapeos_response.status_code == 200:
                    result = mapeos_response.json()
                    print(f'✅ ÉXITO - Mapeos:')
                    print(f'Total mapeos: {result["data"]["total"]}')
                    if result["data"]["mapeos"]:
                        mapeo = result["data"]["mapeos"][0]
                        print(f'Último mapeo: {mapeo["fecha"]} - Plantas 7: {mapeo["plantas_7"]}')
                else:
                    print(f'❌ Error Mapeos: {mapeos_response.text}')
            except Exception as e:
                print(f'❌ Error Mapeos: {e}')
                
        else:
            print('No se encontró token en la respuesta')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')
