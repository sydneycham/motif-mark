#!/usr/bin/env python
from __future__ import annotations
import cairo 
import argparse
import re


#set defaults for cairo plotting
width, height = 1000, 1000

surface = cairo.PDFSurface("test.pdf", width, height)

context = cairo.Context(surface)

#set_custom_palette_color(index: int, red: float, green: float, blue: float, alpha: float)→ None


# Set up variables for legend
legend_x = 50
legend_y = 450
legend_spacing = 20
legend_font_size = 12

# Define legend labels and colors
legend_items = [("ygcy", (255, 0, 0)),
                ("GCAUG", (0, 255, 0)),   
                ("catag", (0, 0, 255)),
                ("YYYYYYYYYY", (0, 102, 102)),
                ("Exon", (0, 0, 0)),]   

# Draw legend
for label, color in legend_items:
    # Draw colored square
    context.set_source_rgb(*color)
    context.rectangle(legend_x, legend_y, 10, 10)
    context.fill()

    # Draw legend label
    context.set_source_rgb(0, 0, 0)  # Set text color to black
    context.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(legend_font_size)
    context.move_to(legend_x + 15, legend_y + 8)
    context.show_text(label)

    # Move to the next legend item
    legend_y += legend_spacing

# Save the surface to a PNG file
surface.write_to_png("legend.png")


def get_args():
    parser= argparse.ArgumentParser()
    parser.add_argument("-f", "--fasta", help="Fasta file", required=True, type = str)
    parser.add_argument("-m", "--motif", help="Motif file", required=True, type = str)
    parser.add_argument("-w", "--write", help="Output file", required=True, type = str)
    parser.add_argument("-ol", "--oneline", help="Oneline fasta intermediate file", required=False, type = str)

    return parser.parse_args()
 
args = get_args()
f=args.fasta
m=args.motif
w=args.write
ol=args.oneline

motif_reg_dict = {}
motif_reg_dict = {
        "A" : "[A]",
        "T" : "[T]",
        "G" : "[G]", 
        "C" : "[C]",
        "U" : "[TU]",
        "W" : "[AT]",
        "S" : "[CG]",
        "M" : "[AC]",
        "K" : "[GT]",
        "R" : "[AG]",
        "Y" : "[CT]",
        "B" : "[CGT]",
        "D" : "[AGT]",
        "H" : "[ACT]",
        "V" : "[ACG]",
        "N" : "[ACGT]",
    }

color_list = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 102, 102), (153, 0, 153)]


def convert_motif(string): 
    string = string.upper()
    verted_motif = ""
    for x in string: 
        verted_motif+=motif_reg_dict[x]
    return(verted_motif)
    

motif_dict = {}
with open(m, "r") as motifs:
    while True:
        line  = motifs.readline().strip()
        if (line == ""):
            break
        print(line)
        motif_dict[line] = len(line)

        # match_motif = re.findall(r'([c|t]gc[c|t])', line)
        # match_gene_name = re.findall(r'>([A-Za-z0-9]+)', line)

def oneline_fasta(f):
    with open(f, "r") as rf, open(w,"w") as wf:
        seq = ''
        while True:
            line = rf.readline().strip()
            if not line:
                break
            if line.startswith(">"):
                if seq != "":
                    wf.write(seq + "\n") 
                seq = ''
                wf.write(line + "\n") 
            else:
                seq += line 
        wf.write(seq)

oneline_fasta(f)


class Motif:
    def __init__(self, motif_seq, length, color, start_position):
        self.motif_seq = motif_seq
        self.length = length
        self.color = color
        self.start_position = start_position
        self.gene_name = gene_name

    #def draw function
    def motif_draw(self, x, y, name, length, start, end, color):
        context.set_line_width(10)
        context.set_source_rgb(*color)
        context.move_to(x + start, y)
        context.line_to(x + end, y)
        context.stroke()
 

class Gene:
    def __init__(self, name, length):
        self.name = name
        self.length = length
    #def draw function (self, x, y, name, length)
    def gene_draw(self, x, y, name, length):
        context.set_line_width(2)
        context.set_source_rgb(0, 0, 0)
        context.move_to(x, y)
        context.line_to(x + gene_length, y)
        context.stroke()
        context.set_source_rgba(0, 0, 0, 1)
        context.move_to(x+10, y+15)
        context.show_text(name)
        context.stroke()


class Exon:
    def __init__(self, start, end, gene):
        self.start = start
        self.end = end
        self.gene = gene


    def exon_draw(self, x, y, start, end, exon_length):
        context.set_line_width(10)
        context.set_source_rgb(0, 0, 0)
        context.move_to(x + start, y)
        context.line_to(end + exon_length, y)
        context.stroke()
        context.set_source_rgba(0, 0, 0, 1)
        
class Intron:
    def __init__(self, start, end, gene):
        self.start = start
        self.end = end
        self.gene = gene
    def intron_draw(self, x, y, intron_length):
        context.set_line_width(10)
        context.set_source_rgb(0, 0, 0)
        context.move_to(x, y)
        context.line_to(x + intron_length, y)
        context.stroke()
        context.set_source_rgba(0, 0, 0, 1)


with open(ol, 'r') as fasta:
    i = 0
    while True:
        header = fasta.readline().split()
        sequence = fasta.readline().split()
        if (header == []):
            break
        gene_name = header[0][1:]
        gene_length = len(sequence[0])
        #add gene to class
        newgene = Gene(header[0][1:], gene_length)
        print(f'the gene length is: {gene_length}')   
        #draw gene action
        newgene.gene_draw(20, 46+i, header[0][1:], gene_length)
        #extract exon by grabbing all capital letters
        Exon_pattern = re.compile("[AGCT]")
        exons = Exon_pattern.findall(sequence[0])
        # Find the exon using a regular expression
        exons_string = ''.join(exons)
        sequence = ''.join(sequence)
        match = re.search('[A-Z]+', sequence)
        if match:
            uppercase_section = match.group()  # Get the uppercase section
            exon_start = match.start()  # Get the start position of the uppercase section
            exon_end = match.end()
        else:
            pass
            #print("No uppercase section found in the sequence.")     
        if exons:
            exon_length = len(exons)
            print("Exon length:", exon_length)
        else:
            pass
            #print("No exons found in the sequence.")
        #add exon to class
        new_exon = Exon(exon_start, exon_end, newgene)
        new_exon.exon_draw(20, 50+i, exon_start, exon_end, exon_length)

        color_index = 0
        for m in motif_dict:
            converted_motif = convert_motif(m)
            upper_seq = sequence.upper()
            match_motif = re.finditer(converted_motif, upper_seq)
            
            
            previous_length = 4
            for match in match_motif:
                new_motif = Motif(m, motif_dict[m], color_list[color_index], match.start())
                new_motif.motif_draw(20, 42+i, m, motif_dict[m], match.start(), match.end(), color_list[color_index])
                if  new_motif.length != previous_length:
                    color_index += 1
                    print("doing th thing")
                previous_length = new_motif.length
                #print(new_motif.length)


        i+=100
