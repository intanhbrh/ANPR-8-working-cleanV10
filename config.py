use_test_video = True  # Set to True to use test video
show_video = True
host_on_IP = True
LIVE_FEED = True  # Set to False for Testing
show_visualization = False  # True = show debug window, False = no visualization

# Slope configurations for predict.py 
LIVE_SLOPES = {
    'inner': ((1300, 0), (0, 927)), # was originally ((1117, 300), (0, 927))
    'middle': ((1900, 1440), (1675, 0)) # was originally ((2023, 1440), (1630, 300))
}
# Modify as per your test video's dimensions
TEST_SLOPES = {
    'inner': ((700, 300), (0, 700)),    # Adjust these values for test video
    'middle': ((1100, 1200), (1200, 300))  # Adjust these values for test video
}

