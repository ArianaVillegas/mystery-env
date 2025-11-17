import sqlite3
import json
import time
from pathlib import Path

# Database file path
DB_FILE = Path("mystery_env.db")

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if we need to migrate from old schema
    cursor.execute("PRAGMA table_info(players)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'total_reward' in column_names and 'best_reward' not in column_names:
        # Migration: rename total_reward to best_reward
        cursor.execute('ALTER TABLE players RENAME COLUMN total_reward TO best_reward')
        print("🔄 Migrated database from total_reward to best_reward")
    
    # Create players table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            start_time REAL,
            attempts_left INTEGER,
            best_reward INTEGER,
            history TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_player(user):
    """Get player data from database"""
    init_database()  # Ensure database exists
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM players WHERE username = ?', (user,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            'username': row[0],
            'start_time': row[1],
            'attempts_left': row[2],
            'best_reward': row[3],
            'history': json.loads(row[4]) if row[4] else []
        }
    return None

def create_player(user, max_attempts):
    """Create a new player in database"""
    init_database()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO players 
        (username, start_time, attempts_left, best_reward, history)
        VALUES (?, ?, ?, ?, ?)
    ''', (user, time.time(), max_attempts, -999, json.dumps([])))
    
    conn.commit()
    conn.close()

def update_after_action(user, action, reward):
    """Update player after an action - track best reward instead of cumulative"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get current player data
    cursor.execute('SELECT attempts_left, best_reward, history FROM players WHERE username = ?', (user,))
    row = cursor.fetchone()
    
    if row:
        current_attempts, current_best, current_history = row
        history = json.loads(current_history) if current_history else []
        
        # Update values
        new_attempts = max(0, current_attempts - 1)
        # Only update best reward if this episode's reward is better
        new_best = max(current_best, reward)
        history.append({
            "action": action,
            "reward": reward,
            "timestamp": time.time(),
            "is_new_best": reward > current_best
        })
        
        # Update database
        cursor.execute('''
            UPDATE players 
            SET attempts_left = ?, best_reward = ?, history = ?
            WHERE username = ?
        ''', (new_attempts, new_best, json.dumps(history), user))
    
    conn.commit()
    conn.close()

def force_timeout(user):
    """Force timeout for a user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE players SET attempts_left = 0 WHERE username = ?', (user,))
    
    conn.commit()
    conn.close()

def get_leaderboard():
    """Get leaderboard sorted by best reward"""
    init_database()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, best_reward, attempts_left
        FROM players 
        ORDER BY best_reward DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'username': row[0],
            'best_reward': row[1],
            'attempts_left': row[2]
        }
        for row in rows
    ]

def clear_database():
    """Clear all data from database (useful for testing)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM players')
    conn.commit()
    conn.close()

# Test function
if __name__ == "__main__":
    print("Testing local database...")
    
    # Test creating a player
    create_player("test_user", 10)
    player = get_player("test_user")
    print(f"Created player: {player}")
    
    # Test updating after action
    update_after_action("test_user", "test_action", 5)
    player = get_player("test_user")
    print(f"After action: {player}")
    
    # Test leaderboard
    leaderboard = get_leaderboard()
    print(f"Leaderboard: {leaderboard}")
    
    print("✅ Local database test completed!")
