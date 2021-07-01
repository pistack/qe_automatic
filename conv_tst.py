import os
import sys

def read_data(f):
    for line in f:
        if '!' in line:
            tmp = line.split()
            tmp = list(filter(None, tmp))
            energy = tmp[4]
            print(energy)
        elif 'P=' in line:
            tmp = line.split()
            tmp = list(filter(None, tmp))
            pressure = tmp[5]
            print(pressure)
        elif 'PWSCF        :' in line:
            tmp = line.split()
            tmp = list(filter(None, tmp))
            time = tmp[4].replace("s","")
        else:
            continue

    return energy, pressure, time

def dict_to_file(dic,fname):
    structure = ''
    for key,val in dic.items():
        structure += f'{key} {val}'
        structure += '\n'
    f = open(fname,'w')
    f.write(structure)
    f.close()
    return 0
        
        
if __name__ == "__main__" :
    
    prefix = sys.argv[1]
    if prefix == '-h':
        mode = 'h'
    else:
        mode = sys.argv[2]
        f = open(f'{sys.argv[1]}.in','r')
        template = f.read()
        f.close()

    if mode == 'k':
        ecutwfc = float(sys.argv[3])
        ratio = float(sys.argv[4])
        k_min = int(sys.argv[5])
        k_max = int(sys.argv[6])
        conve_k = {}
        convp_k = {}
        convp_t = {}
        for k in range(k_min,k_max+1):
            f = open('work.in','w')
            f.write(template.format(prefix,ecutwfc,ratio*ecutwfc,k,k,k))
            f.close()
            os.system('mpirun -np 4 ${QE_PATH}/bin/pw.x -in work.in > work.out')
            if os.path.isfile('CRASH'):
                continue
            else:
                f = open('work.out','r')
                e,p,t = read_data(f)
                conve_k[k]=e
                convp_k[k]=p
                convp_t[k]=t
                f.close()
                os.system(f'rm -rf {prefix}.save {prefix}.xml work.*')

        dict_to_file(conve_k,'k_vs_e.dat')
        dict_to_file(convp_k,'k_vs_p.dat')
        dict_to_file(convp_t,'k_vs_t.dat')
                
                
        
    elif mode == 'e':
        k = int(sys.argv[3])
        ratio = int(sys.argv[4])
        ecut_min = int(sys.argv[5])
        ecut_max = int(sys.argv[6])
        conve_ecut = {}
        convp_ecut = {}
        convt_ecut = {}
        for ecut in range(ecut_min,ecut_max+10,10):
            f = open('work.in','w')
            f.write(template.format(prefix,ecut,ratio*ecut,k,k,k))
            f.close()
            os.system('mpirun -np 4 ${QE_PATH}/bin/pw.x -in work.in > work.out')
            break
            if os.path.isfile('CRASH'):
                continue
            else:
                f = open('work.out','r')
                e,p,t = read_data(f)
                conve_ecut[ecut]=e
                convp_ecut[ecut]=p
                convt_ecut[ecut]=t
                f.close()
                os.system(f'rm -rf {prefix}.save {prefix}.xml work.*')

        dict_to_file(conve_ecut,'ecut_vs_e.dat')
        dict_to_file(convp_ecut,'ecut_vs_p.dat')
        dict_to_file(convt_ecut,'ecut_vs_t.dat')
        
    else:
        help= '''Automatic script for convergence test
Currently supports two mode 
k: k-point convergence tst
command: python3 conv_tst.py file_name k ecutwfc ratio k_min k_max
e: ecut convergence tst
command: python3 conv_tst.py file_name e kpoints ratio ecut_min ecut_max
'''
        print(help)
        
    
