"""
Improving non-functional properties ::

    python improve_xml.py ../sample/Triangle_fast_xml
"""
import sys
import random
import argparse
import re
from pyggi.base import Patch, ParseError, AbstractProgram
from pyggi.tree import XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
from pyggi.algorithms import LocalSearch

class MyXmlEngine(XmlEngine):
    @classmethod
    def get_contents(cls, file_path):
        tree = XmlEngine.get_contents(file_path)
        print(cls.tree_to_string(tree))
        print('------------------------------------')
        cls.remove_tags(tree, ['class', 'specifier', 'name', 'block', 'enum', 'decl', 'function', 'type', 'parameter_list', 'parameter', 'expr', 'call', 'argument_list', 'argument', 'comment', 'condition', 'operator', 'then', 'else', 'elseif', 'init', 'literal', 'catch'])
        print('------------------------------------')
        print(cls.tree_to_string(tree))
        cls.rewrite_tags(tree, ['if', 'decl_stmt', 'expr_stmt', 'return', 'try'], 'stmt')
        print('------------------------------------')
        print(cls.tree_to_string(tree))
        cls.rotate_newlines(tree)
        print('------------------------------------')
        print(cls.tree_to_string(tree))
        print('------------------------------------')
        return tree

    @classmethod
    def remove_tags(cls, element, tags):
        last = None
        marked = []
        buff = 0
        for i, child in enumerate(element):
            cls.remove_tags(child, tags)
            if child.tag in tags:
                marked.append(child)
                if child.text:
                    if last is not None:
                        last.tail = last.tail or ''
                        last.tail += child.text
                    else:
                        element.text = element.text or ''
                        element.text += child.text
                if len(child) > 0:
                    for sub_child in reversed(child):
                        element.insert(i+1, sub_child)
                    last = child[-1]
                if child.tail:
                    if last is not None:
                        last.tail = last.tail or ''
                        last.tail += child.tail
                    else:
                        element.text = element.text or ''
                        element.text += child.tail
            else:
                last = child
        for child in marked:
            element.remove(child)

    @classmethod
    def rewrite_tags(cls, element, tags, new_tag):
        if element.tag in tags:
            element.tag = new_tag
        for child in element:
            cls.rewrite_tags(child, tags, new_tag)

    @classmethod
    def rotate_newlines(cls, element):
        if element.tail:
            match = re.match("(\n\s*)", element.tail)
            if match:
                element.tail = element.tail[len(match.group(1)):]
                if len(element) > 0:
                    element[-1].tail = element[-1].tail or ''
                    element[-1].tail += match.group(1)
                else:
                    element.text = element.text or ''
                    element.text += match.group(1)
        for child in element:
            cls.rotate_newlines(child)


class MyProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return MyXmlEngine

    def compute_fitness(self, elapsed_time, stdout, stderr):
        try:
            runtime, pass_all = stdout.strip().split(',')
            runtime = float(runtime)
            if not pass_all == 'true':
                raise ParseError
            return runtime
        except:
            raise ParseError

class MyLocalSearch(LocalSearch):
    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice([StmtDeletion, StmtInsertion, StmtReplacement])
            patch.add(edit_operator.create(program))
        return patch

    def stopping_criterion(self, iter, fitness):
        return fitness < 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()

    program = MyProgram(args.project_path)
    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15)
    print("======================RESULT======================")
    print(result)
    program.remove_tmp_variant()
