import argparse, json
import yaml
from .schema import Root
from .rules import map_branches, parse_branch, check_branch, expand_branch, apply, format_branch

def main():
    p = argparse.ArgumentParser()
    p.add_argument('path', help="path to doc yml")
    p.add_argument('spec', help="branch spec")
    args = p.parse_args()

    parsed = Root.parse_obj(yaml.safe_load(open(args.path)))
    branches, slots, address_map = map_branches(parsed)
    spec = parse_branch(args.spec)
    print('check', check_branch(branches, spec))
    expanded = expand_branch(branches, slots, spec)
    print('spec', spec)
    print('expanded', expanded)
    print('serial', format_branch(expanded))
    doc = apply(parsed, expanded, branches, slots, address_map)
    print(json.dumps(doc, indent=4))

if __name__ == '__main__':
    main()
