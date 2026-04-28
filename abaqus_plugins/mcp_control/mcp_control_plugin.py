# -*- coding: utf-8 -*-
"""
MCP Control Plugin v4.0 - Adds GUI menu buttons to control MCP from kernel side.
"""

from abaqusGui import *
from abaqusConstants import ALL

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerKernelMenuButton(
    buttonText='MCP|Start MCP (Background, Experimental)',
    moduleName='__main__',
    functionName='mcp_start()',
    icon=None,
    applicableModules=ALL,
    version='4.0',
    author='MCP Plugin',
    description='Start MCP in background thread (experimental on some Abaqus builds)',
    helpUrl=''
)

toolset.registerKernelMenuButton(
    buttonText='MCP|Start MCP (Cooperative)',
    moduleName='__main__',
    functionName='mcp_coop_loop()',
    icon=None,
    applicableModules=ALL,
    version='4.0',
    author='MCP Plugin',
    description='Start MCP in cooperative loop mode',
    helpUrl=''
)

toolset.registerKernelMenuButton(
    buttonText='MCP|Start MCP (Blocking)',
    moduleName='__main__',
    functionName='mcp_loop()',
    icon=None,
    applicableModules=ALL,
    version='4.0',
    author='MCP Plugin',
    description='Start MCP in blocking mode',
    helpUrl=''
)

toolset.registerKernelMenuButton(
    buttonText='MCP|Stop MCP',
    moduleName='__main__',
    functionName='mcp_stop()',
    icon=None,
    applicableModules=ALL,
    version='4.0',
    author='MCP Plugin',
    description='Stop MCP polling',
    helpUrl=''
)

toolset.registerKernelMenuButton(
    buttonText='MCP|MCP Status',
    moduleName='__main__',
    functionName='mcp_status()',
    icon=None,
    applicableModules=ALL,
    version='4.0',
    author='MCP Plugin',
    description='Print current MCP status to console',
    helpUrl=''
)
