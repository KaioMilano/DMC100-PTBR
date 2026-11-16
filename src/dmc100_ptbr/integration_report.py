"""Run integrated virtual UI and report logical resource costs, never an image."""
import argparse
import hashlib
import json
from pathlib import Path

from .arm_menu import assemble_menu
from .arm_ui import (VirtualLanguageUI, bridge_code, draw_code, renderer_code,
                     OWN_TEXTS, PT, DECODER, KEYS)
from .arm_utf8 import assemble_decoder
from .accent_font import budget, compact_table
from .v14 import ACCENTS


def report(firmware=None):
    ui = VirtualLanguageUI(firmware, execute_glyphs=firmware is not None)
    frames = []
    for event in (None,"down","ok","back","down","ok","ok"):
        if event:
            ui.event(event)
        result = ui.render()
        frames.append({"event":event,"state":result["state"],
                       "original_menu_executed":result["original_menu_executed"],
                       "authorial_accent_pixel_calls":sum(t["call"] == "accent_pixel" for t in result["trace"]),
                       "original_glyph_boundary_calls":result["original_glyph_boundary_calls"],
                       "original_glyph_trace_sha256":result["original_glyph_trace_sha256"]})
    components = {"selector_code":len(assemble_menu()),"event_bridge_code":len(bridge_code()),
                  "menu_wrapper_code":len(draw_code()),"utf8_decoder_code":len(assemble_decoder(DECODER,KEYS)),
                  "mixed_text_renderer_code":len(renderer_code()),"unicode_keys":2*len(ACCENTS),
                  "accent_font_compact_source":len(compact_table()),"row_pointer_table":12,
                  "authorial_texts_utf8":sum(len(t.encode("utf-8"))+1 for t in OWN_TEXTS.values())}
    total = sum(components.values())
    return {"scope":"Single virtual CPU, original menu optional, all drawing intercepted",
            "private_original_supplied":firmware is not None,
            "original_sha256":None if firmware is None else hashlib.sha256(firmware).hexdigest(),
            "frames":frames,"components_logical_bytes":components,"logical_bytes_compact_runtime":total,
            "font_storage_comparison":budget(),
            "all_four_sizes_supported_by_runtime":True,
            "label_right_edge_by_height":{h:106+len(OWN_TEXTS[PT])*(h//2) for h in (12,16,24,32)},
            "large_font_overflow_is_not_automatically_fixed":True,
            "original_sample_gap_before_settings":3344,
            "gap_is_proven_free":False,"physical_placement_validated":False,
            "padding_stack_trampolines_other_texts_included":False,
            "buttons_decoded_from_device":False,"flash_persistence_implemented":False,
            "update_integrity_verified":False,"v13_hardware_compatibility_verified":False,
            "recovery_demonstrated":False,"firmware_generated":False,"installable_ready":False,
            "memory_note":"Logical payload only; excludes virtual page padding and complete integration. No address is reserved on the meter."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware",type=Path)
    args = parser.parse_args(argv)
    data = args.firmware.read_bytes() if args.firmware else None
    result = report(data)
    if args.firmware and args.firmware.read_bytes() != data:
        raise RuntimeError("Private input changed")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
