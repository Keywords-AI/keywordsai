#!/usr/bin/env python3
"""
Simple Evaluator Example

This example shows how to:
1. List available evaluators
2. Get details of a specific evaluator
3. Filter evaluators by type

Usage:
    python examples/simple_evaluator_example.py

Environment variables required:
- RESPAN_API_KEY
- RESPAN_BASE_URL (optional)
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from respan.evaluators.api import EvaluatorAPI


async def main():
    """Simple evaluator example"""
    
    api_key = os.getenv("RESPAN_API_KEY")
    base_url = os.getenv("RESPAN_BASE_URL", "http://localhost:8000")
    
    if not api_key:
        print("❌ RESPAN_API_KEY not found in environment")
        return
    
    print("🔍 Respan Evaluators Example")
    print("=" * 40)
    print(f"🔗 Using API: {base_url}")
    print()
    
    evaluator_api = EvaluatorAPI(api_key=api_key, base_url=base_url)
    
    try:
        # List all evaluators
        print("📋 Listing all available evaluators...")
        evaluators = await evaluator_api.alist(page_size=10)
        
        print(f"✅ Found {len(evaluators.results)} evaluators:")
        print()
        
        for i, evaluator in enumerate(evaluators.results, 1):
            print(f"{i:2d}. {evaluator.name}")
            print(f"     Slug: {evaluator.slug}")
            print(f"     ID: {evaluator.id}")
            if hasattr(evaluator, 'description') and evaluator.description:
                print(f"     Description: {evaluator.description}")
            print()
        
        if evaluators.results:
            # Get details of first evaluator
            first_evaluator = evaluators.results[0]
            print(f"🔍 Getting details for: {first_evaluator.name}")
            
            detailed_evaluator = await evaluator_api.aget(first_evaluator.id)
            print(f"✅ Retrieved: {detailed_evaluator.name}")
            print(f"   Slug: {detailed_evaluator.slug}")
            
            # Print all available attributes
            print("   Available attributes:")
            for attr in dir(detailed_evaluator):
                if not attr.startswith('_'):
                    try:
                        value = getattr(detailed_evaluator, attr)
                        if not callable(value):
                            print(f"     {attr}: {value}")
                    except:
                        pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())