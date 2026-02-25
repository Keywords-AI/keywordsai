#!/usr/bin/env python3
"""
Script to compare fields between RespanLogParams, RespanFullLogParams and RespanTextLogParams
to verify they are in sync after changes.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from respan_sdk.respan_types.log_types import RespanLogParams, RespanFullLogParams
from respan_sdk.respan_types.param_types import RespanTextLogParams


def get_field_info(model_class):
    """Get field information from a Pydantic model."""
    fields = {}
    for field_name, field_info in model_class.model_fields.items():
        field_type = field_info.annotation
        default = field_info.default
        fields[field_name] = {
            'type': str(field_type),
            'default': default,
            'required': field_info.is_required()
        }
    return fields


def compare_fields():
    """Compare fields between RespanLogParams, RespanFullLogParams and RespanTextLogParams."""
    
    print("=" * 80)
    print("FIELD COMPARISON: RespanLogParams vs RespanFullLogParams vs RespanTextLogParams")
    print("=" * 80)
    
    log_fields = get_field_info(RespanLogParams)
    full_log_fields = get_field_info(RespanFullLogParams)
    text_log_fields = get_field_info(RespanTextLogParams)
    
    print(f"\n📊 SUMMARY:")
    print(f"   RespanLogParams fields: {len(log_fields)}")
    print(f"   RespanFullLogParams fields: {len(full_log_fields)}")
    print(f"   RespanTextLogParams fields: {len(text_log_fields)}")
    
    # Compare RespanFullLogParams vs RespanTextLogParams (should be identical)
    full_vs_text_missing = set(text_log_fields.keys()) - set(full_log_fields.keys())
    full_vs_text_extra = set(full_log_fields.keys()) - set(text_log_fields.keys())
    
    # Find fields only in RespanLogParams
    only_in_log = set(log_fields.keys()) - set(text_log_fields.keys())
    
    # Find fields only in RespanTextLogParams
    only_in_text_log = set(text_log_fields.keys()) - set(log_fields.keys())
    
    # Find common fields
    common_fields = set(log_fields.keys()) & set(text_log_fields.keys())
    
    print(f"   Common fields (Log vs Text): {len(common_fields)}")
    print(f"   Only in RespanLogParams: {len(only_in_log)}")
    print(f"   Only in RespanTextLogParams: {len(only_in_text_log)}")
    
    # Check RespanFullLogParams completeness
    print(f"\n🎯 COMPLETENESS CHECK:")
    if not full_vs_text_missing and not full_vs_text_extra:
        print(f"   ✅ RespanFullLogParams has EXACTLY the same fields as RespanTextLogParams!")
    else:
        if full_vs_text_missing:
            print(f"   ❌ RespanFullLogParams is missing {len(full_vs_text_missing)} fields:")
            for field in sorted(full_vs_text_missing):
                print(f"      - {field}")
        if full_vs_text_extra:
            print(f"   ⚠️  RespanFullLogParams has {len(full_vs_text_extra)} extra fields:")
            for field in sorted(full_vs_text_extra):
                print(f"      - {field}")
    
    if only_in_log:
        print(f"\n🟡 FIELDS ONLY IN RespanLogParams ({len(only_in_log)}):")
        print("   These are already in the public log params but missing from text log params")
        for field in sorted(only_in_log):
            field_info = log_fields[field]
            print(f"   - {field}: {field_info['type']}")
    
    if only_in_text_log:
        print(f"\n🔴 FIELDS ONLY IN RespanTextLogParams ({len(only_in_text_log)}):")
        print("   These need to be added to RespanLogParams or moved to RespanFullLogParams")
        
        # Group by likely source (LLM vs Embedding vs Respan internal)
        llm_like_fields = []
        embedding_like_fields = []
        internal_fields = []
        
        for field in sorted(only_in_text_log):
            field_info = text_log_fields[field]
            field_lower = field.lower()
            
            # Categorize fields
            if any(keyword in field_lower for keyword in ['token', 'prompt', 'completion', 'model', 'temperature', 'top_p', 'frequency', 'presence', 'stop', 'max_tokens', 'stream', 'tool', 'response_format', 'logprobs', 'echo', 'n']):
                llm_like_fields.append((field, field_info))
            elif any(keyword in field_lower for keyword in ['embedding', 'dimension', 'encoding']):
                embedding_like_fields.append((field, field_info))
            else:
                internal_fields.append((field, field_info))
        
        if llm_like_fields:
            print(f"\n   📝 LLM-related fields ({len(llm_like_fields)}):")
            for field, info in llm_like_fields:
                print(f"      - {field}: {info['type']}")
        
        if embedding_like_fields:
            print(f"\n   🔢 Embedding-related fields ({len(embedding_like_fields)}):")
            for field, info in embedding_like_fields:
                print(f"      - {field}: {info['type']}")
        
        if internal_fields:
            print(f"\n   ⚙️  Internal/Other fields ({len(internal_fields)}):")
            for field, info in internal_fields:
                print(f"      - {field}: {info['type']}")
    
    # Check for type differences in common fields
    type_differences = []
    for field in common_fields:
        log_type = log_fields[field]['type']
        text_log_type = text_log_fields[field]['type']
        if log_type != text_log_type:
            type_differences.append((field, log_type, text_log_type))
    
    if type_differences:
        print(f"\n🟠 FIELDS WITH TYPE DIFFERENCES ({len(type_differences)}):")
        for field, log_type, text_log_type in type_differences:
            print(f"   - {field}:")
            print(f"     RespanLogParams: {log_type}")
            print(f"     RespanTextLogParams: {text_log_type}")
    
    # Check type differences between RespanFullLogParams and RespanTextLogParams
    full_type_differences = []
    for field in set(full_log_fields.keys()) & set(text_log_fields.keys()):
        full_type = full_log_fields[field]['type']
        text_type = text_log_fields[field]['type']
        if full_type != text_type:
            full_type_differences.append((field, full_type, text_type))
    
    if full_type_differences:
        print(f"\n🔴 TYPE DIFFERENCES: RespanFullLogParams vs RespanTextLogParams ({len(full_type_differences)}):")
        for field, full_type, text_type in full_type_differences:
            print(f"   - {field}:")
            print(f"     RespanFullLogParams: {full_type}")
            print(f"     RespanTextLogParams: {text_type}")
    
    print("\n" + "=" * 80)
    print("SYNC STATUS:")
    print("=" * 80)
    
    if not full_vs_text_missing and not full_vs_text_extra and not full_type_differences:
        print("✅ PERFECT SYNC: RespanFullLogParams is perfectly synchronized with RespanTextLogParams!")
    else:
        print("❌ OUT OF SYNC: RespanFullLogParams needs updates to match RespanTextLogParams")
    
    if not only_in_text_log:
        print("✅ GOOD: RespanLogParams contains a proper subset of RespanTextLogParams fields")
    else:
        print("⚠️  ATTENTION: Some fields exist only in RespanTextLogParams")
    
    print("\n" + "=" * 80)
    
    return {
        'only_in_log': only_in_log,
        'only_in_text_log': only_in_text_log,
        'common_fields': common_fields,
        'type_differences': type_differences,
        'full_vs_text_missing': full_vs_text_missing,
        'full_vs_text_extra': full_vs_text_extra,
        'full_type_differences': full_type_differences,
        'is_complete': not full_vs_text_missing and not full_vs_text_extra and not full_type_differences
    }


if __name__ == "__main__":
    try:
        comparison_results = compare_fields()
        
        # Exit with appropriate code
        if comparison_results['is_complete']:
            print("🎉 All checks passed!")
            sys.exit(0)
        else:
            print("💥 Synchronization issues found!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during comparison: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)