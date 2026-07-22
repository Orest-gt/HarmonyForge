"""
Core configuration and settings for HarmonyForge.
"""

from pydantic import BaseModel, Field
import random
from typing import Optional

class HarmonyConfig(BaseModel):
    """Global configuration for the HarmonyForge engine."""
    
    # Deterministic generation
    seed: Optional[int] = Field(default=None, description="Random seed for deterministic generation")
    
    # Engine parameters
    default_bpm: int = Field(default=120, description="Default BPM for generation")
    
    def set_seed(self, new_seed: int) -> None:
        """Sets the global random seed and numpy/scipy seeds if applicable."""
        self.seed = new_seed
        random.seed(new_seed)
        
        try:
            import numpy as np
            np.random.seed(new_seed)
        except ImportError:
            pass
            
        try:
            import torch
            torch.manual_seed(new_seed)
        except ImportError:
            pass

# Default global instance
config = HarmonyConfig()
