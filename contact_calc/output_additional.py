from __future__ import division
from collections import defaultdict

import json
import os
import errno

full_name_dirs = {'hbbb': 'hydrogen_bonds/backbone_backbone_hydrogen_bonds',
                  'hbsb': 'hydrogen_bonds/sidechain_backbone_hydrogen_bonds',
                  'hbss': 'hydrogen_bonds/sidechain_sidechain_hydrogen_bonds',
                  'vdw': 'van_der_Waals',
                  'sb': 'salt_bridges',
                  'ts': 't_stacking',
                  'ps': 'pi_stacking',
                  'pc': 'pi_cation',
                  'wb': 'hydrogen_bonds/water_mediated_hydrogen_bonds',
                  'wb2': 'hydrogen_bonds/extended_water_mediated_hydrogen_bonds',
                  'lhb': 'ligand_hydrogen_bonds/hydrogen_bonds',
                  'hlb': 'ligand_hydrogen_bonds/backbone_hydrogen_bonds',
                  'hls': 'ligand_hydrogen_bonds/sidechain_hydrogen_bonds',
                  'lwb': 'ligand_hydrogen_bonds/water_mediated_hydrogen_bonds',
                  'lwb2': 'ligand_hydrogen_bonds/extended_water_mediated_hydrogen_bonds',
                  }

def open_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def get_residue_from_atom(atom_name):
    split_atom_name = atom_name.split(':')
    return "%s:%s" % (split_atom_name[1], split_atom_name[2])


def create_dynamic_jsons(output_filename, interaction_to_frames, simulation_length):
    # Assemble and write out .json
    edges = []
    for interaction_pair in interaction_to_frames:  # loop over all residuepairs
        int1, int2 = interaction_pair.split('\t')
        edges.append({"name1":int1, "name2":int2, "frames":list(interaction_to_frames[interaction_pair])})
    with open(output_filename, 'w+') as fq:
        fq.write(json.dumps({"edges":edges, "simulation_length":simulation_length}, indent=2))


def create_frequencies_file(frequency_filename, residuepair_to_frames, simulation_length):
    # Write out .txt file
    with open(frequency_filename, 'w+') as fq:
        header = '\t'.join(['Res1','Res2','Freq','NumFrames','TotalFrames:%d' % simulation_length])
        fq.write('%s\n' % header)
        for interaction in residuepair_to_frames:
            numFrames = len(residuepair_to_frames[interaction])
            totalFrames = simulation_length
            interaction_frequency = numFrames / totalFrames
            interaction_line = '\t'.join([interaction,'%.8f'%interaction_frequency,'%d'%numFrames,'%d'%totalFrames])
            fq.write('%s\n' % interaction_line)


'''
def get_atompair_set(itype, stitched_lines):
    atompair_to_frames = defaultdict(set)
    for stitched_line in stitched_lines:
        frame = int(stitched_line[0])
        atom1 = stitched_line[1]
        atom2 = stitched_line[-2]
        atom_pair = ','.join(sorted([atom1, atom2]))
        atompair_to_frames[atom_pair].add(frame)
    return atompair_to_frames
    '''

def get_framesets(stitched_lines):
    atompair_to_frames = defaultdict(set)
    residuepair_to_frames = defaultdict(set)
    for stitched_line in stitched_lines:
        frame = int(stitched_line[0])
        atom1 = stitched_line[1]
        atom2 = stitched_line[-2]
        atompair = '\t'.join(sorted([atom1, atom2]))
        atompair_to_frames[atompair].add(frame)

        # Get residue from atom
        res1 = get_residue_from_atom(atom1)
        res2 = get_residue_from_atom(atom2)
        residuepair = '\t'.join(sorted([res1, res2]))
        residuepair_to_frames[residuepair].add(frame)

    #return atompair_to_frames, residuepair_to_frames
    return residuepair_to_frames


def make_additional_files(itype, output_dir, stitched_filename, simulation_length):
    with open(stitched_filename) as stitched_open:
        stitched_lines = [line.strip().split() for line in stitched_open.readlines()]

    residuepair_to_frames = get_framesets(stitched_lines)
    # atompair_to_frames = get_atompair_set(itype, stitched_lines)

    frequency_filename = output_dir + '/' + full_name_dirs[itype] + '/' + itype + "_frequencies.txt"
    byres_filename = output_dir + '/' + full_name_dirs[itype] +  '/' + itype + ".json"
    #byatom_filename = output_dir + '/' + itype + "_by_atom.json"

    create_frequencies_file(frequency_filename, residuepair_to_frames, simulation_length)
    create_dynamic_jsons(byres_filename, residuepair_to_frames, simulation_length)
    #create_dynamic_jsons(byatom_filename, atompair_to_frames, simulation_length)

