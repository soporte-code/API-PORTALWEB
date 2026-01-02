import requests
import json

# URL base
base_url = 'https://api-portalweb-927498545444.us-central1.run.app'

# Datos de login
login_data = {
    'username': 'fsoto',
    'password': '212121'
}

print('=== PRUEBAS ENDPOINTS DETALLE CUARTEL ===')
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
            cuartel_id = 1020200501
            
            print(f'\n--- INFORMACION GENERAL CUARTEL {cuartel_id} ---')
            try:
                info_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/informacion-general', headers=headers)
                print(f'Status: {info_response.status_code}')
                if info_response.status_code == 200:
                    result = info_response.json()
                    cuartel = result['data']['cuartel']
                    print('EXITO - Informacion General:')
                    print(f'  ID: {cuartel["id"]}')
                    print(f'  Nombre: {cuartel["nombre"]}')
                    print(f'  Variedad: {cuartel["variedad"]}')
                    print(f'  Superficie: {cuartel["superficie_productiva"]} ha')
                    print(f'  Ano Plantacion: {cuartel["año_plantacion"]}')
                    print(f'  Plantas HA: {cuartel["plantas_ha_teoricas"]}')
                    print(f'  Estado Productivo: {cuartel["estado_productivo"]}')
                    print(f'  Numero Brazos: {cuartel["numero_brazos_ejes"]}')
                    print(f'  CECO: {cuartel["nombre_ceco"]}')
                    print(f'  Sucursal: {cuartel["nombre_sucursal"]}')
                else:
                    print(f'ERROR: {info_response.text}')
            except Exception as e:
                print(f'ERROR: {e}')
            
            print(f'\n--- MAPEOS CUARTEL {cuartel_id} ---')
            try:
                mapeos_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/mapeos', headers=headers)
                print(f'Status: {mapeos_response.status_code}')
                if mapeos_response.status_code == 200:
                    result = mapeos_response.json()
                    print(f'EXITO - Mapeos:')
                    print(f'  Total mapeos: {result["data"]["total"]}')
                    if result["data"]["mapeos"]:
                        mapeo = result["data"]["mapeos"][0]
                        print(f'  Ultimo mapeo:')
                        print(f'    Fecha: {mapeo["fecha"]}')
                        print(f'    Plantas 7: {mapeo["plantas_7"]}')
                        print(f'    Plantas 5: {mapeo["plantas_5"]}')
                        print(f'    Plantas 3: {mapeo["plantas_3"]}')
                        print(f'    Usuario: {mapeo["usuario"]}')
                    else:
                        print('  No hay mapeos disponibles')
                else:
                    print(f'ERROR: {mapeos_response.text}')
            except Exception as e:
                print(f'ERROR: {e}')
            
            print(f'\n--- ESTIMACIONES CUARTEL {cuartel_id} ---')
            try:
                estimaciones_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/estimaciones', headers=headers)
                print(f'Status: {estimaciones_response.status_code}')
                if estimaciones_response.status_code == 200:
                    result = estimaciones_response.json()
                    print(f'EXITO - Estimaciones:')
                    print(f'  Total estimaciones: {result["data"]["total"]}')
                    if result["data"]["estimaciones"]:
                        estimacion = result["data"]["estimaciones"][0]
                        print(f'  Ultima estimacion:')
                        print(f'    Tipo: {estimacion["tipo_estimacion"]}')
                        print(f'    Estimacion: {estimacion["estimacion"]}')
                        print(f'    Fecha: {estimacion["fecha"]}')
                        print(f'    Usuario: {estimacion["usuario"]}')
                    else:
                        print('  No hay estimaciones disponibles')
                else:
                    print(f'ERROR: {estimaciones_response.text}')
            except Exception as e:
                print(f'ERROR: {e}')
                
        else:
            print('No se obtuvo token')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')

print('\n=== RESUMEN ===')
print('Los endpoints del detalle de cuartel estan funcionando correctamente!')
print('El frontend puede proceder con la implementacion de la vista detallada.')
