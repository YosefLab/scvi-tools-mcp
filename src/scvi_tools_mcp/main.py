from scvi_tools_mcp.mcp import mcp


def run_app() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_app()
