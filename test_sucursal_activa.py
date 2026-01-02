import requests
import json

# URL base
base_url = 'https://api-portalweb-927498545444.us-central1.run.app'

# Datos de login
login_data = {
    'username': 'fsoto',
    'password': '212121'
}

print('=== VERIFICAR FILTRADO POR SUCURSAL ACTIVA ===')
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
            
            # Obtener información del usuario
            print(f'\n--- INFORMACION DEL USUARIO ---')
            try:
                me_response = requests.get(f'{base_url}/api/auth/me', headers=headers)
                print(f'Status Me: {me_response.status_code}')
                if me_response.status_code == 200:
                    me_result = me_response.json()
                    print(f'Usuario: {me_result.get("usuario")}')
                    print(f'Sucursal Activa: {me_result.get("sucursal_nombre")} (ID: {me_result.get("id_sucursal")})')
                else:
                    print(f'Error Me: {me_response.text}')
            except Exception as e:
                print(f'Error Me: {e}')
            
            # Obtener cuarteles de la sucursal activa
            print(f'\n--- CUARTELES SUCURSAL ACTIVA ---')
            try:
                cuarteles_response = requests.get(f'{base_url}/api/cuarteles/sucursal-activa', headers=headers)
                print(f'Status Cuarteles: {cuarteles_response.status_code}')
                if cuarteles_response.status_code == 200:
                    result = cuarteles_response.json()
                    cuarteles = result.get('data', {}).get('cuarteles', [])
                    print(f'Total cuarteles en sucursal activa: {len(cuarteles)}')
                    if cuarteles:
                        print('Primeros 3 cuarteles:')
                        for i, cuartel in enumerate(cuarteles[:3]):
                            print(f'  {i+1}. {cuartel["nombre"]} (ID: {cuartel["id"]})')
                else:
                    print(f'Error Cuarteles: {cuarteles_response.text}')
            except Exception as e:
                print(f'Error Cuarteles: {e}')
            
            # Probar endpoint detalle con cuartel de la sucursal activa
            print(f'\n--- PROBAR DETALLE CON CUARTEL DE SUCURSAL ACTIVA ---')
            try:
                # Usar el primer cuartel de la sucursal activa
                cuarteles_response = requests.get(f'{base_url}/api/cuarteles/sucursal-activa', headers=headers)
                if cuarteles_response.status_code == 200:
                    result = cuarteles_response.json()
                    cuarteles = result.get('data', {}).get('cuarteles', [])
                    if cuarteles:
                        cuartel_id = cuarteles[0]['id']
                        print(f'Probando con cuartel: {cuarteles[0]["nombre"]} (ID: {cuartel_id})')
                        
                        # Probar información general
                        info_response = requests.get(f'{base_url}/api/estimaciones/cuartel/{cuartel_id}/informacion-general', headers=headers)
                        print(f'Status Info: {info_response.status_code}')
                        if info_response.status_code == 200:
                            info_result = info_response.json()
                            cuartel_info = info_result['data']['cuartel']
                            print(f'EXITO - Informacion General:')
                            print(f'  Nombre: {cuartel_info["nombre"]}')
                            print(f'  Sucursal: {cuartel_info["nombre_sucursal"]}')
                        else:
                            print(f'ERROR Info: {info_response.text}')
                    else:
                        print('No hay cuarteles en la sucursal activa')
                else:
                    print('No se pudieron obtener cuarteles')
            except Exception as e:
                print(f'Error Detalle: {e}')
                
        else:
            print('No se obtuvo token')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')

print('\n=== RESUMEN ===')
print('Verificacion de filtrado por sucursal activa completada.')
print('Los endpoints ahora deben mostrar solo cuarteles de la sucursal activa del usuario.')
