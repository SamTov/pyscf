#!/usr/bin/env python
#
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

import numpy as np
from pyscf import gto, symm
from pyscf.gto.basis import parse_molpro

'''
Read Molpro orbital coefficients

The Molpro orbital coefficients can be generated by matrop keyword.  Eg
executing Molpro with the input file
basis=vdz
geometry={
N1,0.  0.  1.
N2,0.  0. -1.
}
hf
{matrop
load,orb,orbitals,2100.2        !load orbitals
write,orb,orb.matrop,new        !write new orbitals to file orb.matrop
}
will generate orb.matrop file in the temporary directory.  orb.matrop file
saves the molecular orbital coefficients on symmetry adapted basis.  We can
read the coefficients and transform the orbitals to AO representation.
'''

mol = gto.M(atom='N 0 0 1; N 0 0 -1',
            basis={'N':parse_molpro.load('path/to/molpor/basis_name.libmol', 'N')},
            symmetry='d2h')
dat = open('orb.matrop').read().split('\n')
dat = ''.join(dat[2:-2])  # [2:-2] to skip comments
dat = np.array([float(x) for x in dat.split(',')[:-1]])  # [:-1] to remove last comma
dims = [7,3,3,1,7,3,3,1]  # orbitals in each irrep
off = 0
molpro_mo = []
for i, nd in enumerate(dims):
    molpro_mo.append(dat[off:off+nd**2].reshape(nd,nd))
    off += nd**2
mo = []
for i, ir in enumerate(mol.irrep_id):
    molpro_id = symm.param.IRREP_ID_MOLPRO['D2h'][ir]-1
    mo.append(np.dot(mol.symm_orb[i], molpro_mo[molpro_id]))
mo = np.hstack(mo)
# Check normalization to ensure no bug
print (np.einsum('ji,jk,ki->i', mo, mol.intor('cint1e_ovlp_sph'), mo))
