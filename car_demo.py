from simulation import CarEnvironment
import random

def demo_car_simulation():
    """Demonstrate the car environment simulation"""
    print("=== Car Environment Demo ===")
    
    # Create environment
    env = CarEnvironment(target_distance=15)
    
    print(f"Goal: Reach {env.target_distance}km")
    print("States: cool, warm, overheated")
    print("Actions: slow (+1km), fast (+2km)")
    print("Rewards: +10 at goal, -10 when overheated, -1 per step\n")
    
    # Run simulation
    obs = env.reset()
    total_reward = 0
    step = 0
    
    print("Step | State      | Distance | Action | Reward | Total")
    print("-" * 55)
    
    while not obs["done"]:
        step += 1
        
        # Choose random action for demo
        action = random.choice(["slow", "fast"])
        
        obs, reward, done = env.step(action)
        total_reward += reward
        
        print(f"{step:4d} | {obs['state']:10s} | {obs['distance']:8d} | {action:6s} | {reward:6d} | {total_reward:5d}")
        
        # Safety break
        if step > 20:
            print("Demo stopped after 20 steps")
            break
    
    if obs["done"] and obs["distance"] >= env.target_distance:
        print(f"\n🎉 Goal reached! Total reward: {total_reward}")
    else:
        print(f"\n❌ Goal not reached. Distance: {obs['distance']}")

def demo_custom_probabilities():
    """Demonstrate configurable probabilities"""
    print("\n=== Custom Probabilities Demo ===")
    
    env = CarEnvironment()
    
    # Custom probabilities - make fast action less risky from cool state
    custom_probs = {
        "cool": {
            "slow": [("cool", 1.0)],
            "fast": [("warm", 0.8), ("overheated", 0.2)]  # Less chance of overheating
        },
        "warm": {
            "slow": [("cool", 0.7), ("warm", 0.3)],  # Higher chance to cool down
            "fast": [("overheated", 1.0)]
        },
        "overheated": {
            "slow": [("warm", 0.3), ("overheated", 0.7)],  # Chance to recover
            "fast": [("overheated", 1.0)]
        }
    }
    
    env.set_transition_probabilities(custom_probs)
    print("Updated transition probabilities:")
    print("- Cool -> Fast: 80% warm, 20% overheated (was 50/50)")
    print("- Warm -> Slow: 70% cool, 30% warm (was 50/50)")
    print("- Overheated -> Slow: 30% warm, 70% overheated (was 100% overheated)")

if __name__ == "__main__":
    demo_car_simulation()
    demo_custom_probabilities()
