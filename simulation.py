import random

class CarEnvironment:
    def __init__(self, target_distance=15):
        self.states = ["cool", "warm", "overheated"]
        self.actions = ["slow", "fast"]
        self.target_distance = target_distance
        
        # Configurable transition probabilities
        # Format: {state: {action: [(next_state, probability), ...]}}
        self.transition_probs = {
            "cool": {
                "slow": [("cool", 1.0)],
                "fast": [("cool", 0.5), ("warm", 0.5)]
            },
            "warm": {
                "slow": [("cool", 0.5), ("warm", 0.5)],
                "fast": [("warm", 0.5), ("overheated", 0.5)]
            },
            "overheated": {
                "slow": [("overheated", 1.0)],
                "fast": [("overheated", 1.0)]
            }
        }
        
        self.reset()
    
    def reset(self):
        """Reset the environment to initial state"""
        self.current_state = "cool"
        self.distance_traveled = 0
        self.done = False
        return self.get_observation()
    
    def get_observation(self):
        """Get current observation"""
        return {
            "state": self.current_state,
            "distance": self.distance_traveled,
            "remaining": self.target_distance - self.distance_traveled,
            "done": self.done
        }
    
    def step(self, action):
        """Execute one step in the environment"""
        if self.done:
            return self.get_observation(), 0, self.done
        
        # Move based on action
        if action == "slow":
            distance_gain = 1
        elif action == "fast":
            distance_gain = 2
        else:
            raise ValueError(f"Invalid action: {action}. Must be 'slow' or 'fast'")
        
        self.distance_traveled += distance_gain
        
        # State transition first (before calculating reward based on new state)
        if not self.done:
            self.current_state = self._transition_state(self.current_state, action)
        
        # Calculate reward
        if self.distance_traveled >= self.target_distance:
            reward = 10  # Reached the goal
            self.done = True
        elif self.current_state == "overheated":
            reward = -10 
            self.done = True
        else:
            reward = -1  # Step penalty
        
        return self.get_observation(), reward, self.done
    
    def _transition_state(self, current_state, action):
        """Handle state transitions based on probabilities"""
        transitions = self.transition_probs[current_state][action]
        
        # Generate random number and select next state based on probabilities
        rand = random.random()
        cumulative_prob = 0
        
        for next_state, prob in transitions:
            cumulative_prob += prob
            if rand < cumulative_prob:
                return next_state
        
        # Fallback (shouldn't happen if probabilities sum to 1)
        return transitions[-1][0]
    
    def set_transition_probabilities(self, new_probs):
        """Update transition probabilities
        
        Args:
            new_probs: Dictionary in format {state: {action: [(next_state, probability), ...]}}
        """
        # Validate probabilities sum to 1
        for state, actions in new_probs.items():
            for action, transitions in actions.items():
                total_prob = sum(prob for _, prob in transitions)
                if abs(total_prob - 1.0) > 1e-6:
                    raise ValueError(f"Probabilities for {state}-{action} sum to {total_prob}, not 1.0")
        
        self.transition_probs = new_probs

def simulate_step(player, action):
    """
    Legacy function for compatibility.
    Creates a car environment and simulates one step.
    """
    if "env" not in player:
        player["env"] = CarEnvironment()
    
    env = player["env"]
    
    # Convert numeric actions to string actions for compatibility
    action_map = {1: "slow", 2: "fast"}
    if isinstance(action, int) and action in action_map:
        action = action_map[action]
    
    obs, reward, done = env.step(action)
    
    # Store in history
    if "history" not in player:
        player["history"] = []
    
    player["history"].append({
        "state": obs["state"],
        "distance": obs["distance"],
        "action": action,
        "reward": reward,
        "done": done
    })
    
    return reward
