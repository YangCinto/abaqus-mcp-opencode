import os


MCP_HOME = os.environ.get('ABAQUS_MCP_HOME')
if not MCP_HOME:
    MCP_HOME = os.path.dirname(os.path.abspath(__file__))
os.environ['ABAQUS_MCP_HOME'] = MCP_HOME

stop_file = os.path.join(MCP_HOME, 'stop.flag')
if os.path.exists(stop_file):
    os.remove(stop_file)

plugin_path = os.path.join(MCP_HOME, 'abaqus_mcp_plugin.py')
with open(plugin_path, 'r') as f:
    exec(compile(f.read(), plugin_path, 'exec'), globals(), globals())

mcp_loop(sleep_interval=0.1)
