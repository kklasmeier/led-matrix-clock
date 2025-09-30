# utils/process_lock.py - Process locking to prevent multiple instances

import os
import sys
import atexit
from typing import Optional

class ProcessLock:
    """Ensures only one instance of the application runs at a time"""
    
    def __init__(self, lockfile_path: str = "/tmp/led_clock.pid"):
        """
        Initialize the process lock
        
        Args:
            lockfile_path: Path to the PID lock file
        """
        self.lockfile_path = lockfile_path
        self.locked = False
    
    def is_process_running(self, pid: int) -> bool:
        """
        Check if a process with given PID is running
        
        Args:
            pid: Process ID to check
            
        Returns:
            bool: True if process is running, False otherwise
        """
        try:
            # Sending signal 0 checks if process exists without actually signaling it
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def acquire(self) -> bool:
        """
        Acquire the process lock
        
        Returns:
            bool: True if lock acquired successfully, False if another instance is running
        """
        # Check if lock file exists
        if os.path.exists(self.lockfile_path):
            try:
                with open(self.lockfile_path, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Check if the process is still running
                if self.is_process_running(old_pid):
                    print(f"ERROR: Another instance is already running (PID: {old_pid})")
                    print(f"Lock file: {self.lockfile_path}")
                    print(f"To force start, stop the other instance or remove the lock file:")
                    print(f"  sudo kill {old_pid}")
                    print(f"  # or")
                    print(f"  rm {self.lockfile_path}")
                    return False
                else:
                    # Stale lock file (process not running), remove it
                    print(f"Removing stale lock file (old PID: {old_pid})")
                    os.remove(self.lockfile_path)
            except (ValueError, IOError) as e:
                print(f"Warning: Could not read lock file: {e}")
                print(f"Removing invalid lock file")
                try:
                    os.remove(self.lockfile_path)
                except:
                    pass
        
        # Create new lock file with current PID
        try:
            with open(self.lockfile_path, 'w') as f:
                f.write(str(os.getpid()))
            
            self.locked = True
            
            # Register cleanup on exit
            atexit.register(self.release)
            
            print(f"Process lock acquired (PID: {os.getpid()})")
            return True
            
        except IOError as e:
            print(f"ERROR: Could not create lock file: {e}")
            return False
    
    def release(self) -> None:
        """Release the process lock by removing the lock file"""
        if self.locked and os.path.exists(self.lockfile_path):
            try:
                # Verify this is our lock file
                with open(self.lockfile_path, 'r') as f:
                    pid = int(f.read().strip())
                
                if pid == os.getpid():
                    os.remove(self.lockfile_path)
                    print(f"Process lock released")
                    self.locked = False
            except Exception as e:
                print(f"Warning: Could not remove lock file: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        if not self.acquire():
            raise RuntimeError("Could not acquire process lock - another instance is running")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


# Global lock instance
_process_lock: Optional[ProcessLock] = None

def get_process_lock(lockfile_path: str = "/tmp/led_clock.pid") -> ProcessLock:
    """Get or create the global ProcessLock instance"""
    global _process_lock
    if _process_lock is None:
        _process_lock = ProcessLock(lockfile_path)
    return _process_lock