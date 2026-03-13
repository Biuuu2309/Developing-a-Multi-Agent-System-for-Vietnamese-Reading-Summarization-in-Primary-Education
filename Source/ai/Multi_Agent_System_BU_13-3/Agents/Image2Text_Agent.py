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
        num_ctx: int = 8192,
        num_predict: int = 2048
    ):
        """
        Initialize Image2Text Agent - ưu tiên chất lượng và độ chính xác
        
        Args:
            model: Model name cho Ollama (vision-language model)
            temperature: Temperature cho LLM (0 cho OCR chính xác)
            num_ctx: Context window size (8192 để đủ cho text dài)
            num_predict: Max tokens to predict (2048 để không bị cắt text)
        """
        # Tối ưu môi trường
        os.environ["OLLAMA_NUM_PARALLEL"] = "4"
        
        self.llm = ChatOllama(
            model=model,
            temperature=temperature,
            num_ctx=num_ctx,
            num_predict=num_predict
        )
        
        # Prompt chi tiết để extract đầy đủ nội dung
        self.ocr_prompt = (
            "Extract ALL visible text from the image exactly as written. "
            "Preserve ALL Vietnamese diacritics and special characters. "
            "Include ALL text, even if it appears in different sections or formats. "
            "Do not skip any text. "
            "Do not summarize or shorten the content. "
            "Return the complete text exactly as it appears in the image. "
            "No explanation, no formatting, just the raw text content."
        )
    
    def encode_image(
        self,
        image_path: str,
        max_size: int = None,
        quality: int = 100
    ) -> str:
        """
        Encode image to base64 string - ưu tiên chất lượng để không mất nội dung
        
        Args:
            image_path: Đường dẫn đến file ảnh
            max_size: Kích thước tối đa (pixels) cho thumbnail (None = không resize, giữ nguyên)
            quality: JPEG quality (100 = không nén, giữ chất lượng tối đa)
            
        Returns:
            Base64 encoded string của ảnh
        """
        try:
            img = Image.open(image_path)
            
            # Chỉ resize nếu max_size được chỉ định và ảnh lớn hơn
            # Ưu tiên giữ nguyên kích thước để không mất chi tiết
            if max_size is not None:
                # Chỉ resize nếu ảnh thực sự lớn hơn max_size
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to RGB nếu cần
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Encode to JPEG với quality cao nhất để giữ chi tiết text
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=False)
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return image_base64
        except Exception as e:
            raise ValueError(f"Error encoding image: {str(e)}")
    
    def extract_text_from_image(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None,
        show_timing: bool = False,
        max_size: Optional[int] = None,
        quality: int = 100
    ) -> Dict[str, Any]:
        """
        Extract text từ ảnh - ưu tiên chất lượng và độ đầy đủ
        
        Args:
            image_path: Đường dẫn đến file ảnh
            custom_prompt: Custom prompt nếu muốn (optional)
            show_timing: Hiển thị thời gian xử lý (default: False)
            max_size: Kích thước tối đa (None = không resize, giữ nguyên chất lượng)
            quality: JPEG quality (100 = không nén, giữ chất lượng tối đa)
            
        Returns:
            Dict với keys:
                - text: Extracted text (đầy đủ, không bị cắt)
                - success: bool
                - error: error message nếu có
                - image_path: đường dẫn ảnh
                - execution_time: thời gian xử lý (seconds) nếu show_timing=True
        """
        try:
            # Encode image với chất lượng cao nhất để không mất nội dung
            image_base64 = self.encode_image(image_path, max_size=max_size, quality=quality)
            
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
            
            # Invoke LLM với timing
            start_time = time.time()
            response = self.llm.invoke([message])
            execution_time = time.time() - start_time
            
            # Chỉ strip whitespace ở đầu/cuối, giữ nguyên nội dung bên trong
            # (có thể có nhiều dòng, khoảng trắng quan trọng)
            extracted_text = response.content.strip()
            
            result = {
                "text": extracted_text,
                "success": True,
                "error": None,
                "image_path": image_path
            }
            
            if show_timing:
                result["execution_time"] = round(execution_time, 2)
                print(f"⏱ OCR Time: {result['execution_time']} seconds")
            
            return result
            
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
