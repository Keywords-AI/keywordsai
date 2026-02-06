#!/usr/bin/env python3
"""
Example demonstrating Python logging hierarchy and __name__ usage.

This shows exactly how KeywordsAI tracing debug logging works.
"""

import logging
from keywordsai_tracing.constants import LOGGER_NAME

print("=== Understanding __name__ and Logger Inheritance ===\n")

# 1. Show what __name__ contains in different contexts
print("1. What __name__ contains:")
print(f"   In this script: __name__ = '{__name__}'")
print(f"   In exporter module: __name__ = 'keywordsai_tracing.core.exporter'")
print(f"   In client module: __name__ = 'keywordsai_tracing.core.client'")
print(f"   LOGGER_NAME constant = '{LOGGER_NAME}'")
print()

# 2. Create the logger hierarchy
print("2. Creating logger hierarchy:")
parent_logger = logging.getLogger(LOGGER_NAME)
child1_logger = logging.getLogger(f"{LOGGER_NAME}.core.exporter")
child2_logger = logging.getLogger(f"{LOGGER_NAME}.core.client")
grandchild_logger = logging.getLogger(f"{LOGGER_NAME}.core.exporter.http")

print(f"   Parent: {parent_logger.name}")
print(f"   Child 1: {child1_logger.name}")
print(f"   Child 2: {child2_logger.name}")
print(f"   Grandchild: {grandchild_logger.name}")
print()

# 3. Show parent-child relationships
print("3. Parent-child relationships:")
print(f"   Child1 parent: {child1_logger.parent.name}")
print(f"   Child2 parent: {child2_logger.parent.name}")
print(f"   Grandchild parent: {grandchild_logger.parent.name}")
print()

# 4. Setup logging like KeywordsAITelemetry does
print("4. Setting up logging (like KeywordsAITelemetry):")
parent_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
parent_logger.addHandler(handler)
parent_logger.propagate = False

print("   Parent logger set to DEBUG level")
print("   Added handler with formatter")
print()

# 5. Show effective levels
print("5. Effective log levels after parent setup:")
print(f"   Parent effective level: {logging.getLevelName(parent_logger.getEffectiveLevel())}")
print(f"   Child1 effective level: {logging.getLevelName(child1_logger.getEffectiveLevel())}")
print(f"   Child2 effective level: {logging.getLevelName(child2_logger.getEffectiveLevel())}")
print(f"   Grandchild effective level: {logging.getLevelName(grandchild_logger.getEffectiveLevel())}")
print()

# 6. Demonstrate inheritance in action
print("6. Debug messages (inheritance in action):")
parent_logger.debug("Parent debug message")
child1_logger.debug("Child1 debug message (this is like the exporter)")
child2_logger.debug("Child2 debug message (this is like the client)")
grandchild_logger.debug("Grandchild debug message")
print()

# 7. Show what happens with different log levels
print("7. Testing with INFO level:")
parent_logger.setLevel(logging.INFO)
print("   Parent set to INFO level")
print("   Effective levels now:")
print(f"     Parent: {logging.getLevelName(parent_logger.getEffectiveLevel())}")
print(f"     Child1: {logging.getLevelName(child1_logger.getEffectiveLevel())}")

print("   Trying debug messages (should not appear):")
child1_logger.debug("This debug message won't appear")
child1_logger.info("This info message will appear")
print()

print("=== Summary ===")
print("✅ __name__ creates hierarchical logger names based on module paths")
print("✅ Dot notation automatically creates parent-child relationships")
print("✅ Child loggers inherit log levels from their parents")
print("✅ KeywordsAI sets parent logger to DEBUG, all children inherit it")
print("✅ That's why exporter debug messages appear!") 