import copy
import re
from . import AbstractTreeEngine
from xml.etree import ElementTree

class XmlEngine(AbstractTreeEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path) as target_file:
            return cls.string_to_tree(target_file.read())

    @classmethod
    def get_modification_points(cls, contents_of_file):
        def aux(accu, prefix, root):
            tags = dict()
            for child in root:
                if child.tag in tags:
                    tags[child.tag] += 1
                else:
                    tags[child.tag] = 1
                s = '{}/{}[{}]'.format(prefix, child.tag, tags[child.tag])
                accu.append(s)
                accu = aux(accu, s, child)
            return accu
        return aux([], '.', contents_of_file)

    @classmethod
    def get_source(cls, program, file_name, index):
        # never used?
        return cls.dump(program.contents[file_name].find(program.modification_points[file_name][index]))

    @classmethod
    def write_to_tmp_dir(cls, contents_of_file, tmp_path):
        assert tmp_path[-4:] == '.xml'
        with open(tmp_path[:-4], 'w') as tmp_file:
            tmp_file.write(cls.dump(contents_of_file))

    @classmethod
    def dump(cls, contents_of_file):
        return cls.strip_xml_from_tree(contents_of_file)


    @staticmethod
    def string_to_tree(s):
        xml = re.sub(r'(?:\s+xmlns[^=]*="[^"]+")+', '', s, count=1)
        xml = re.sub(r'<(/?)[^>]+:([^:>]+)>', r'<\1\2>', xml)
        try:
            return ElementTree.fromstring(xml)
        except ElementTree.ParseError as e:
            raise Exception('Program', 'ParseError: {}'.format(str(e))) from None

    @staticmethod
    def tree_to_string(tree):
        return ElementTree.tostring(tree, encoding='unicode', method='xml')

    @staticmethod
    def strip_xml_from_tree(tree):
        return ''.join(tree.itertext())

    @staticmethod
    def split_xpath(xpath, prefix=None):
        assert xpath != '.'
        if prefix is None:
            pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
            match = re.match(pattern, xpath)
            assert match
            return (match.group(1), match.group(2), int(match.group(3)), None)
        else:
            if xpath[:len(prefix)+1] == prefix+'/':
                pattern = re.compile(r'^/([^\[]+)(?:\[([^\]]+)\])?(?:/(.*))?$')
                match = re.match(pattern, xpath[len(prefix):])
                assert match
                return (prefix, match.group(1), int(match.group(2)), match.group(3))
            else:
                return (None, None, None, None)


    @classmethod
    def do_replace(cls, program, op, new_contents, modification_points):
        # get elements
        target = new_contents[op.target[0]].find(modification_points[op.target[0]][op.target[1]])
        ingredient = program.contents[op.ingredient[0]].find(program.modification_points[op.ingredient[0]][op.ingredient[1]])
        if target is None or ingredient is None:
            return False
        if target == ingredient:
            return True

        # mutate
        old_tag = target.tag
        old_tail = target.tail
        target.clear() # to remove children
        target.tag = ingredient.tag
        target.attrib = ingredient.attrib
        target.text = ingredient.text
        target.tail = old_tail
        for child in ingredient:
            target.append(copy.deepcopy(child))

        # update modification points
        if old_tag != ingredient.tag:
            head, tag, pos, _ = cls.split_xpath(modification_points[op.target[0]][op.target[1]])
            itag = 1
            for i, pos in enumerate(modification_points[op.target[0]]):
                h, t, p, s = cls.split_xpath(pos, head)
                if i < op.target[1]:
                    if h != head:
                        continue
                    elif t == ingredient.tag:
                        itag += 1
                elif i == op.target[0]:
                    modification_points[i] = '{}/{}[{}]'.format(h, t, itag)
                elif h != head:
                    break
                elif t == tag:
                    if s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p-1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p-1)
                    modification_points[op.target[0]][i] = new_pos
                elif t == ingredient.tag:
                    if s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p+1)
                    modification_points[op.target[0]][i] = new_pos
        return True

    @classmethod
    def do_insert(cls, program, op, new_contents, modification_points):
        # get elements
        target = new_contents[op.target[0]].find(modification_points[op.target[0]][op.target[1]])
        parent = new_contents[op.target[0]].find(modification_points[op.target[0]][op.target[1]]+'..')
        ingredient = program.contents[op.ingredient[0]].find(program.modification_points[op.ingredient[0]][op.ingredient[1]])
        if target is None or ingredient is None:
            return False

        # mutate
        for i, child in enumerate(parent):
            if child == target:
                tmp = copy.deepcopy(ingredient)
                tmp.tail = None
                if op.direction == 'after':
                    i += 1
                parent.insert(i, tmp)
                break
        else:
            assert False

        # update modification points
        head, tag, pos, _ = cls.split_xpath(modification_points[op.target[0]][op.target[1]])
        buff = 1 if op.direction == 'after' else 0
        for i, pos in enumerate(modification_points[op.target[0]]):
            if i < op.target[1] + buff:
                continue
            h, t, p, s = cls.split_xpath(pos, head)
            if h != head:
                break
            if t == ingredient.tag:
                if s:
                    new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
                else:
                    new_pos = '{}/{}[{}]'.format(h, t, p+1)
                modification_points[op.target[0]][i] = new_pos
        return True

    @classmethod
    def do_delete(cls, program, op, new_contents, modification_points):
        # get elements
        target = new_contents[op.target[0]].find(modification_points[op.target[0]][op.target[1]])
        if target is None:
            return False

        # mutate
        old_tag = target.tag
        old_tail = target.tail
        target.clear() # to remove children
        target.tag = old_tag
        target.tail = old_tail
        return True
