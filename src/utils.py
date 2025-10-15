import base64
import os
import re
from pathlib import Path
from typing import List
import aiofiles
from src.models import Attachment
from src.config import config


async def decode_and_save_attachments(attachments: List[Attachment], task_id: str) -> List[Path]:
    """Decode data URIs and save attachments to disk"""
    saved_paths = []
    
    # Create temp directory
    temp_dir = Path(config.TEMP_ATTACHMENTS_DIR) / task_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    for attachment in attachments:
        # Parse data URI: data:image/png;base64,iVBORw...
        match = re.match(r'data:([^;]+);base64,(.+)', attachment.url)
        if not match:
            continue
        
        mime_type, base64_data = match.groups()
        
        # Decode base64
        file_data = base64.b64decode(base64_data)
        
        # Save to file
        file_path = temp_dir / attachment.name
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)
        
        saved_paths.append(file_path)
    
    return saved_paths


def sanitize_repo_name(task_id: str) -> str:
    """Convert task ID to valid GitHub repo name"""
    # Replace invalid characters with hyphens
    repo_name = re.sub(r'[^a-zA-Z0-9\-_.]', '-', task_id)
    # Remove leading/trailing hyphens
    repo_name = repo_name.strip('-')
    return repo_name


def get_mit_license() -> str:
    """Return MIT license text"""
    return """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
