import argparse, json
import yaml
from .schema import Root, BfBoolBranch
from .rules import map_branches, parse_branch, check_branch, expand_branch, apply, format_branch

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command')
    # keys documentation command
    cmd_keys = sub.add_parser('keys', help="show available keys and tags")
    cmd_keys.add_argument('path', help="path to doc yml")
    # render command
    cmd_render = sub.add_parser('render', help="render a branch spec")
    cmd_render.add_argument('path', help="path to doc yml")
    cmd_render.add_argument('spec', help="branch spec")
    cmd_render.add_argument('-b', '--show-branch', action='store_true', help="show formatted branch")
    args = p.parse_args()

    parsed = Root.parse_obj(yaml.safe_load(open(args.path)))
    branches, slots, address_map, weights = map_branches(parsed)
    if args.command == 'keys':
        for key, tags in branches.items():
            if key in slots:
                addr = address_map[(key, tags[0])]
                print(f'list key "{key}"')
                print(f"- values {slots[key]}")
                print(f'- at "{addr[1]}"')
            else:
                print(f'branch key "{key}"')
                for tag in tags:
                    branch = parsed.branches[address_map[(key, tag)][1]]
                    print(f'- "{tag}"', branch, '(autobool)' if isinstance(branch, BfBoolBranch) else '')
    elif args.command == 'render':
        spec = parse_branch(args.spec)
        if (check_fail := check_branch(branches, spec)):
            raise ValueError('unknown keys', check_fail)
        expanded = expand_branch(branches, slots, weights, spec)
        if args.show_branch:
            print('spec', spec)
            print('expanded', expanded)
            print('serial', format_branch(expanded))
        doc = apply(parsed, expanded, slots, address_map)
        print(json.dumps(doc, indent=4))

if __name__ == '__main__':
    main()
