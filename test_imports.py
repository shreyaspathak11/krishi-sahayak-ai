#!/usr/bin/env python
"""Test which import paths work for create_tool_calling_agent"""

attempts = [
    ("from langchain.agents.tool_calling_agent.base import create_tool_calling_agent", "tool_calling_agent.base"),
    ("from langchain.agents import create_tool_calling_agent", "agents direct"),
    ("from langchain_core.agents import create_tool_calling_agent", "core.agents"),
]

for import_stmt, name in attempts:
    try:
        exec(import_stmt)
        print(f"✓ {name}")
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
