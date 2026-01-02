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
            
            # Probar con cuartel específico
            cuartel_id = 1020200501
            print(f'\n--- PROBAR CONEO REAL: CUARTEL {cuartel_id} ---')
            
            try:
                mapeos_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/mapeos', headers=headers)
                print(f'Status Mapeos: {mapeos_response.status_code}')
                
                if mapeos_response.status_code == 200:
                    mapeos_result = mapeos_response.json()
                    print('EXITO - Conteo real de plantas:')
                    print(f'  Total mapeos: {mapeos_result["data"]["total"]}')
                    
                    if mapeos_result["data"]["mapeos"]:
                        for i, mapeo in enumerate(mapeos_result["data"]["mapeos"]):
                            print(f'\n  Mapeo {i+1}:')
                            print(f'    ID: {mapeo["id"]}')
                            print(f'    Fecha: {mapeo["fecha"]}')
                            print(f'    Plantas Tipo 7: {mapeo["plantas_7"]}')
                            print(f'    Plantas Tipo 5: {mapeo["plantas_5"]}')
                            print(f'    Plantas Tipo 3: {mapeo["plantas_3"]}')
                            print(f'    Total Plantas: {mapeo["total_plantas"]}')
                            print(f'    Usuario: {mapeo["usuario"]}')
                            
                            # Verificar suma
                            suma_tipos = mapeo["plantas_7"] + mapeo["plantas_5"] + mapeo["plantas_3"]
                            print(f'    Suma tipos (7+5+3): {suma_tipos}')
                            if suma_tipos == mapeo["total_plantas"]:
                                print(f'    ✅ Conteo correcto!')
                            else:
                                print(f'    ⚠️ Diferencia en conteo')
                    else:
                        print('  No hay mapeos disponibles para este cuartel')
                else:
                    print(f'ERROR Mapeos: {mapeos_response.text}')
            except Exception as e:
                print(f'ERROR Mapeos: {e}')
                
        else:
            print('No se obtuvo token')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')

print('\n=== RESUMEN ===')
print('Prueba del conteo real de plantas por tipo completada.')
print('El endpoint ahora debe mostrar el conteo real de plantas según su tipo.')
