'''Create attributes from family tree data
'''

import data
import findfamilies


def main():
    train_dataset = data.TitanicDataSet.load("data/csv/train.csv", True)
    people = [mark_problems(p, f) for f in findfamilies.construct_family_components(train=train_dataset, test=None)
              for p in f.nodes]
    result = synthesize(people)
    print(result[0])


def mark_problems(p, f):
    p.difficult_parent_child = f.difficult_parent_child
    return p


def synthesize(people):
    return [{key: fun(p) for key, fun in synthesized_attributes} for p in people]


def coere_attribute(v):
    return v


def calculate_spouse_survived(p):
    if p.spouse is not None and p.spouse.survived is not None:
        return int(p.spouse.survived)
    return -1


def iter_children(p):
    if not p.difficult_parent_child:
        for c in p.children:
            yield c
        return
    for e in p.edges:
        o = e.other(p)
        if e.definitive_child and findfamilies.child_parent_direction(p, o):
            yield o


def iter_parents(p):
    if not p.difficult_parent_child:
        for pp in p.known_parents:
            yield pp
        return
    for e in p.edges:
        o = e.other(p)
        if e.definitive_child and findfamilies.child_parent_direction(o, p):
            yield o


def iter_siblings(p):
    if not p.difficult_parent_child:
        for s in p.siblings:
            yield s
        return
    for e in p.edges:
        if e.definitive_sibling:
            yield e.other(p)


def iter_extended(p):
    if not p.difficult_parent_child:
        for e in p.extendeds:
            yield e
        return
    for e in p.edges:
        if e.definitive_extended:
            yield e.other(p)


def make_count(itr):
    return lambda p: sum(1 for o in itr(p))


def make_count_survived(itr):
    return lambda p: sum(1 for o in itr(p) if o.survived is True)


def make_count_died(itr):
    return lambda p: sum(1 for o in itr(p) if o.survived is False)


synthesized_attributes = [
    ('id', lambda p: p.id),
    ('firstname', lambda p: p.parsed_name.first),
    ('lastname', lambda p: p.parsed_name.last),
    ('title', lambda p: p.parsed_name.title),
    ('nickname', lambda p: p.parsed_name.nick),
    ('othername', lambda p: p.parsed_name.other),

    ('had_spouse', lambda p: p.spouse is not None),
    # ('spouse_survived', calculate_spouse_survived),

    ('n_children', make_count(iter_children)),
    # ('n_children_died', make_count_died(iter_children)),
    # ('n_children_survived', make_count_survived(iter_children)),
    ('n_parents', make_count(iter_parents)),
    # ('n_parents_died', make_count_died(iter_parents)),
    # ('n_parents_survived', make_count_survived(iter_parents)),

    ('n_sibling', make_count(iter_siblings)),
    # ('n_sibling_died', make_count_died(iter_siblings)),
    # ('n_sibling_survived', make_count_survived(iter_siblings))
]

__name__ == '__main__' and main()
