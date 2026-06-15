# Architecture

The block diagram below summarizes the `scvi-tools-mcp` package layers: MCP client consumers,
FastMCP server, seven tool-module groups, shared utilities, the bundled Markdown/JSON knowledge base,
and the offline build-script pipeline that populates it. The Hugging Face Hub source is refreshed quarterly
and exposed through dedicated hub tools without runtime network calls.

```{raw} html
<p>
  <a class="reference external" href="scvi-tools-mcp-block-diagram.html" target="_blank">
    Open the block diagram in a full browser tab
  </a>
</p>
<iframe
  src="scvi-tools-mcp-block-diagram.html"
  title="scvi-tools-mcp block diagram"
  style="width: 100%; height: 1100px; border: 1px solid #d8dee4; border-radius: 8px;"
></iframe>
```
