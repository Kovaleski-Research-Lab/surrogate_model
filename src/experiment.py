import os 
import time
import yaml
import torch
import logging
import argparse
import numpy as np
from IPython import embed

import train
from math import log10, floor
#import evaluate

def round_sig(x, sig=2):
    return round(x, sig-int(floor(log10(abs(x))))-1)

def begin_experiment(params):
    os.environ['TORCH_HOME'] = params['torch_home']
    train.run(params)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    parser = argparse.ArgumentParser()
    parser.add_argument("-config", help = "Experiment: Train and Eval LRN Network")
    args = parser.parse_args()
    if(args.config == None):
        logging.error("\nAttach Configuration File! Run experiment.py -h\n")
        exit()
    params = yaml.load(open(args.config), Loader = yaml.FullLoader)
    start_time = time.time()
    begin_experiment(params)
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f"elapsed time: {elapsed_time} minutes")

