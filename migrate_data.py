# migrate_data.py
import pickle
import json
import os

def migrate_pickle_to_json():
    """Convert existing pickle data to JSON format"""
    
    # Check if pickle file exists
    pickle_file = 'hotel_data.pkl'
    json_file = 'hotel_data.json'
    
    if not os.path.exists(pickle_file):
        print("No pickle file found. Starting fresh.")
        return
    
    try:
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        
        # Save as JSON
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Successfully migrated {pickle_file} to {json_file}")
        print(f"   - Guests: {len(data.get('guests', {}))}")
        print(f"   - Rooms: {len(data.get('rooms', {}))}")
        print(f"   - Bookings: {len(data.get('bookings', {}))}")
        print(f"   - Payments: {len(data.get('payments', {}))}")
        
        # Backup old pickle file
        backup_file = 'hotel_data.pkl.backup'
        os.rename(pickle_file, backup_file)
        print(f"📦 Old pickle file backed up to {backup_file}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == '__main__':
    migrate_pickle_to_json()