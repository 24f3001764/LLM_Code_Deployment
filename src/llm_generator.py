import os
from pathlib import Path
from typing import List
from openai import OpenAI
from src.config import config
import aiofiles


class LLMAppGenerator:
    """Generate web applications using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    async def generate_app(
        self, 
        brief: str, 
        checks: List[str], 
        attachments: List[Path],
        task_id: str
    ) -> Path:
        """Generate a complete web app based on the brief"""
        
        # Create output directory
        app_dir = Path(config.GENERATED_APPS_DIR) / task_id
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Build prompt
        prompt = self._build_prompt(brief, checks, attachments)
        
        # Generate HTML
        html_content = await self._generate_html(prompt)
        
        # Save index.html
        index_path = app_dir / "index.html"
        async with aiofiles.open(index_path, 'w', encoding='utf-8') as f:
            await f.write(html_content)
        
        # Generate README
        readme_content = await self._generate_readme(brief, task_id)
        readme_path = app_dir / "README.md"
        async with aiofiles.open(readme_path, 'w', encoding='utf-8') as f:
            await f.write(readme_content)
        
        return app_dir
    
    def _build_prompt(self, brief: str, checks: List[str], attachments: List[Path]) -> str:
        """Build prompt for LLM"""
        attachment_info = ""
        if attachments:
            attachment_names = [att.name for att in attachments]
            attachment_info = f"\n\nAttachments provided: {', '.join(attachment_names)}"
        
        checks_text = "\n".join([f"- {check}" for check in checks])
        
        return f"""Create a complete, self-contained single-page web application (HTML with embedded CSS and JavaScript).

**Requirements:**
{brief}

**Evaluation Criteria:**
{checks_text}
{attachment_info}

**Instructions:**
1. Create a modern, responsive UI using HTML5, CSS3, and vanilla JavaScript
2. Handle URL parameters (e.g., ?url=...) as specified
3. Include error handling and loading states
4. Make it visually appealing with good UX
5. Add clear instructions for users
6. Ensure all functionality works client-side
7. Use modern web APIs and best practices

Return ONLY the complete HTML file content, no explanations."""
    
    async def _generate_html(self, prompt: str) -> str:
        """Call OpenAI API to generate HTML"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert web developer. Generate clean, modern, production-ready HTML/CSS/JS code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            html_content = response.choices[0].message.content
            
            # Clean up markdown code blocks if present
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0].strip()
            elif "```" in html_content:
                html_content = html_content.split("```")[1].split("```")[0].strip()
            
            return html_content
        
        except Exception as e:
            # Fallback to basic template
            return self._get_fallback_template(prompt)
    
    async def _generate_readme(self, brief: str, task_id: str) -> str:
        """Generate professional README"""
        prompt = f"""Create a professional README.md for a web application with these details:

**Brief:** {brief}
**Task ID:** {task_id}

Include these sections:
1. Project title and brief description
2. Features
3. Setup instructions (how to run locally)
4. Usage instructions (how to use the app)
5. Code explanation (brief technical overview)
6. License (MIT)

Keep it concise and professional. Use Markdown formatting."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a technical writer creating clear, professional documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            readme = response.choices[0].message.content
            
            # Clean up markdown code blocks if present
            if "```markdown" in readme:
                readme = readme.split("```markdown")[1].split("```")[0].strip()
            elif "```" in readme:
                readme = readme.split("```")[1].split("```")[0].strip()
            
            return readme
        
        except Exception as e:
            return self._get_fallback_readme(brief, task_id)
    
    def _get_fallback_template(self, brief: str) -> str:
        """Fallback HTML template if API fails"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        p {{ color: #666; line-height: 1.6; margin-bottom: 20px; }}
        .brief {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Generated Application</h1>
        <p>This application was automatically generated based on the following requirements:</p>
        <div class="brief">
            <strong>Brief:</strong><br>
            {brief}
        </div>
        <p style="margin-top: 20px; font-size: 14px; color: #999;">
            Note: This is a placeholder. The full application will be generated by the LLM.
        </p>
    </div>
</body>
</html>"""
    
    def _get_fallback_readme(self, brief: str, task_id: str) -> str:
        """Fallback README if API fails"""
        return f"""# {task_id}

## Description
{brief}

## Setup
1. Clone this repository
2. Open `index.html` in a web browser

## Usage
Open the application in your browser and follow the on-screen instructions.

## Technical Details
This is a single-page web application built with HTML, CSS, and JavaScript.

## License
MIT License - see LICENSE file for details
"""
