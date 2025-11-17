#!/usr/bin/env python3
"""
Demo script to test the local database and simulation
"""

from local_database import *
from simulation import CarEnvironment

def demo_database():
    """Test the local database functionality"""
    print("🗄️ Testing Local Database...")
    
    # Clear any existing data
    clear_database()
    
    # Create test players
    create_player("alice", 10)
    create_player("bob", 10)
    
    # Simulate some actions
    update_after_action("alice", "Episode-5steps", 15)
    update_after_action("bob", "Episode-7steps", -5)
    update_after_action("alice", "Episode-3steps", 8)
    
    # Check leaderboard
    leaderboard = get_leaderboard()
    print("📊 Current Leaderboard:")
    for i, player in enumerate(leaderboard, 1):
        print(f"  {i}. {player['username']}: {player['total_reward']} points")
    
    print("✅ Database test completed!\n")

def demo_simulation():
    """Test the car simulation with different policies"""
    print("🚗 Testing Car Simulation...")
    
    # Test conservative policy
    env = CarEnvironment()
    print(f"Initial state: {env.current_state}, Distance: {env.distance_traveled}")
    
    policy = {"cool": "slow", "warm": "slow", "overheated": "slow"}
    total_reward = 0
    step = 0
    
    print("Testing Conservative Policy (all slow):")
    while not env.done and step < 20:
        action = policy[env.current_state]
        obs, reward, done = env.step(action)
        total_reward += reward
        step += 1
        print(f"  Step {step}: Action={action}, Reward={reward}, Progress={obs['distance']}")
    
    print(f"Final result: {total_reward} total reward, reached {env.distance_traveled}/15")
    print("✅ Simulation test completed!\n")

if __name__ == "__main__":
    demo_database()
    demo_simulation()
