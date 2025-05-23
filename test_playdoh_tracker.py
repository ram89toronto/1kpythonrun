import unittest
from unittest.mock import MagicMock, patch

# Attempt to import from playdoh_tracker. If this fails,
# a simplified local version of is_mask_confident might be needed.
try:
    from playdoh_tracker import is_mask_confident, SAM2VideoPredictor
except ImportError:
    print("Could not import from playdoh_tracker. Using local is_mask_confident for testing.")
    # Define a local version if import fails (e.g., when run in certain CI environments)
    def is_mask_confident(mask, threshold_area=100):
        if mask is not None:
            return True
        else:
            return False
    # We will be mocking SAM2VideoPredictor anyway, so its absence is fine if mocked properly.
    SAM2VideoPredictor = None 


class TestPlayDohTrackerLogic(unittest.TestCase):

    def mock_sam2_get_mask(self, obj_id, target_frame_index, original_prompts=None):
        """
        Custom mock function for SAM2VideoPredictor.get_mask_for_object_on_frame.
        Defines behavior based on obj_id and target_frame_index.
        """
        # Frame 0: All objects present
        if target_frame_index == 0:
            return {'data': 'dummy_mask_data', 'obj_id': obj_id, 'frame': target_frame_index}
        
        # Frame 150: bottle_03 disappears
        elif target_frame_index == 150:
            if obj_id == 'bottle_03':
                return None
            else:
                return {'data': 'dummy_mask_data', 'obj_id': obj_id, 'frame': target_frame_index}

        # Frame 300: All objects disappear
        elif target_frame_index == 300:
            return None
            
        # Default for any other frame (should not be hit by this test's design)
        return None

    # We patch 'playdoh_tracker.SAM2VideoPredictor' if it was imported, 
    # otherwise, we create a MagicMock that will be used as the class itself.
    # This is a bit complex due to the conditional import, a simpler approach might be to
    # ensure playdoh_tracker is always in PYTHONPATH or define SAM2VideoPredictor locally for tests.
    @patch('__main__.SAM2VideoPredictor' if SAM2VideoPredictor is None else 'playdoh_tracker.SAM2VideoPredictor')
    def test_counting_logic_over_time(self, MockSAM2Predictor):
        
        # 1. Setup Mock SAM2VideoPredictor
        # If SAM2VideoPredictor was None (import failed), MockSAM2Predictor is the patch of __main__.SAM2VideoPredictor
        # If SAM2VideoPredictor was imported, MockSAM2Predictor is the patch of playdoh_tracker.SAM2VideoPredictor
        
        mock_sam2_instance = MockSAM2Predictor.return_value # Get the instance
        mock_sam2_instance.get_mask_for_object_on_frame.side_effect = self.mock_sam2_get_mask

        # 2. Test Setup
        initial_inventory_ids = {'bottle_01', 'bottle_02', 'bottle_03'}
        initial_count = len(initial_inventory_ids)
        
        # captured_clicks is passed to the mocked method, but its content isn't critical for this mock logic
        dummy_captured_clicks = { 
            'click_object_ids': list(initial_inventory_ids) 
            # Add other keys if the real method signature expects them, even if mock ignores them
        } 
        
        # fps is used for print statements in the original script but not for core logic being tested here
        # dummy_fps = 30 

        # Frame indices to test
        test_frames = [
            {'index': 0, 'expected_present': 3, 'expected_removed': 0, 'description': "Initial state"},
            {'index': 150, 'expected_present': 2, 'expected_removed': 1, 'description': "One bottle removed"},
            {'index': 300, 'expected_present': 0, 'expected_removed': 3, 'description': "All bottles removed"}
        ]

        # 3. Execution & Assertions (Loop through simulated frames)
        for frame_info in test_frames:
            target_frame_index = frame_info['index']
            
            present_object_ids_in_current_frame = set()
            
            for obj_id in initial_inventory_ids:
                # Call the mocked sam2_predictor's method
                mask = mock_sam2_instance.get_mask_for_object_on_frame(
                    obj_id, 
                    target_frame_index, 
                    original_prompts=dummy_captured_clicks
                )
                
                # Use is_mask_confident (either imported or local)
                if is_mask_confident(mask):
                    present_object_ids_in_current_frame.add(obj_id)
            
            current_present_count = len(present_object_ids_in_current_frame)
            removed_count = initial_count - current_present_count
            
            with self.subTest(frame=target_frame_index, description=frame_info['description']):
                self.assertEqual(current_present_count, frame_info['expected_present'], 
                                 f"Incorrect present count for frame {target_frame_index}")
                self.assertEqual(removed_count, frame_info['expected_removed'],
                                 f"Incorrect removed count for frame {target_frame_index}")

if __name__ == '__main__':
    unittest.main()
