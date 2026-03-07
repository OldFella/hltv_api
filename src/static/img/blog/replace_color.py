import os

def main(filename):
    
    with open(filename, 'r') as f:
        svg = f.read()

    # replace hardcoded colors with css variable references
    svg = svg.replace('fill: #ff7f0e', 'fill: var(--accent)')
    svg = svg.replace('stroke: #1f77b4', 'stroke: var(--danger)')
    svg = svg.replace('fill: #020617', 'fill: var(--bg)')
    svg = svg.replace('fill: #0d1520', 'fill: var(--surface)')
    svg = svg.replace('fill: #1a2535', 'fill: var(--border)')
    svg = svg.replace('fill: #e5e7eb', 'fill: var(--text)')
    svg = svg.replace('stroke: #e5e7eb', 'stroke: var(--text)')
    svg = svg.replace('stroke: #1a2535', 'stroke: var(--border)')

    with open(filename, 'w') as f:
        f.write(svg)
if __name__ == "__main__":
    files = os.listdir()

    svgs = [file for file in files if '.svg' in file]

    for svg in svgs:
        main(svg)
