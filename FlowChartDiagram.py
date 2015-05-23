#! /usr/bin/python3
# FlowChartDiagram
# Copyright (C) 2015 LEVY-FALK Hugo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Organisation d'un fichier:

st=>start:Titre
e=>end:Titre
s1=>subroutine:Titre
o1=>operation:Titre
io=>inputoutput:Titre

st->io->s1->o1->e

init := name=>function:title

expr := name->expr
     |  name(port)->expr
     |  name
     |  name(port)

name := CHAR

title := CHAR

port := left
      | right
      | top
      | bottom

function := start
          | end
          | subroutine
          | operation
          | inputoutput
"""
import re


class Link:

    def __init__(self, begin, end, diagram, attach_beg="bottom"):
        self.begin = begin
        self.end = end
        self.attach_beg = attach_beg
        self.diagram = diagram
        self.points = []

    def calc_points(self):
        if self.attach_beg is "bottom":
            bx = self.begin.attach['bottom'][0]
            by = self.begin.attach['bottom'][1]
            step_by = by + self.begin.bottom*13
            ex = self.end.attach['top'][0]
            ey = self.end.attach['top'][1]
            step_ey = ey - self.end.top*13
            if by > ey:
                left = self.diagram.get_left()
                self.points = [(bx, by), (bx, step_by), (left, step_by), (left, step_ey), (ex, step_ey), (ex, ey)]
            else:
                self.points = [(bx,by),(bx,step_by),(ex,step_by),(ex,ey)]
        else:  # i.e. is "right"
            bx = self.begin.attach['right'][0]
            by = self.begin.attach['right'][1]
            if self.end.pos[1] is not self.begin.pos[1]:
                right = self.diagram.get_right()
                ex = self.end.attach['top'][0]
                ey = self.end.attach['top'][1]
                step_ey = ey - self.end.top*13
                self.points = [(bx, by), (right, by), (right, step_ey), (ex, step_ey), (ex, ey)]
            else:
                ex = self.end.attach['left'][0]
                ey = self.end.attach['left'][1]
                self.points = [(bx, by), (ex, ey)]

    def get_draw_code(self):
        points = "M{} {} ".format(*self.points[0])
        for i in self.points[1:]:
            points += "L{} {} ".format(*i)
        return "<path d='{}' fill='transparent' stroke='#000000' stroke-width='2' style='marker-end: url(#markerArrow);'/>\n".format(points)


class Element:

    def __init__(self, name, title):
        self.row = 0
        self.bottom = 1
        self.top = 1
        self.positionned = False
        self.name = name
        self.title = title

        self.cell_width = 0

        self.pos = (0, 0)
        self.width = 0

        self.attach = {
            'left': (0, 0),
            'right': (0, 0),
            'bottom': (0, 0),
            'top': (0, 0),
        }
        self.link = {
            'left': '',
            'right': '',
            'bottom': '',
            'top': '',
        }
        self.width = len(self.title) * 7 + 10 * 2

    def set_pos(self, pos, cell_width):
        self.cell_width = cell_width
        self.pos = (pos[0] + (self.cell_width - self.width) / 2, pos[1])

    def set_link(self, side, linked):
        self.link[side] = linked

    def __str__(self):
        return ''.join([self.name, ' : ', self.title])

    def get_draw_code(self):
        return ""

    def calc_attach_pos(self):
        self.attach['left'] = (self.pos[0], self.pos[1] + 36 / 2)
        self.attach['right'] = (self.pos[0] + self.width, self.pos[1] + 36 / 2)
        self.attach['top'] = (self.pos[0] + self.width / 2, self.pos[1])
        self.attach['bottom'] = (
            self.pos[0] + self.width / 2, self.pos[1] + 36)


class StartEnd(Element):

    def get_draw_code(self):
        return """<g transform="translate({},{})">
        <text x='10px' y='14px' style=' font: 14px "monospace";' font-size="14px" textLength="{}"><tspan dy="8.5">{}</tspan></text>
   <rect width='{}' height='36' rx='20' fill="transparent" stroke='#000000' stroke-width='2'/>
