import time
import streamlit as st

# Switch between local and cloud database
USE_LOCAL_DATABASE = True  # Set to False to use Firestore

if USE_LOCAL_DATABASE:
    from local_database import (
        get_player,
        create_player, 
        update_after_action,
        force_timeout,
        get_leaderboard
    )
else:
    from firestore import (
        get_player,
        create_player,
        update_after_action,
        force_timeout,
        get_leaderboard
    )

from simulation import CarEnvironment

DURATION_SECONDS = 10 * 60
MAX_ATTEMPTS = 15

st.set_page_config(page_title="Mystery Env", page_icon="🎮")

st.title("Mystery Env")

# ------------- LOGIN -------------
user = st.text_input("Ingresa tu usuario:")
if not user:
    st.stop()

player = get_player(user)
if player is None:
    create_player(user, MAX_ATTEMPTS)

player = get_player(user)
start_time = player["start_time"]
elapsed = time.time() - start_time
remaining_time = max(0, DURATION_SECONDS - int(elapsed))

time_expired = elapsed > DURATION_SECONDS
if time_expired:
    force_timeout(user)
    remaining_time = 0

# Initialize environment in session state
if "env" not in st.session_state:
    st.session_state.env = CarEnvironment()

env = st.session_state.env

# Player status
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⏱ Time Left", f"{remaining_time}s")
with col2:
    st.metric("🎯 Attempts Left", player['attempts_left'])
with col3:
    st.metric("🏆 Best Score", player['best_reward'])

# ------------- TABS -------------
tab1, tab2 = st.tabs(["🎮 Environment", "🏆 Leaderboard"])

# Map states to generic labels (global for the session)
state_map = {"cool": "A", "warm": "B", "overheated": "C"}

