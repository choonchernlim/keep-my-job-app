import sys
import subprocess
import threading


def forward_stream(src, dst):
    """Reads from src and writes to dst."""
    for line in src:
        # THE FIX: Filter out the specific noisy line(s)
        if "STDIO MCP Server started" in line:
            continue

        dst.write(line)
        dst.flush()


if __name__ == "__main__":
    # Launch the actual MCP server
    # Note: We use shell=True/False depending on OS, generally False is safer
    process = subprocess.Popen(
        ["npx", "-y", "mcp-mermaid"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,  # Let stderr flow through directly
        text=True,
        bufsize=1  # Line buffered
    )

    # Start a thread to read the server's stdout and pipe it to our stdout (filtering bad lines)
    t = threading.Thread(target=forward_stream, args=(process.stdout, sys.stdout))
    t.daemon = True
    t.start()

    # Read from our stdin and pipe it to the server's stdin
    try:
        for line in sys.stdin:
            process.stdin.write(line)
            process.stdin.flush()
    except BrokenPipeError:
        pass
