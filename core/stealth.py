import random
import time
import asyncio
import logging
from math import sin, pi

class StealthManager:
    def __init__(self, level=1):
        """
        Initialize stealth manager with specified level
        Level 1: Basic stealth (random delays)
        Level 2: Intermediate (random + patterns)
        Level 3: Advanced (complex patterns, traffic shaping)
        """
        self.level = level
        self.logger = logging.getLogger('Red_T.stealth')
        self.pattern_phase = 0
        
    async def random_delay(self, base=0.1, multiplier=2.0):
        """Generate a random delay based on stealth level"""
        if self.level == 1:
            delay = base + random.random() * multiplier
        elif self.level == 2:
            # More sophisticated delay with pattern
            delay = base + (random.random() * multiplier * 0.5) + (0.5 * sin(self.pattern_phase) + 0.5)
            self.pattern_phase += 0.3
        else:
            # Advanced: Combine random, pattern, and traffic shaping
            delay = base + (random.random() * multiplier * 0.3) + \
                   (0.3 * sin(self.pattern_phase) + \
                   (0.4 * sin(self.pattern_phase * 0.5))
            self.pattern_phase += 0.2
            
        self.logger.debug(f"Applying stealth delay: {delay:.2f}s")
        await asyncio.sleep(delay)
        return delay
        
    async def connection_pattern(self):
        """Pattern for connection attempts to avoid detection"""
        if self.level == 1:
            await self.random_delay(0.5, 1.0)
        elif self.level == 2:
            # Burst pattern with cooldown
            for _ in range(random.randint(1, 3)):
                await asyncio.sleep(0.1 + random.random() * 0.2)
            await asyncio.sleep(0.5 + random.random() * 1.0)
        else:
            # Advanced: Mimic normal user behavior patterns
            pattern = [
                0.2, 0.3, 0.1,  # Quick initial attempts
                1.5,             # Pause
                0.4, 0.2,        # Follow-up
                3.0,             # Longer pause
                0.3, 0.3, 0.3    # Final attempts
            ]
            for delay in pattern:
                await asyncio.sleep(delay * (0.9 + random.random() * 0.2))
                
    async def transmission_pattern(self, data_size):
        """Shape data transmission timing based on size and stealth level"""
        if self.level == 1:
            # Simple linear delay based on size
            delay = min(5.0, data_size / 1024 * 0.1)  # 0.1s per KB, max 5s
            await asyncio.sleep(delay)
        elif self.level == 2:
            # Non-linear delay with randomness
            delay = min(3.0, (data_size / 1024) ** 0.7 * 0.3)
            delay *= 0.8 + random.random() * 0.4
            await asyncio.sleep(delay)
        else:
            # Advanced: Simulate human typing patterns for small data
            if data_size < 128:
                # Simulate typing speed (50-300ms per character)
                for _ in range(data_size):
                    await asyncio.sleep(0.05 + random.random() * 0.25)
            else:
                # For larger data, use shaped bursts
                remaining = data_size
                while remaining > 0:
                    chunk = min(512, remaining)
                    # Delay based on chunk size
                    delay = (chunk / 1024) ** 0.6 * 0.5
                    await asyncio.sleep(delay)
                    # Small pause between chunks
                    await asyncio.sleep(0.1 + random.random() * 0.3)
                    remaining -= chunk
                    
    def get_jitter(self, base=0.1, scale=1.0):
        """Get jitter value for scan intervals"""
        if self.level == 1:
            return base + random.random() * scale
        elif self.level == 2:
            return base + (random.random() * scale * 0.5) + (0.3 * sin(time.time()))
        else:
            return base + (random.random() * scale * 0.3) + \
                   (0.2 * sin(time.time())) + \
                   (0.2 * sin(time.time() * 0.3))
                   
    def get_scan_window(self):
        """Get variable scan window duration"""
        if self.level == 1:
            return 2.0 + random.random() * 3.0
        elif self.level == 2:
            return 1.5 + random.random() * 2.0 + 0.5 * sin(time.time() * 0.5)
        else:
            return 1.0 + random.random() * 1.5 + \
                   0.3 * sin(time.time() * 0.3) + \
                   0.2 * sin(time.time() * 0.7)
                   
    def get_scan_duration(self):
        """Get total scan duration with stealth variations"""
        if self.level == 1:
            return 8.0 + random.random() * 10.0
        elif self.level == 2:
            return 6.0 + random.random() * 6.0 + 2.0 * sin(time.time() * 0.2)
        else:
            return 5.0 + random.random() * 4.0 + \
                   1.5 * sin(time.time() * 0.15) + \
                   1.0 * sin(time.time() * 0.4)
                   
    def random_choice(self, probability):
        """Make random choice with probability adjusted by stealth level"""
        if self.level == 1:
            return random.random() < probability
        elif self.level == 2:
            # Slightly more conservative
            adj_prob = probability * 0.9
            return random.random() < adj_prob
        else:
            # More conservative with pattern
            adj_prob = probability * (0.8 + 0.1 * sin(time.time() * 0.1))
            return random.random() < adj_prob
            
    def add_jitter(self, value, jitter_ratio):
        """Add jitter to a value based on stealth level"""
        if self.level == 1:
            return value * (1.0 + (random.random() - 0.5) * jitter_ratio)
        elif self.level == 2:
            jitter = (random.random() - 0.5) * jitter_ratio * 0.7
            jitter += 0.1 * sin(time.time() * 0.5)
            return value * (1.0 + jitter)
        else:
            jitter = (random.random() - 0.5) * jitter_ratio * 0.5
            jitter += 0.1 * sin(time.time() * 0.3)
            jitter += 0.05 * sin(time.time() * 0.7)
            return value * (1.0 + jitter)