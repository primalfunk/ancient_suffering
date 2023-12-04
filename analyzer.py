import json

def analyze_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if 'locations' in data:
        print(f"Total Locations: {len(data['locations'])}")
        analyze_structure(data['locations'], 0)
        print_sorted_locations(data['locations'])
    else:
        analyze_structure(data, 0)

def analyze_structure(data, level):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                # For lists, only print the count
                print('  ' * level + f"{key}: List Count: {len(value)}")
            else:
                print('  ' * level + f"{key}:")
                analyze_structure(value, level + 1)
    elif isinstance(data, list):
        # Just print the count of items in the list
        print('  ' * level + f"List Count: {len(data)}")
    else:
        # Print other data types
        print('  ' * level + str(data))

def print_sorted_locations(locations):
    sorted_locations = sorted(locations.items(), key=lambda x: x[1]['total_zones'], reverse=True)
    print("\nLocations sorted by total_zones (descending):")
    for location, details in sorted_locations:
        print(f"{location}: {details['total_zones']} zones")

# Example usage
file_path = 'words.json'
analyze_json(file_path)