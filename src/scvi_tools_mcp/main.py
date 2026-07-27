from scvi_tools_mcp.mcp import mcp


def run_app() -> None:
    """Run the scVI-Tools MCP server over the standard I/O transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_app()
