#!/usr/bin/env python3
"""
Simple converter: cppcheck XML -> human-friendly HTML report.
Usage:
    python3 tools/cppcheck_xml_to_html.py /path/to/cppcheck-report.xml /path/to/output.html

No external dependencies (uses Python stdlib).
"""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
import html

if len(sys.argv) != 3:
    print("Usage: cppcheck_xml_to_html.py input.xml output.html")
    sys.exit(2)

input_path = sys.argv[1]
output_path = sys.argv[2]

try:
    tree = ET.parse(input_path)
    root = tree.getroot()
except Exception as e:
    print(f"Failed to parse XML: {e}")
    sys.exit(1)

# cppcheck xml layout: <results><errors><error ...><location file="..." line="..."/></error>...</errors></results>
errors = root.findall('.//error')
by_file = defaultdict(list)
summary = defaultdict(int)

for err in errors:
    severity = err.get('severity','')
    eid = err.get('id','')
    msg = err.get('msg','')
    verbose = []
    for t in err:
        if t.tag == 'location':
            file = t.get('file','(unknown)')
            line = t.get('line','')
            by_file[file].append({'severity':severity,'id':eid,'msg':msg,'line':line,'raw':ET.tostring(err,encoding='unicode')})
            summary[severity]+=1
            break
    else:
        # no location tag
        by_file['(no-file)'].append({'severity':severity,'id':eid,'msg':msg,'line':'','raw':ET.tostring(err,encoding='unicode')})
        summary[severity]+=1

# generate HTML
html_parts = []
html_parts.append('<!doctype html>')
html_parts.append('<html><head><meta charset="utf-8"><title>cppcheck report</title>')
html_parts.append('<style>body{font-family:Segoe UI,Roboto,Arial, sans-serif;padding:18px} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:6px;text-align:left} th{background:#f2f2f2} .severity-error{background:#f8d7da} .severity-warning{background:#fff3cd} .severity-style{background:#d1ecf1} .severity-performance{background:#e2e3e5} pre{background:#fafafa;padding:8px;border:1px solid #eee;overflow:auto}</style>')
html_parts.append('</head><body>')
html_parts.append('<h1>cppcheck report</h1>')
html_parts.append('<h3>Summary</h3>')
html_parts.append('<ul>')
for sev,count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
    html_parts.append(f'<li><strong>{html.escape(sev)}</strong>: {count}</li>')
html_parts.append('</ul>')

html_parts.append('<h3>By file</h3>')
for file,items in sorted(by_file.items()):
    html_parts.append(f'<h4>{html.escape(file)} ({len(items)})</h4>')
    html_parts.append('<table>')
    html_parts.append('<thead><tr><th>Line</th><th>Severity</th><th>ID</th><th>Message</th></tr></thead>')
    html_parts.append('<tbody>')
    for it in items:
        sev = html.escape(it['severity'])
        cls = 'severity-'+sev if sev else ''
        html_parts.append(f'<tr class="{cls}"><td>{html.escape(it["line"])}</td><td>{html.escape(it["severity"])}</td><td>{html.escape(it["id"])}</td><td>{html.escape(it["msg"])}</td></tr>')
    html_parts.append('</tbody></table>')

html_parts.append('<h3>Full raw XML snippets (per error)</h3>')
for file,items in sorted(by_file.items()):
    html_parts.append(f'<h4>{html.escape(file)}</h4>')
    for idx,it in enumerate(items,1):
        html_parts.append(f'<details><summary>{html.escape(it["severity"])} - {html.escape(it["id"])} @ line {html.escape(it["line"])}</summary>')
        html_parts.append('<pre>')
        html_parts.append(html.escape(it['raw']))
        html_parts.append('</pre></details>')

html_parts.append('</body></html>')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_parts))

print(f'Wrote HTML report to: {output_path}')
