"""
Core configuration and settings for HarmonyForge.
"""

from pydantic import BaseModel, Field
import random
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

class HarmonyConfig(BaseModel):
    """Global configuration for the HarmonyForge engine."""
    
    # Deterministic generation
    seed: Optional[int] = Field(default=None, description="Random seed for deterministic generation")
    
    # Engine parameters
    default_bpm: int = Field(default=120, description="Default BPM for generation")
    
    def set_seed(self, new_seed: int) -> None:
        """Sets the global random seed and numpy/scipy seeds if applicable."""
        try:
            self.seed = new_seed
            random.seed(new_seed)
            logger.info(f"Random seed set to {new_seed}")
            
            try:
                import numpy as np
                np.random.seed(new_seed)
                logger.debug("NumPy random seed set")
            except ImportError:
                logger.debug("NumPy not available, skipping seed")
                
            try:
                import torch
                torch.manual_seed(new_seed)
                logger.debug("PyTorch random seed set")
            except ImportError:
                logger.debug("PyTorch not available, skipping seed")
        except Exception as e:
            logger.error(f"Failed to set random seed: {e}")
            raise

# Default global instance
config = HarmonyConfig()
