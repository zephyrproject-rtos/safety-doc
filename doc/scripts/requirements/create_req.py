#!/usr/bin/env python3
# Copyright (c) 2024 Intel Corp.
# SPDX-License-Identifier: Apache-2.0

import sys
import argparse
import json
import textwrap


HEADER = """
/**
@page Requirements
@tableofcontents

"""

RST_HEADER = """
===================================
Software Requirements Specification
===================================

This is the Software Requirements Specification.

Software capabilities
=====================
"""

FOOTER = """
*/
"""

def debug(msg):
    print("DEBUG: {}".format(msg))

def parse_nodes(nodes, grouped):
    for n in nodes:
        if n['TYPE'] in ['TEXT'] :
            continue
        elif n['TYPE'] in ['SECTION'] :
            grouped = parse_nodes(n['NODES'], grouped)
        else:
            rid = n.get('UID')
            name = n['TITLE']
            text= n['STATEMENT']
            group = n.get('COMPONENT', None)
            if not group:
                debug("No group for {}".format(rid))
                continue
            if not grouped.get(group, None):
                grouped[group] = []
            grouped[group].append({'rid': rid, 'req': text, 'name': name })

    return grouped

def parse_strictdoc_json(filename):
    grouped = dict()
    with open(filename) as fp:
        data = json.load(fp)
        docs = data.get('DOCUMENTS')
        for d in docs:
            parse_nodes(d['NODES'], grouped)
    return grouped

def write_dox(grouped, output="requirements.dox"):
    with open(output, "w") as req:
        req.write(HEADER)
        counter = 0
        for r in grouped.keys():
            comp = grouped[r]
            counter += 1
            req.write(f"\n@section REQSEC{counter} {r}\n\n")
            for c in comp:
                req.write("@subsection {} {}: {}\n{}\n\n\n".format(c['rid'], c['rid'], c['name'], c['req']))

        req.write(FOOTER)

def wrap_text(text, width=80):
    indentation = "    "  # 4 spaces indentation

    # Split paragraphs by double newline
    paragraphs = text.strip().split('\n\n')

    # Wrap each paragraph individually, then join them with a double newline
    wrapped_paragraphs = [
        textwrap.fill(p, width=width, initial_indent=indentation, subsequent_indent=indentation)
        for p in paragraphs
    ]

    result = '\n\n'.join(wrapped_paragraphs)
    return result

def write_rst(grouped, output="requirements.rst"):
    with open(output, "w") as req:
        req.write(RST_HEADER)
        section_counter = 0
        for group, requirements in grouped.items():
            section_counter += 1
            # Write section header
            req.write(f"\n.. _REQSEC{section_counter}:\n\n")
            req.write(f"{group}\n")
            req.write(f"{'-' * len(group)}\n\n")
            
            # Write each requirement in the group
            for req_item in requirements:
                req.write(f".. item:: {req_item['rid']} {req_item['name']}\n")
                req.write(f"    :status: not reviewed\n\n")
                req_text= wrap_text(req_item['req'], 80)
                req.write(f"{req_text}\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create requirements document', allow_abbrev=False)
    parser.add_argument('--json', help='JSON file to parse', required=True)
    parser.add_argument('--output', help='Output file to write to', required=True)
    parser.add_argument('--format', choices=['dox', 'rst'], default='dox', help='Output format (dox or rst)')

    args = parser.parse_args()

    grouped = parse_strictdoc_json(args.json)

    if args.format == 'dox':
        write_dox(grouped, args.output)
    elif args.format == 'rst':
        write_rst(grouped, args.output)
    else:
        sys.exit("Unsupported format specified")
