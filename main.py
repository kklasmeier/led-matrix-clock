# main.py - Main application entry point with frame-based scrolling

import sys
import time
import signal
from typing import Dict, Any

from config import UpdateIntervals
from data.data_manager import get_data_manager
from display.matrix import get_matrix_display, cleanup_matrix
from display.renderer import get_display_renderer
from utils.process_lock import get_process_lock

class LEDClock:
    """Main LED Clock application with threaded data management"""
    
    def __init__(self):
        self.running = False
        self.data_manager = get_data_manager()
        self.matrix_display = get_matrix_display()
        self.renderer = get_display_renderer()
        
        # Track last rendered state to minimize unnecessary redraws
        self.last_rendered_time = ""
        self.last_weather_data = None
        self.last_stock_data = None
        self.last_news_data = None
        
        # Frame-based scroll timing
        self.frame_count = 0
        self.scroll_every_n_frames = 4  # Scroll every frame for maximum speed
                                        # Set to 2 for half speed, 3 for third speed, etc.
        
        print("LED Clock initialized successfully")
        print(f"Scroll configuration: Every {self.scroll_every_n_frames} frame(s)")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False
    
    def should_update_display(self, time_data: Dict[str, Any], 
                            weather_data: Dict[str, Any], 
                            stock_data: Dict[str, Any],
                            news_data: Dict[str, Any],
                            should_scroll: bool = False) -> bool:
        """
        Determine if the display needs updating
        
        Args:
            time_data: Current time data
            weather_data: Current weather data (always valid dict)
            stock_data: Current stock data (always valid dict)
            news_data: Current news data (always valid dict)
            should_scroll: True if this frame should scroll headlines
            
        Returns:
            bool: True if display should be updated
        """
        # Always update for scrolling animation
        if should_scroll:
            return True
            
        # Always update if time string has changed
        current_time_str = time_data.get('time', '')
        if current_time_str != self.last_rendered_time:
            return True
        
        # Update if weather data has changed (compare dict contents)
        if weather_data != self.last_weather_data:
            return True
            
        # Update if stock data has changed (compare dict contents)
        if stock_data != self.last_stock_data:
            return True
        
        # Update if news data has changed (compare dict contents)
        if news_data != self.last_news_data:
            return True
        
        return False
    
    def update_display(self, time_data: Dict[str, Any], 
                      weather_data: Dict[str, Any], 
                      stock_data: Dict[str, Any],
                      news_data: Dict[str, Any]) -> None:
        """
        Update the LED matrix display
        
        Args:
            time_data: Time data to display
            weather_data: Weather data to display (always valid dict)
            stock_data: Stock data to display (always valid dict)
            news_data: News data to display (always valid dict)
        """
        try:
            # Get current canvas
            canvas = self.matrix_display.get_canvas()
            
            # Render the frame with all data (including news)
            self.renderer.render_frame(canvas, time_data, weather_data, stock_data, news_data)
            
            # Swap canvas to display the new frame
            self.matrix_display.swap_canvas()
            
            # Update tracking variables
            self.last_rendered_time = time_data.get('time', '')
            self.last_weather_data = weather_data
            self.last_stock_data = stock_data
            self.last_news_data = news_data
            
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def run(self) -> None:
        """Main application loop with frame-based scrolling"""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Starting LED Clock...")
        print("Starting background data manager...")
        
        # Start background data fetching
        self.data_manager.start()
        
        print("Press Ctrl+C to stop")
        
        self.running = True
        print(f"DEBUG: self.running set to {self.running}")
        
        # Simple loop counter for debugging
        loop_count = 0
        update_count = 0
        start_time = time.time()
        
        try:
            print(f"DEBUG: Entering main loop at {time.strftime('%H:%M:%S')}")
            while self.running:
                loop_count += 1
                self.frame_count += 1
                # Add to main.py in the main loop every 125 iterations:
                if loop_count % 125 == 0:
                    info = self.renderer.headline_scroller.get_current_headline_info()
                    # print(f"Headlines: {info}")
                                    
                current_time = time.time()
                
                # Get all current data (non-blocking, uses cached data)
                all_data = self.data_manager.get_current_data()
                
                time_data = all_data['time']
                weather_data = all_data['weather']
                stock_data = all_data['stocks']
                news_data = all_data['news']
                
                # Frame-based scroll timing - simple and predictable
                should_scroll = (self.frame_count % self.scroll_every_n_frames == 0)
                
                # Update display if any data has changed or it's time to scroll
                if self.should_update_display(time_data, weather_data, stock_data, news_data, should_scroll):
                    update_count += 1
                    self.update_display(time_data, weather_data, stock_data, news_data)
                    
                    # Log the update (but not every scroll frame)
                    if time_data.get('time', '') != self.last_rendered_time:
                        weather_str = weather_data.get("current_text", "Weather: --") if weather_data else "Weather: --"
                        dow_str = stock_data.get("dow_text", "DOW: --") if stock_data else "DOW: --"
                        news_count = news_data.get("count", 0) if news_data else 0
                        print(f"Display updated: {time_data['time']} {time_data['ampm']} | {weather_str} | {dow_str} | News: {news_count} headlines")
                
                # Performance logging every 125 loops with actual timing
#                if loop_count % 125 == 0:
#                    elapsed = current_time - start_time
#                    actual_fps = loop_count / elapsed if elapsed > 0 else 0
#                    update_rate = (update_count / loop_count) * 100 if loop_count > 0 else 0
#                    scroll_fps = actual_fps * (update_count / loop_count) if loop_count > 0 else 0
#                    print(f"DEBUG [{time.strftime('%H:%M:%S')}]: Loop {loop_count} | Updates: {update_count} ({update_rate:.1f}%) | Elapsed: {elapsed:.1f}s | Actual FPS: {actual_fps:.1f} | Scroll: ~{scroll_fps:.1f} px/s | Running: {self.running}")
                
                # Minimal sleep to prevent CPU spinning
                time.sleep(0.003)
                
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            total_elapsed = time.time() - start_time
            actual_fps = loop_count / total_elapsed if total_elapsed > 0 else 0
            print(f"DEBUG: Exiting at {time.strftime('%H:%M:%S')} - Loops: {loop_count}, Updates: {update_count}, Total time: {total_elapsed:.1f}s, Actual FPS: {actual_fps:.1f}")
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        print("Cleaning up...")
        
        # Stop background threads
        self.data_manager.stop()
        
        # Clean up display
        cleanup_matrix()
        
        print("LED Clock stopped")

def main():
    """Entry point for the LED Clock application"""
    # Acquire process lock to prevent multiple instances
    lock = get_process_lock()
    
    if not lock.acquire():
        print("\n=== CANNOT START ===")
        print("Another instance of the LED clock is already running.")
        print("Only one instance can control the LED matrix at a time.")
        sys.exit(1)
    
    try:
        clock = LEDClock()
        clock.run()
    except Exception as e:
        print(f"Failed to start LED Clock: {e}")
        cleanup_matrix()
        sys.exit(1)
    finally:
        # Release the lock when we're done
        lock.release()

if __name__ == "__main__":
    main()