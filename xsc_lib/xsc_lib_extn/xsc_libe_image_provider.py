"""
File: image_provider.py
Description: External integration for Image generation using Pillow.
Author: Siddharth Amdal.
"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


from PIL import Image, ImageDraw
from typing import Dict, Any


class ImageProvider:
    @staticmethod
    def generate(template_path: str, data: Dict[str, Any], output_path: str) -> bool:
        """
        Load an image template, overlay dynamic text onto it, and save the output.

        Args:
            template_path (str): The physical path to the image template file.
            data (Dict[str, Any]): The dictionary containing dynamic text overlays.
            output_path (str): The path to save the generated Image file.

        Returns:
            bool: True if generated successfully.
        """
        try:
            img = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(img)

            texts = data.get("texts", [])

            for item in texts:
                text = str(item.get("text", ""))
                x = item.get("x", 0)
                y = item.get("y", 0)
                color = item.get("color", "black")

                draw.text((x, y), text, fill=color)

            # Save output (convert back to RGB if JPEG)
            if XSCUtility.to_lower(output_path).endswith((".jpg", ".jpeg")):
                img = img.convert("RGB")

            img.save(output_path)
            return True
        except Exception as _e:
            print(f"[ImageProvider] Error generating Image: {str(e)}")
            raise
