import streamlit as st
from playdoh_tracker import process_video_for_tracking
# sample_captured_clicks is not globally defined in playdoh_tracker.py,
# so we define it here for the simulation.
sample_captured_clicks = {
    'click_coordinates': [[10,10],[12,12], [50,50], [100,100], [105,105]],
    'click_labels': [1, 1, 1, 1, 1], # 1 for positive click
    'click_frames': [0, 0, 0, 0, 0], # All clicks on the first frame
    'click_object_ids': ['bottle_01', 'bottle_01', 'bottle_02', 'bottle_03', 'bottle_03']
}

# --- Page Configuration (Optional, but good practice) ---
st.set_page_config(
    page_title="Play-Doh Inventory Tracker",
    layout="wide"
)

# --- Main Application ---
st.title("Play-Doh Inventory Tracker")

st.sidebar.header("Controls")

# Placeholder for video upload
uploaded_file = st.sidebar.file_uploader("Upload an inventory video (simulated)", type=["mp4", "mov", "avi"])

# Button to start processing
start_button = st.sidebar.button("Start Tracking Inventory")

st.sidebar.markdown("---") # Separator

# --- Display Area for Counts ---
st.header("Live Inventory Count")

col1, col2 = st.columns(2)
present_count_placeholder = col1.empty()
removed_count_placeholder = col2.empty()

# Initialize placeholders
present_count_placeholder.metric("Bottles Present", "N/A")
removed_count_placeholder.metric("Bottles Removed (since start)", "N/A")

# Placeholder for detailed log or status messages
st.subheader("Processing Log")
log_placeholder = st.empty()
log_placeholder.text("Awaiting video processing to start...")

# --- Button Logic ---
if start_button:
    log_placeholder.text("Starting video processing...")
    
    # In a real app, this path would come from the uploaded_file
    # For now, playdoh_tracker.py itself uses a dummy path internally when it receives one.
    dummy_video_path = "dummy_inventory_video.mp4" 
    
    # Use the locally defined sample_captured_clicks
    simulated_clicks_data = sample_captured_clicks 
    
    log_messages = ["Processing started..."]
    log_placeholder.text("\n".join(log_messages)) # Initial log message

    # Call process_video_for_tracking and iterate through its yielded results
    for result in process_video_for_tracking(
        video_path=dummy_video_path, 
        captured_clicks_data=simulated_clicks_data, # Corrected parameter name
        check_interval_seconds=3 # Using the default from playdoh_tracker or can be explicit
    ):
        if result.get('type') == 'initial_summary':
            initial_total_count = result.get('initial_total_count', 'N/A')
            log_messages.append(f"Initial total count: {initial_total_count} items being tracked.")
            log_messages.append(f"Object IDs: {result.get('initial_inventory_ids', 'N/A')}")
            log_messages.append(f"Video Info: FPS={result.get('fps', 'N/A')}, Total Frames={result.get('total_frames', 'N/A')}")
            log_messages.append("--- Starting Periodic Tracking Updates ---")
            
            present_count_placeholder.metric("Bottles Present", str(initial_total_count)) # Start with all present
            removed_count_placeholder.metric("Bottles Removed (since start)", "0")

        elif result.get('type') == 'tracking_update':
            present_count = result.get('present_count', 'N/A')
            removed_count = result.get('removed_count', 'N/A')
            time_seconds = result.get('time_seconds', 0)
            present_ids = result.get('present_ids', set())

            # Update metric placeholders
            present_count_placeholder.metric("Bottles Present", str(present_count))
            removed_count_placeholder.metric("Bottles Removed (since start)", str(removed_count))

            # Update log
            log_msg = f"Time: {time_seconds:.2f}s (Frame: {result.get('frame_index', 'N/A')}) - Present: {present_count} (IDs: {present_ids}), Removed: {removed_count}"
            log_messages.append(log_msg)
        
        # Update log display (showing last 10 messages for brevity)
        log_placeholder.text("\n".join(log_messages[-10:]))

    log_messages.append("Processing complete.")
    log_placeholder.text("\n".join(log_messages[-10:]))

if __name__ == '__main__':
    # Streamlit apps are typically run from top to bottom on every interaction.
    # The main logic is triggered by the 'start_button' state.
    pass
