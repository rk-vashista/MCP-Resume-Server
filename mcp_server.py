from typing import Annotated
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
import markdownify
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, TextContent
from openai import BaseModel
from pydantic import AnyUrl, Field
import readabilipy
from pathlib import Path
import fitz  # PyMuPDF

# 🔁 Replace these
TOKEN = " "
MY_NUMBER = "916366797779"


class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None


class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(
            public_key=k.public_key, jwks_uri=None, issuer=None, audience=None
        )
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="unknown",
                scopes=[],
                expires_at=None,
            )
        return None


class Fetch:
    IGNORE_ROBOTS_TXT = True
    USER_AGENT = "Puch/1.0 (Autonomous)"

    @classmethod
    async def fetch_url(cls, url: str, user_agent: str, force_raw: bool = False) -> tuple[str, str]:
        from httpx import AsyncClient, HTTPError
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": user_agent},
                    timeout=30,
                )
            except HTTPError as e:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch {url}: {e!r}"))

            if response.status_code >= 400:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch {url} - status code {response.status_code}"))

            page_raw = response.text

        content_type = response.headers.get("content-type", "")
        is_page_html = "<html" in page_raw[:100] or "text/html" in content_type or not content_type

        if is_page_html and not force_raw:
            return cls.extract_content_from_html(page_raw), ""
        return page_raw, f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n"

    @staticmethod
    def extract_content_from_html(html: str) -> str:
        ret = readabilipy.simple_json.simple_json_from_html_string(html, use_readability=True)
        if not ret["content"]:
            return "<e>Page failed to be simplified from HTML</e>"
        return markdownify.markdownify(ret["content"], heading_style=markdownify.ATX)


mcp = FastMCP("My MCP Server", auth=SimpleBearerAuthProvider(TOKEN))

ResumeToolDescription = RichToolDescription(
    description="Serve your resume in plain markdown.",
    use_when="Puch (or anyone) asks for your resume; this must return raw markdown, no extra formatting.",
    side_effects=None,
)

@mcp.tool(description=ResumeToolDescription.model_dump_json())
async def resume(
    name: Annotated[str | None, Field(default=None, description="Name of the person requesting the resume")] = None
) -> str:
    """
    Return resume as markdown text.
    """
    print(f"📄 resume() tool called for: {name}")  # For debug

    try:
        resume_path = Path("Resume.pdf")
        if not resume_path.exists():
            # Fallback basic markdown if PDF not found
            greeting = f"Hello {name}! " if name else ""
            return (
                f"# Resume\n\n"
                f"{greeting}Here is my resume:\n\n"
                "**Roshan RK Vashista**\n\n"
                "- AI/ML Research Intern at ISRO\n"
                "- Full Stack Developer\n"
                "- Projects: Gesture Control, PDF Chat, Image Segmentation\n"
                "- Skills: Python, JavaScript, ML, AI\n"
                "- Contact: mailtorkvashista@gmail.com\n"
            )

        doc = fitz.open(resume_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        
        # Limit resume length to prevent timeouts (max 1500 characters)
        if len(text) > 1500:
            text = text[:1500] + "\n\n[Resume content truncated for brevity - full details available on request]"
        
        greeting = f"Hello {name}! " if name else ""
        markdown_resume = f"# Resume\n\n{greeting}Here is my resume:\n\n{text.strip()}"
        
        print(f"📄 Resume length: {len(markdown_resume)} characters")  # Debug
        return markdown_resume
        
    except Exception as e:
        error_msg = f"Failed to load resume: {str(e)}"
        print(f"❌ Resume error: {error_msg}")  # Debug
        return f"# Resume\n\n**Roshan RK Vashista**\n\n*AI/ML Research Intern at ISRO*\n\nContact: mailtorkvashista@gmail.com\n\n- Full Stack Developer\n- Projects: Gesture Control, PDF Chat, Image Segmentation\n- Skills: Python, JavaScript, ML, AI"


ValidateToolDescription = RichToolDescription(
    description="Return the phone number in country_code+number format for validation.",
    use_when="When validation is required to confirm the server identity.",
    side_effects=None,
)

@mcp.tool(description=ValidateToolDescription.model_dump_json())
async def validate() -> str:
    """
    Return phone number in country_code+number format for validation.
    """
    print("🔍 validate() tool called")  # For debug
    print(f"🔍 Returning validation number: {MY_NUMBER}")  # Debug
    return MY_NUMBER  # Returns "916366797779"


FetchToolDescription = RichToolDescription(
    description="Fetch a URL and return its content.",
    use_when="Use this tool when the user provides a URL and asks for its content, or when the user wants to fetch a webpage.",
    side_effects="The user will receive the content of the requested URL in a simplified format, or raw HTML if requested.",
)

@mcp.tool(description=FetchToolDescription.model_dump_json())
async def fetch(
    url: Annotated[AnyUrl, Field(description="URL to fetch")],
    max_length: Annotated[int, Field(default=5000, description="Max characters to return.", gt=0, lt=1000000)] = 5000,
    start_index: Annotated[int, Field(default=0, description="Starting character index.", ge=0)] = 0,
    raw: Annotated[bool, Field(default=False, description="Get raw HTML if True.")] = False,
) -> list[TextContent]:
    url_str = str(url).strip()
    if not url:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="URL is required"))

    content, prefix = await Fetch.fetch_url(url_str, Fetch.USER_AGENT, force_raw=raw)
    original_length = len(content)
    if start_index >= original_length:
        content = "<e>No more content available.</e>"
    else:
        truncated_content = content[start_index : start_index + max_length]
        if not truncated_content:
            content = "<e>No more content available.</e>"
        else:
            content = truncated_content
            actual_length = len(truncated_content)
            remaining = original_length - (start_index + actual_length)
            if actual_length == max_length and remaining > 0:
                next_start = start_index + actual_length
                content += f"\n\n<e>Content truncated. Call the fetch tool with a start_index of {next_start} to get more.</e>"

    return [TextContent(type="text", text=f"{prefix}Contents of {url}:\n{content}")]


async def main():
    print(f"🚀 Starting MCP Server with token: {TOKEN}")
    print(f"📱 Phone validation number: {MY_NUMBER}")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8085)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