</g>""".format(self.pos[0], self.pos[1], self.width - 10 * 2, self.title, self.width)


class Start(StartEnd):

    def block_type(self):
        return "start"


class End(StartEnd):

    def block_type(self):
        return "end"


class Subroutine(Element):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = len(self.title) * 7 + 20 * 2

    def block_type(self):
        return "subroutine"

    def get_draw_code(self):
        return """<g transform="translate({},{})">
        <text x='10px' y='14px' style=' font: 14px "monospace";' font-size="14px" textLength="{}"><tspan dy="8.5">{}</tspan></text>
        <rect width='{}' height='36' x='5' fill="transparent" stroke='#000000' stroke-width='2'/>
        <rect width='{}' height='36' fill="transparent" stroke='#000000' stroke-width='2'/>
</g>""".format(self.pos[0], self.pos[1], self.width - 10 * 2, self.title, self.width - 10, self.width)


class InputOutput(Element):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = len(self.title) * 7 + 20 * 2

    def block_type(self):
        return "inputoutput"

    def get_draw_code(self):
        return """<g transform="translate({},{})">
        <text x='10px' y='14px' style=' font: 14px "monospace";' font-size="14px" textLength="{}"><tspan dy="8.5">{}</tspan></text>
        <path d="M0 0 L{} 0 L{} 36 L10 36 Z" fill="transparent" stroke='#000000' stroke-width='2'/>
</g>""".format(self.pos[0], self.pos[1], self.width - 10 * 2, self.title, self.width - 10, self.width)

    def calc_attach_pos(self):
        super().calc_attach_pos()
        self.attach['left'] = (self.attach['left'][0]+5, self.attach['left'][1])
        self.attach['right'] = (self.attach['right'][0]-5, self.attach['right'][1])


class Operation(Element):

    def block_type(self):
        return "operation"

    def get_draw_code(self):
        return """<g transform="translate({},{})">
        <text x='10px' y='14px' style=' font: 14px "monospace";' font-size="14px" textLength="{}"><tspan dy="8.5">{}</tspan></text>
   <rect width='{}' height='36' fill="transparent" stroke='#000000' stroke-width='2'/>
</g>""".format(self.pos[0], self.pos[1], self.width - 10 * 2, self.title, self.width)


class Condition(Element):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = len(self.title) * 7 + 20 * 3

    def block_type(self):
        return "condition"

    def get_draw_code(self):
        return """<g transform="translate({},{})">
        <text x='20px' y='14px' style=' font: 14px "monospace";' font-size="14px" textLength="{}"><tspan dy="8.5">{}</tspan></text>
        <path d="M0 18 L{} -14 L{} 18 L{} 50 Z" fill="transparent" stroke='#000000' stroke-width='2'/>
        <text x='{}' y='{}' style=' font: 12px "monospace";' font-size="12px">No</text>
        <text x='{}' y='{}' style=' font: 12px "monospace";' font-size="12px">Yes</text>
