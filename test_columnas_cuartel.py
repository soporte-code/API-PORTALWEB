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
            
            print(f'\n=== VERIFICAR COLUMNAS DE TABLAS ===')
            
            # Crear un endpoint temporal para verificar columnas
            debug_data = {
                'tabla': 'general_dim_cuartel',
                'columnas_buscadas': ['plantas_ha_teoricas', 'plantas_teoricas_ha', 'plantas_ha', 'plantas_por_ha', 'n_plantas', 'plantas']
            }
            
            print(f'Verificando columnas de general_dim_cuartel...')
            try:
                # Usar endpoint de debug si existe, sino crear uno temporal
                debug_response = requests.post(f'{base_url}/api/pautas/debug-tablas', json=debug_data, headers=headers)
                print(f'Status Debug: {debug_response.status_code}')
                if debug_response.status_code == 200:
                    print(f'Debug Response: {json.dumps(debug_response.json(), indent=2, ensure_ascii=False)}')
                else:
                    print(f'Debug Error: {debug_response.text}')
            except Exception as e:
                print(f'Error Debug: {e}')
            
            print(f'\n=== PROBAR INFORMACIÓN GENERAL CON COLUMNAS ALTERNATIVAS ===')
            # Probar con diferentes nombres de columnas
            columnas_plantas = ['plantas_ha_teoricas', 'plantas_teoricas_ha', 'plantas_ha', 'plantas_por_ha', 'n_plantas', 'plantas', 'plantas_por_hectarea']
            
            for col in columnas_plantas:
                print(f'\nProbando columna: {col}')
                try:
                    # Crear query manual para probar
                    test_query = f"""
                        SELECT 
                            c.id,
                            c.nombre,
                            c.{col} as plantas_ha_teoricas
                        FROM general_dim_cuartel c
                        WHERE c.id = {cuartel_id}
                        LIMIT 1
                    """
                    print(f'Query: {test_query}')
                except Exception as e:
                    print(f'Error con columna {col}: {e}')
                
        else:
            print('No se encontró token en la respuesta')
    else:
        print(f'Error Login: {login_response.text}')
        
except Exception as e:
    print(f'Error general: {e}')
