import csv

def read_destinations(filepath="destinos.txt"):
    """
    Lee los datos de los destinos desde un archivo CSV.
    Retorna un diccionario donde la clave es el código del aeropuerto
    y el valor es un diccionario con 'nombre' y 'requiere_visa'.
    """
    destinations_data = {}
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 3:
                    code, name, visa_status = row
                    requires_visa = (visa_status.strip().lower() == "requiere visa")
                    destinations_data[code.strip()] = {
                        'name': name.strip(),
                        'requiere_visa': requires_visa
                    }
    except FileNotFoundError:
        print(f"Error: El archivo '{filepath}' no se encontró. Asegúrate de que esté en el mismo directorio.")
        return None 
    return destinations_data

def read_fares(filepath="tarifas.txt"):
    """
    Lee los datos de las tarifas desde un archivo CSV.
    Retorna una lista de diccionarios, donde cada diccionario representa un vuelo.
    """
    fares_data = []
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 3:
                    origin, destination, price_str = row
                    try:
                        price = float(price_str.strip().replace('$', '').replace(',', ''))
                        fares_data.append({
                            'origin': origin.strip(),
                            'destination': destination.strip(),
                            'price': price
                        })
                    except ValueError:
                        print(f"Advertencia: No se pudo parsear el precio '{price_str}' en la fila: {row}")
    except FileNotFoundError:
        print(f"Error: El archivo '{filepath}' no se encontró. Asegúrate de que esté en el mismo directorio.")
        return None
    return fares_data