</g>""".format(self.pos[0], self.pos[1], self.width - 10 * 4, self.title, self.width/2, self.width, self.width/2, self.width, 11, self.width/2+4, 60)

    def calc_attach_pos(self):
        super().calc_attach_pos()
        self.attach['top'] = (self.attach['top'][0], self.attach['top'][1]-14)
        self.attach['bottom'] = (self.attach['bottom'][0], self.attach['bottom'][1]+14)


class ParseError(Exception):
    pass


class Parser:
    FIND_INIT = re.compile(r'^\w+=>[\w\(\)]+:[\w\ \'\?\.]+$')
    FIND_LINK = re.compile(r'^([\w\(\)]+->)+[\w\(\)]+$')
    FIND_ARGUMENT = re.compile(r'^\w+(\((?P<arg>\w+)\))?$')

    BLOCK_NAME = {
        'start': Start,
        'end': End,
        'subroutine': Subroutine,
        'inputoutput': InputOutput,
        'operation': Operation,
        'condition': Condition,
    }

    def __init__(self, input_str):
        self.input = input_str.split('\n')

    def parse(self):
        parsed = []
        for x, i in enumerate(self.input):
            if i is '':
                pass
            elif self.FIND_INIT.match(i):
                parsed += self.parse_init(i)
            elif self.FIND_LINK.match(i):
                parsed += self.parse_link(i)
            else:
                raise ParseError("Ligne {} non reconnue : {}".format(x, i))
        return parsed

    def parse_init(self, init_line):
        name, initial = init_line.split('=>')
        block_name, title = initial.split(':')

        try:
            block = self.BLOCK_NAME[block_name]
        except KeyError:
            raise ParseError("Block inconnu : {}".format(block_name))

        return [('INIT', block(name, title))]

    def parse_link(self, init_line):
        if init_line == '' or len(init_line.split('->')) < 2:
            return []
        begin = self.parse_slot(init_line.split('->')[0])
        end = init_line.split('->')[1].split("(")[0]
        return [('LINK', begin, end)] + self.parse_link('->'.join(init_line.split('->')[1:]))

    def parse_slot(self, init_str):
        a = self.FIND_ARGUMENT.match(init_str)
        if not a:
            raise ParseError("Mauvais nom: {}".format(init_str))

        arg = a.groupdict()['arg']
        if arg and (not arg in ['bottom', 'right', 'yes', 'no']):
            raise ParseError("Argument inconnu : {}".format(arg))
        name = init_str.split("(")[0]
        return (name, arg)


class LinkError(Exception):
    pass


class Diagram:

    def __init__(self, prgm):
        self.blocks = {}
        self.links = []
        self.start = ""

        self.rows_block = []
        self.rows_link = []
        self.column_size = []
        self.left = 0
        self.right = 0
        self.from_prgm(prgm)

    def get_left(self):
        self.left -= 10
        return self.left

    def get_right(self):
        self.right += 10
        return self.right

    def from_prgm(self, prgm):
        for i in prgm:
            if i[0] is 'INIT':
                if i[1].block_type() is "start":
                    self.start = i[1].name
                self.blocks[i[1].name] = i[1]
            else:
                self.add_link(*i[1:])
        if self.start is "":
            raise LinkError("Erreur, pas de point d'entrée.")
        self.manage_all_pos()
        self.manage_links()
        self.calc_pos()

    def add_link(self, orig, end):
        if orig[1] is not None:
            equivalence = {
                "yes": "bottom",
                "no": "right",
                "right": "right",
                "bottom": "bottom",
            }
            self.blocks[orig[0]].set_link(equivalence[orig[1]], end)
        else:
            self.blocks[orig[0]].set_link('bottom', end)

    def __str__(self):
        r = ""
        for i in self.rows:
            for j in i:
                if j is None:
                    r += "    "
                else:
                    r += j.name + "  "
            r += "\n"
        return r

    def manage_all_pos(self):
        current = self.blocks[self.start]
        end = False
        row = []
        y = 0
        while not end:
            row.append(current)
            current.positionned = True
            if len(self.column_size) < len(row):
                self.column_size.append(current.width)            
            try:
                current = self.blocks[current.link['right']]
                if current.positionned:
                    end = True
            except KeyError:
                end = True
            current.row = y
        self.rows_block.append(list(row))
        while len(row) is not 0:
            row = self.manage_pos(row, y)
            y += 1
            self.rows_block.append(list(row))
        for i in self.rows_block:
            for j in i:
                if j:
                    self.blocks[j.name] = j

    def manage_pos(self, precedly, y):
        r = []
        for i in precedly:
            if i is None:
                pass
            elif i.link['bottom'] is '':
                r.append(None)
            else:
                c = self.blocks[i.link['bottom']]
                if not c.positionned:
                    c.positionned = True
                    c.row = y
                    r.append(c)

                    if len(self.column_size) < len(r):
                        self.column_size.append(c.width)
                    elif self.column_size[len(r)-1] < c.width:
                        self.column_size[len(r)-1] = c.width    
                    quit = False
                    while not quit:
                        try:
                            c = self.blocks[c.link['right']]
                        except:
                            break
                        if not c.positionned:
                            c.positionned = True
                            c.row = y
                            r.append(c)
                            if len(self.column_size) < len(r):
                                self.column_size.append(c.width)
                            elif self.column_size[len(r)-1] < c.width:
                                self.column_size[len(r)-1] = c.width
                        else:
                            quit = True
        return r

    def manage_links(self):
        self.rows_link = [list([0,0]) for i in range(len(self.rows_block))]
        links_eq = {
            "right": "left",
            "bottom": "top"
        }
        for b in self.blocks.values():
            if b.link['bottom'] is not '':
                self.rows_link[b.row][1] += 1
                self.rows_link[self.blocks[b.link['bottom']].row][0] += 1
                b.bottom = self.rows_link[b.row][1] + 1
                self.blocks[b.link['bottom']].top = self.rows_link[self.blocks[b.link['bottom']].row][0]+1
            if b.link['right'] is not '' and self.blocks[b.link['right']].row is not b.row:
                self.rows_link[self.blocks[b.link['right']].row][0] += 1
                self.blocks[b.link['right']].top = self.rows_link[self.blocks[b.link['right']].row][0]+1

            for v in b.link.keys():
                if b.link[v] in self.blocks.keys():
                    l = Link(b, self.blocks[b.link[v]], self, attach_beg=v)
                    self.links.append(l)

    def calc_pos(self):
        y = 0
        for l,i in enumerate(self.rows_block):
            x = 0
            row_width = 0
            for j,k in enumerate(i):
                if k :
                    k.set_pos((x,y), self.column_size[j])
                    k.calc_attach_pos()
                    x += self.column_size[j] + 20
                row_width += x
            if l+1 < len(self.rows_link):
                y += (self.rows_link[l][1] + self.rows_link[l+1][0])*10 + 80
        self.right = sum(self.column_size) + 20*len(self.column_size)
        for i in self.links:
            i.calc_points()


def print_prgm(prgm):
    for i in prgm:
        print(i)


class Drawer(object):

    def __init__(self, diagram):
        self.diagram = diagram
        self.svg = ""

    def draw(self):
        self.diagram.right
        blocks = ""
        links = ""
        for i in self.diagram.blocks.values():
            blocks += i.get_draw_code()
        for i in self.diagram.links:
            links += i.get_draw_code()
        self.svg = """<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg width="100%" height="100%" xml:lang="fr"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<marker id="markerArrow" markerWidth="5" markerHeight="5" orient="auto" refX="5" refY="2.5">
    <path style="fill: #000000;" d="M0,0 L0,5 L5,2.5 L0,0"></path>
</marker>
<g transform="translate(30,30)">
{}
{}
</g>
</svg>""".format(blocks, links)
        return self.svg


def diagram(str_in):
    d = Diagram(Parser(str_in).parse())
    return Drawer(d).draw()

if __name__ == "__main__":
    IN = """st=>start: Start
e=>end: End
op1=>operation: My Operation
sub1=>subroutine: My Subroutine
cond=>condition: Yes or No?
io=>inputoutput: catch something ...
op2=>operation:test
op3=>operation:test

st->op1->cond
cond(yes)->io->e->st
cond(no)->sub1(right)->op1
op1(right)->op2(right)->op3->sub1->io(right)->op2
"""
    with open("test.svg", "w") as fic:
        fic.write(diagram(IN))
