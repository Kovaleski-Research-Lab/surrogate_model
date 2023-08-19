import os
import sys
import yaml
import torch 
import pickle
import numpy as np
from tqdm import tqdm
from numpy.polynomial.polynomial import Polynomial
from IPython import embed

sys.path.append('../')
from utils import parameter_manager
from utils import mapping

from core import curvature
#from core import propagator

#def propagate_fields(prop, near_fields):
#    #We will assume we can just propagate them individually... #TODO
#    far_fields = [] 
#    for f in near_fields.squeeze():
#        far_fields.append(prop(f).unsqueeze(dim=0))
#        
#    return torch.cat(far_fields, dim=0)

def radii_to_phase(radii):
    mapper = pickle.load(open("/develop/code/src/core/radii_to_phase.pkl", 'rb'))
    phases = torch.from_numpy(Polynomial(mapper)(radii.numpy()))
    phases =  torch.clamp(phases, min=-torch.pi, max=torch.pi)
    return phases

def constrain_values(value):
    return torch.nn.functional.sigmoid(value)

def preprocess_data(raw_data_files = None, path = None):
    params = yaml.load(open('/develop/code/src/config.yaml', 'r'),
                                    Loader = yaml.FullLoader)
    pm = parameter_manager.ParameterManager(params = params)
#    prop = propagator.Propagator(pm.params_propagator)
    
    near_fields = []
#    far_fields = []
    phases = []
    radii = []
    der = []
    count = 0
    if raw_data_files is None:
        raw_data_files = os.listdir(path)
       
    for f in tqdm(raw_data_files, desc="Preprocessing data"):
        if '.pkl' in f:

            path = "/develop/results/" # KUBE
            #path = "/develop/data/spie_journal_2023/data_subset"
            
            data = pickle.load(open(os.path.join(path, f), "rb"))
            count += 1
            print(f"count = {count} file = {os.path.join(path,f)}")
        else:
            pass

        dft_fields = data['near_fields']
        print("dft_fields")
        nf_ex = torch.from_numpy(dft_fields['grating_ex']).unsqueeze(dim=0)
        nf_ey = torch.from_numpy(dft_fields['grating_ey']).unsqueeze(dim=0)
        nf_ez = torch.from_numpy(dft_fields['grating_ez']).unsqueeze(dim=0)

        temp = torch.cat([nf_ex, nf_ey, nf_ez], dim=0).unsqueeze(dim=0)
        print("temp")
        near_fields_mag = temp.abs().unsqueeze(dim=2)
        near_fields_angle = temp.angle().unsqueeze(dim=2)
        near_fields.append(torch.cat((near_fields_mag, near_fields_angle), dim=2))

        #temp = propagate_fields(prop, temp).unsqueeze(dim=0)

        #far_fields_mag = temp.abs().unsqueeze(dim=2)
        #far_fields_angle = temp.angle().unsqueeze(dim=2)

        #far_fields.append(torch.cat((far_fields_mag, far_fields_angle), dim=2))
        print("radii")
        radii.append(torch.from_numpy(np.asarray(data['radii'])).unsqueeze(dim=0))

        #temp_phases = radii_to_phase(radii[-1])
        temp_phases = torch.from_numpy(mapping.radii_to_phase(radii[-1]))
        #embed();exit()        

        #phases.append(constrain_values(temp_phases))
        phases.append(temp_phases)
        
        temp_der = curvature.get_der_train(temp_phases.view(1,3,3))
        #der.append(constrain_values(temp_der))
        der.append(temp_der)
        print("bout to save")
    near_fields = torch.cat(near_fields, dim=0).float()
    #far_fields = torch.cat(far_fields, dim=0).float()
    radii = torch.cat(radii, dim=0).float()
    phases = torch.cat(phases, dim=0).float()
    der = torch.stack(der).float()

    data = {'near_fields' : near_fields,    
#            'far_fields' : far_fields, 
            'radii' : radii, 
            'phases' : phases,
            'derivatives' : der,}
    path_save = '/develop/results/preprocessed' #KUBE
    #path_save = '/develop/data/spie_journal_2023/data_subset/preprocessed'
    torch.save(data, os.path.join(path_save, 'pp_data.pt'))

if __name__=="__main__":
    folder = os.listdir('/develop/results') # KUBE
    #folder = os.listdir('/develop/data/spie_journal_2023/data_subset')
    raw_data_files = []
    for filename in folder:
        if filename.endswith(".pkl"):
            raw_data_files.append(filename)
    preprocess_data(raw_data_files = raw_data_files)