with tab1:
    # Show time expired warning if needed
    if time_expired:
        st.error("⏰ Se agotó el tiempo (10 minutos). ¡Revisa tu puntuación final en el Leaderboard!")
        st.divider()
    
    # Only show progress, not internal state
    st.subheader("Environment Status")
    
    # Show minimal information - no internal state revealed
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Progress: {env.distance_traveled}/15")
    with col2:
        if env.done:
            if env.distance_traveled >= env.target_distance:
                st.success("✅ Episode Complete")
            else:
                st.error("❌ Episode Terminated")
        else:
            st.info("🎮 Ready for next episode")
    
    # Minimal instructions - let them discover through trial and error
    with st.expander("📋 Instructions"):
        st.write("""
        **Objetivo:** Discover the environment rules through experimentation!
        
        - There are 3 possible states: A, B, C
        - There are 2 possible actions: 1, 2  
        - You'll receive rewards based on your actions
        - Try to maximize your best single episode reward
        - Episodes end when certain conditions are met
        
        **Your task:** Learn the optimal policy through trial and error!
        """)
    
    # Strategy Configuration - use generic labels
    st.subheader("🎯 Policy Configuration")
    st.write("Define your policy - choose action for each state:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**When in State A:**")
        action_a = st.radio("Action for State A:", ["1", "2"], key="state_a")
    
    with col2:
        st.write("**When in State B:**")
        action_b = st.radio("Action for State B:", ["1", "2"], key="state_b")
    
    with col3:
        st.write("**When in State C:**")
        action_c = st.radio("Action for State C:", ["1", "2"], key="state_c")
    
    # Store strategy in session state - map generic actions back to environment actions
    action_map = {"1": "slow", "2": "fast"}
    st.session_state.strategy = {
        "cool": action_map[action_a],
        "warm": action_map[action_b], 
        "overheated": action_map[action_c]
    }
    
    # Game controls
    if player["attempts_left"] > 0 and not time_expired:
        if st.button("▶️ Execute Policy", type="primary"):
            # Reset environment to initial state for new episode
            st.session_state.env = CarEnvironment()
            env = st.session_state.env
            
            # Show simulation progress
            st.subheader("🎬 Running Episode Simulation...")
            
            # Create containers for dynamic updates
            progress_container = st.container()
            step_container = st.container()
            result_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Run complete episode with delays
            episode_steps = []
            total_reward = 0
            step_count = 0
            max_steps = 20
            
            while not env.done and step_count < max_steps:
                current_state = env.current_state
                current_state_label = state_map[current_state]
                action = st.session_state.strategy[current_state]
                action_display = "1" if action == "slow" else "2"
                
                # Update progress
                progress = (step_count + 1) / max_steps
                progress_bar.progress(progress)
                status_text.text(f"Step {step_count + 1}: Taking Action {action_display}...")
                
                # Execute step
                obs, reward, done = env.step(action)
                total_reward += reward
                step_count += 1
                
                episode_steps.append({
                    "step": step_count,
                    "action": action_display,
                    "reward": reward,
                    "progress": obs["distance"]
                })
                
                # Show current step result
                with step_container:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Step", step_count)
                    with col2:
                        st.metric("Action", action_display)
                    with col3:
                        st.metric("Step Reward", reward)
                
                # Add 2-second delay
                if not done:
                    time.sleep(2)
                
                if done:
                    break
            
            # Complete progress bar
            progress_bar.progress(1.0)
            status_text.text("Episode Complete!")
            
            # Check if this is a new best before updating
            current_best = player['best_reward']
            is_new_best = total_reward > current_best
            
            # Update database with episode reward
            update_after_action(user, f"Episode-{step_count}steps", total_reward)
            
            # Display final results
            with result_container:
                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Steps", step_count)
                with col2:
                    if is_new_best:
                        st.metric("Episode Reward", total_reward, delta=f"NEW BEST! (+{total_reward - current_best})")
                    else:
                        st.metric("Episode Reward", total_reward)
                with col3:
                    st.metric("Final Progress", f"{env.distance_traveled}/15")
                
                # Show special celebration for achievements
                if is_new_best:
                    st.balloons()
                    st.success("🎉 NEW BEST SCORE! Outstanding improvement!")
                elif env.distance_traveled >= env.target_distance:
                    st.success("🎯 Goal Reached! Great policy!")
                else:
                    st.info("📈 Keep experimenting to improve your score!")
                
                # Show episode trace (without internal states)
                with st.expander("📈 Episode Trace"):
                    import pandas as pd
                    df = pd.DataFrame(episode_steps)
                    st.dataframe(df, use_container_width=True)
            
            # Auto-refresh after showing results for 3 seconds
            time.sleep(3)
            st.rerun()
    
    elif env.done and not time_expired:
        if env.distance_traveled >= env.target_distance:
            st.success("🎉 Episode Complete! Click 'Reset Environment' to continue learning.")
        else:
            st.error("💥 Episode Terminated! Click 'Reset Environment' to try again.")
        
        if st.button("🔄 Reset Environment"):
            st.session_state.env = CarEnvironment()
            st.rerun()
    
    elif player["attempts_left"] <= 0 and not time_expired:
        st.warning("⚠️ No attempts left!")
        
    elif time_expired:
        st.info("🏁 Tiempo terminado. Tu puntuación final ha sido registrada.")

with tab2:
    st.subheader("🏆 Leaderboard")
    
    # Show final results message if time expired
    if time_expired:
        st.success(f"🏁 ¡Juego terminado! Tu mejor puntuación: **{player['best_reward']}** puntos")
        st.divider()
    
    # Refresh button
    if st.button("🔄 Refresh Leaderboard"):
        st.rerun()
    
    table = get_leaderboard()
    
    if table:
        # Display as a proper table
        leaderboard_data = []
        current_user_rank = None
        
        for i, row in enumerate(table[:10], 1):  # Top 10
            is_current_user = row['username'] == user
            if is_current_user:
                current_user_rank = i
            
            leaderboard_data.append({
                "Rank": f"#{i}",
                "Username": f"👤 {row['username']}" if is_current_user else row['username'],
                "Best Score": row['best_reward'],
                "Attempts Left": row['attempts_left']
            })
        
        st.dataframe(leaderboard_data, use_container_width=True)
        
        # Show user's position if they're in top 10
        if current_user_rank and time_expired:
            if current_user_rank == 1:
                st.success(f"🥇 ¡Felicitaciones! Estás en primer lugar")
            elif current_user_rank <= 3:
                st.success(f"🏆 ¡Excelente! Estás en el puesto #{current_user_rank}")
            else:
                st.info(f"📊 Tu posición actual: #{current_user_rank}")
    else:
        st.info("No players yet. Be the first to play!")