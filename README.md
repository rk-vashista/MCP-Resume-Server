# 🚀 MCP Resume Server

A **Model Context Protocol (MCP) server** built with FastMCP that serves personal resume data and provides web fetching capabilities. This server is designed to integrate with AI systems like Puch AI for automated resume sharing and validation.

## 📋 Features

- **🔐 Bearer Token Authentication** - Secure access with configurable tokens
- **📄 Resume Tool** - Automatically extracts and serves resume from PDF files
- **✅ Validation Tool** - Phone number validation for server identity verification
- **🌐 Web Fetching** - Fetch and parse web content with markdown conversion
- **🔍 Debug Support** - Built-in debugging tools for troubleshooting

## 🛠️ Tools Available

### 1. **Resume Tool**
- **Purpose**: Serves personal resume in markdown format
- **Input**: Optional name parameter for personalized greeting
- **Output**: Resume content extracted from `Resume.pdf` or fallback content
- **Features**: 
  - PDF text extraction using PyMuPDF
  - Automatic length truncation to prevent timeouts
  - Graceful error handling

### 2. **Validate Tool**
- **Purpose**: Returns phone number for server identity validation
- **Output**: Phone number in `{country_code}{number}` format
- **Required**: Must be present for Puch AI integration

### 3. **Fetch Tool**
- **Purpose**: Fetches and parses web content
- **Input**: URL, max length, start index, raw option
- **Output**: Simplified markdown content or raw HTML
- **Features**: 
  - Content truncation with continuation support
  - HTML to markdown conversion
  - Error handling for failed requests

## 🚀 Quick Start

### Prerequisites

```bash
# Install required packages
pip install fastmcp pymupdf httpx readabilipy markdownify pydantic
```

### Configuration

1. **Set your authentication token:**
   ```python
   TOKEN = "your_application_key_here"
   ```

2. **Set your phone number:**
   ```python
   MY_NUMBER = "916366797779"  # Format: {country_code}{number}
   ```

3. **Add your resume:**
   - Place your resume as `Resume.pdf` in the project directory
   - Or modify the fallback content in the resume function

### Running the Server

```bash
# Start the MCP server
python mcp_server.py
```

The server will start on `http://0.0.0.0:8085/mcp`

### Making it Publicly Accessible

For integration with external services like Puch AI, you'll need to expose your server:

```bash
# Using ngrok (recommended)
ngrok http 8085

# Your public URL will be something like:
# https://abcd-1234-5678-9012.ngrok-free.app/mcp
```


## 📁 Project Structure

```
puchAI/
├── mcp_server.py      # Main MCP server implementation
├── Resume.pdf         # Your resume file (optional)
├── .gitignore        # Git ignore rules
├── README.md         # This file
└── .venv/            # Virtual environment (if used)
```

## 🔧 Configuration Options

### Environment Variables (Recommended)
```python
import os
TOKEN = os.getenv("MCP_TOKEN", "default_token")
MY_NUMBER = os.getenv("PHONE_NUMBER", "916366797779")
```

### Server Settings
- **Host**: `0.0.0.0` (accepts connections from any IP)
- **Port**: `8085`
- **Transport**: `streamable-http`
- **Authentication**: Bearer token

## 🛡️ Security Considerations

- **🔒 Token Security**: Never commit your actual token to version control
- **🌐 Public Exposure**: Only expose your server when needed
- **📱 Phone Number**: Ensure your phone number format is correct
- **📄 Resume Content**: Review what personal information is being shared

## 🐛 Troubleshooting

### Common Issues:

1. **401 Unauthorized**
   - Check your bearer token is correct
   - Ensure token matches between client and server

2. **Could not process request**
   - Resume content might be too long (check truncation)
   - Verify PDF file exists and is readable
   - Check server logs for specific errors

3. **Connection Failed**
   - Verify ngrok tunnel is active
   - Check firewall settings
   - Ensure correct URL format with `/mcp` endpoint

### Debug Commands:
```bash
# Check server status
curl -X POST http://localhost:8085/mcp/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## 📝 Logs

The server provides detailed logging:
- `📄 resume() tool called` - Resume tool execution
- `🔍 validate() tool called` - Validation tool execution  
- `🐛 debug_info() tool called` - Debug tool execution
- `❌ Error in resume tool` - Error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is intended for personal use. Modify and distribute as needed for your own applications.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review server logs
3. Verify configuration settings
4. Test with debug tools

---

**Built with ❤️ using FastMCP**
