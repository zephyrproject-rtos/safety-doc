#!/usr/bin/env python3
# Copyright (c) 2024 Intel Corp.
# SPDX-License-Identifier: Apache-2.0

import sys
import argparse
import json
import textwrap
import re

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
            uid = n.get('UID')
            title = n['TITLE']
            statement= n['STATEMENT']
            status = n.get('STATUS', None)
            component = n.get('COMPONENT', None)
            rtype = n.get('TYPE', None)
            relations = n.get('RELATIONS', [])
            if not component:
                debug("No group for {}".format(uid))
                continue
            if not grouped.get(component, None):
                grouped[component] = []
            grouped[component].append(
                {'uid': uid, 
                 'statement': statement, 
                 'title': title,
                 'status': status,
                 'component': component,
                 'type': rtype,
                 'relations': relations,
                 }
                 )

    return grouped

def parse_strictdoc_json(filename):
    documents = {}
    with open(filename) as fp:
        data = json.load(fp)
        docs = data.get('DOCUMENTS')
        for d in docs:
            grouped = dict()
            doc = d.get('TITLE')
            print(f"Parsing document {doc}")
            parse_nodes(d['NODES'], grouped)
            documents[doc] = grouped
    return documents

def write_dox(grouped):
    counter = 0
    for doc in docs.keys():
        fname = to_valid_filename(doc)
        output = f"{fname}.dox"
        grouped = docs[doc]
        with open(output, "w") as req:
            req.write(f"/**\n")
            req.write(f"@page {fname} {doc}\n")
            req.write(f"@tableofcontents\n\n")
            for r in grouped.keys():
                comp = grouped[r]
                counter += 1
                req.write(f"\n@section REQSEC{counter} {r}\n\n")
                for c in comp:
                    req.write("@subsection {} {}: {}\n{}\n\n\n".format(c['uid'], c['uid'], c['title'], c['statement']))

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


def to_valid_filename(input_str):
    # Convert to lowercase
    filename = input_str.lower()
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove invalid characters (keep letters, numbers, underscores, and hyphens)
    filename = re.sub(r'[^a-z0-9_\-]', '', filename)
    return filename

def write_rst(docs):
    section_counter = 0
    for doc in docs.keys():
        fname = to_valid_filename(doc)
        output = f"{fname}.rst"
        grouped = docs[doc]
        with open(output, "w") as req:
            req.write(f"{doc}\n")
            req.write(f"{'*' * len(doc)}\n\n")
            for group, requirements in grouped.items():
                section_counter += 1
                # Write section header
                req.write(f"\n.. _REQSEC{section_counter}:\n\n")
                req.write(f"{group}\n")
                req.write(f"{'=' * len(group)}\n\n")

                # Write each requirement in the group
                for req_item in requirements:
                    req.write(f".. item:: {req_item['uid']} {req_item['title']}\n")
                    req.write(f"    :status: {req_item['status']}\n")
                    req.write(f"    :rtype: {req_item['type']}\n")
                    req.write(f"    :uid: {req_item['uid']}\n")
                    req.write(f"    :component: {req_item['component']}\n")
                    req.write("\n")
                    if req_item['relations']:
                        for r in req_item['relations']:
                            req.write(f"    .. item-link::\n")
                            req.write(f"        :sources: {req_item['uid']}\n")
                            req.write(f"        :targets: {r['VALUE']}\n")
                            req.write(f"        :type: parent\n")

                        req.write("\n")
                    req_text= wrap_text(req_item['statement'], 80)
                    req.write(f"{req_text}\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create requirements document', allow_abbrev=False)
    parser.add_argument('--json', help='JSON file to parse', required=True)
    parser.add_argument('--format', choices=['dox', 'rst'], default='dox', help='Output format (dox or rst)')

    args = parser.parse_args()

    docs = parse_strictdoc_json(args.json)

    if args.format == 'dox':
        write_dox(docs)
    elif args.format == 'rst':
        write_rst(docs)
    else:
        sys.exit("Unsupported format specified")
