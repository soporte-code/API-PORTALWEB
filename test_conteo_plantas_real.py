import requests
import json

# URL base
base_url = 'https://api-portalweb-927498545444.us-central1.run.app'

# Datos de login
login_data = {
    'username': 'fsoto',
    'password': '212121'
}

print('=== PROBAR CONEO REAL DE PLANTAS POR TIPO ===')
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
            
            # Obtener cuarteles de la sucursal activa
            print(f'\n--- OBTENER CUARTELES SUCURSAL ACTIVA ---')
            try:
                cuarteles_response = requests.get(f'{base_url}/api/cuarteles/sucursal-activa', headers=headers)
                print(f'Status Cuarteles: {cuarteles_response.status_code}')
                if cuarteles_response.status_code == 200:
                    result = cuarteles_response.json()
                    cuarteles = result.get('data', {}).get('cuarteles', [])
                    print(f'Total cuarteles disponibles: {len(cuarteles)}')
                    
                    if cuarteles:
                        # Probar con el primer cuartel
                        cuartel_id = cuarteles[0]['id']
                        cuartel_nombre = cuarteles[0]['nombre']
                        print(f'\n--- PROBAR MAPEOS CON CONEO REAL: {cuartel_nombre} (ID: {cuartel_id}) ---')
                        
                        try:
                            mapeos_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/mapeos', headers=headers)
                            print(f'Status Mapeos: {mapeos_response.status_code}')
                            
                            if mapeos_response.status_code == 200:
                                mapeos_result = mapeos_response.json()
                                print('EXITO - Mapeos con conteo real:')
                                print(f'  Total mapeos: {mapeos_result["data"]["total"]}')
                                
                                if mapeos_result["data"]["mapeos"]:
                                    for i, mapeo in enumerate(mapeos_result["data"]["mapeos"][:3]):
                                        print(f'  Mapeo {i+1}:')
                                        print(f'    ID: {mapeo["id"]}')
                                        print(f'    Fecha: {mapeo["fecha"]}')
                                        print(f'    Plantas Tipo 7: {mapeo["plantas_7"]}')
                                        print(f'    Plantas Tipo 5: {mapeo["plantas_5"]}')
                                        print(f'    Plantas Tipo 3: {mapeo["plantas_3"]}')
                                        print(f'    Usuario: {mapeo["usuario"]}')
                                        print()
                                else:
                                    print('  No hay mapeos disponibles para este cuartel')
                            else:
                                print(f'ERROR Mapeos: {mapeos_response.text}')
                        except Exception as e:
                            print(f'ERROR Mapeos: {e}')
                    else:
                        print('No hay cuarteles disponibles')
                else:
                    print(f'Error Cuarteles: {cuarteles_response.text}')
            except Exception as e:
                print(f'Error Cuarteles: {e}')
                
        else:
            print('No se obtuvo token')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')

print('\n=== RESUMEN ===')
print('Prueba del conteo real de plantas por tipo completada.')
print('El endpoint ahora debe mostrar el conteo real de plantas según su tipo.')
