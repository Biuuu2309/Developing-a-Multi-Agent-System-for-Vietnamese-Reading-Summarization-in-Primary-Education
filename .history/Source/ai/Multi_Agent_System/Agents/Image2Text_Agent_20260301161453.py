from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from PIL import Image
import base64
import io
import time
import os
from typing import Optional, Dict, Any
from pathlib import Path


class Image2TextAgent:
    """
    Agent để extract text từ ảnh sử dụng Vision-Language Model
    Tối ưu hóa cho performance với model quantized và image compression
    """
    
    def __init__(
        self,
        model: str = "qwen2.5vl:7b-q4_K_M",
        temperature: float = 0,
        num_ctx: int = 2048,
        num_predict: int = 256
    ):
        """
        Initialize Image2Text Agent với cấu hình tối ưu
        
        Args:
            model: Model name cho Ollama (vision-language model, mặc định dùng quantized version)
            temperature: Temperature cho LLM (0 cho OCR chính xác)
            num_ctx: Context window size (2048 đủ cho OCR)
            num_predict: Max tokens to predict (256 đủ cho OCR)
        """
        # Tối ưu môi trường
        os.environ["OLLAMA_NUM_PARALLEL"] = "4"
        
        self.llm = ChatOllama(
            model=model,
            temperature=temperature,
            num_ctx=num_ctx,
            num_predict=num_predict
        )
        
        # Prompt ngắn gọn, tối ưu
        self.ocr_prompt = (
            "Extract all visible text exactly as written. "
            "Preserve Vietnamese diacritics. "
            "No explanation. "
            "Return plain text only."
        )
    
    def encode_image(
        self,
        image_path: str,
        max_size: int = 1000,
        quality: int = 80
    ) -> str:
        """
        Encode image to base64 string với compression tối ưu
        
        Args:
            image_path: Đường dẫn đến file ảnh
            max_size: Kích thước tối đa (pixels) cho thumbnail (1000 đủ cho OCR)
            quality: JPEG quality (80 đủ tốt và nhẹ hơn 95)
            
        Returns:
            Base64 encoded string của ảnh
        """
        try:
            img = Image.open(image_path)
            
            # Resize giữ tỉ lệ (giảm compute cho Vision encoder)
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to RGB nếu cần
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Encode to JPEG (nhẹ hơn PNG)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return image_base64
        except Exception as e:
            raise ValueError(f"Error encoding image: {str(e)}")
    
    def extract_text_from_image(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text từ ảnh
        
        Args:
            image_path: Đường dẫn đến file ảnh
            custom_prompt: Custom prompt nếu muốn (optional)
            
        Returns:
            Dict với keys:
                - text: Extracted text
                - success: bool
                - error: error message nếu có
        """
        try:
            # Encode image
            image_base64 = self.encode_image(image_path)
            
            # Use custom prompt or default OCR prompt
            prompt = custom_prompt or self.ocr_prompt
            
            # Create message với image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            # Invoke LLM
            response = self.llm.invoke([message])
            extracted_text = response.content.strip()
            
            return {
                "text": extracted_text,
                "success": True,
                "error": None,
                "image_path": image_path
            }
            
        except Exception as e:
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def extract_text_from_base64(
        self,
        image_base64: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text từ base64 encoded image (dùng khi đã có base64)
        
        Args:
            image_base64: Base64 encoded image string
            custom_prompt: Custom prompt nếu muốn
            
        Returns:
            Dict với keys: text, success, error
        """
        try:
            prompt = custom_prompt or self.ocr_prompt
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.llm.invoke([message])
            extracted_text = response.content.strip()
            
            return {
                "text": extracted_text,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    def is_image_file(self, file_path: str) -> bool:
        """
        Kiểm tra xem file có phải là ảnh không
        
        Args:
            file_path: Đường dẫn file
            
        Returns:
            True nếu là file ảnh
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
        return Path(file_path).suffix.lower() in image_extensions
