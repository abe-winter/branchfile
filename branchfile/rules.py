import collections, random, re
from dataclasses import dataclass
from typing import List, Dict, Union
from .schema import Root, BfList, BfDocBranch, BfAddressBranch

# List[str] is [tag]
# Dict[int, List[str]] is {slot: [tag]}
BranchOptions = Dict[str, Union[List[str], Dict[int, List[str]]]]

def map_branches(root: Root) -> BranchOptions:
    "return object with information about branch options"
    ret = {}
    slots = {}
    address_map = {}
    for key, val in root.base.items():
        if isinstance(val, BfList):
            if val.key not in ret:
                ret[val.key] = []
            if val.key not in slots:
                slots[val.key] = collections.defaultdict(list)
            for i, field in enumerate(val.fields):
                ret[val.key].append(field.tag)
                slots[val.key][field.slot].append(field.tag)
                address_map[val.key, field.tag] = ('base', key, i)
        elif isinstance(val, str):
            pass # nothing to do here
        elif isinstance(val, list):
            pass # assume no branches in here
        else:
            raise TypeError(f'unhandled type {type(val)} at {key}')
    for i, branch in enumerate(root.branches):
        if isinstance(branch, (BfDocBranch, BfAddressBranch)):
            if branch.key not in ret:
                ret[branch.key] = []
            ret[branch.key].append(branch.tag)
            address_map[branch.key, branch.tag] = ('branch', i)
        else:
            raise TypeError(f'unhandled type {type(branch)} at {i}')

    # convert {slot: values} to [values, values]
    for key, val in slots.items():
        opts = [()] * (max(val) + 1)
        for slot, vals in val.items():
            opts[slot] = vals
        slots[key] = opts

    return ret, slots, address_map

def parse_branch(raw: str) -> Dict[str, str]:
    sections = raw.split('.')
    return {
        section[0]: section[1:]
        for section in raw.split('.') if section
    }

def check_branch(branches, parsed_branch) -> list:
    "return list of missing fields from branch spec"
    not_found = []
    for key, val in parsed_branch.items():
        for letter in val:
            if (key, letter) not in branches:
                not_found.append((key, letter))
    return not_found

def expand_branch(branches, slots, parsed_branch):
    "fill in missing branch rules"
    # todo: switch with random logic when missing (rather than crashing)
    ret = {}
    for key, val in branches.items():
        if key in parsed_branch:
            ret[key] = parsed_branch[key]
        else:
            # todo: slotless random choice mode with length
            if key in slots:
                ret[key] = [random.choice(vals) for vals in slots[key]]
            else:
                ret[key] = random.choice(val)
    return ret

def set_address(doc, address, value):
    *parent_addr, child_addr = address
    parent = doc
    for key in parent_addr:
        parent = parent[int(key) if isinstance(parent, list) else key]
    parent[child_addr] = value

def apply(root: Root, spec, branches, slots, address_map) -> dict:
    "generate a merged copy of the doc using the (expanded) branch spec"
    doc = root.base.copy()
    for key, val in spec.items():
        if isinstance(val, str):
            source = address_map[key, val]
            if source[0] == 'branch':
                resolved = root.branches[source[1]]
                if isinstance(resolved, BfDocBranch):
                    doc.update(resolved.doc)
                elif isinstance(resolved, BfAddressBranch):
                    set_address(doc, resolved.address, resolved.value)
                else:
                    raise TypeError(f"unk source type {type(resolved)} at {source} in {key} {val}")
            else:
                raise NotImplementedError(f"source {source}")
        elif isinstance(val, list):
            # warning: empty case here totally broken
            slots = [address_map[key, subval] for subval in val]
            section, field = slots[0][:2]
            if section != 'base':
                raise NotImplementedError(f'todo: lookup {slots}')
            values = [
                root.base[field].fields[slot[2]].val
                for slot in slots
            ]
            doc[field] = values
        else:
            raise TypeError(f"unk type in apply {key} {val} {type(val)}")
    return doc
