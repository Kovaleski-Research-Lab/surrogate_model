#--------------------------------
# Import: Basic Python Libraries
#--------------------------------

from IPython import embed
import os
import yaml
import torch
import signal
import logging
from pytorch_lightning.strategies import DDPStrategy
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import ModelCheckpoint

#--------------------------------
# Import: Custom Python Libraries
#--------------------------------

from core import datamodule, model, custom_logger, curvature
from utils import parameter_manager, model_loader

#--------------------------------
# Initialize: Training
#--------------------------------
  
def run(params):
    OMP_NUM_THREADS=1
    logging.debug("train.py() | running training")
    #logging.basicConfig(level=logging.DEBUG)

    # Initialize: Parameter manager
    pm = parameter_manager.ParameterManager(params=params)
          
    # Initialize: Seeding
    if(pm.seed_flag):
        seed_everything(pm.seed_value, workers = True)

    # Initialize: The model
    model = model_loader.select_model(pm)

    print("model initialized")

    # Initialize: The datamodule
    data = datamodule.select_data(pm.params_datamodule)
    # Initialize: The logger
    logger = custom_logger.Logger(all_paths=pm.all_paths, name=pm.model_id, version=0)

    # Initialize:  PytorchLighting model checkpoint
    checkpoint_path = os.path.join(pm.path_root, "results/spie_journal_2023", pm.model_id, "checkpoints")
    checkpoint_callback = ModelCheckpoint(dirpath = checkpoint_path)
    
    #logging.debug(f'Checkpoint path: {checkpoint_path}')

    logging.debug('Setting matmul precision to HIGH')
    torch.set_float32_matmul_precision('high')

    # Initialize: PytorchLightning Trainer
    if(pm.gpu_flag and torch.cuda.is_available()):
        logging.debug("Training with GPUs")
        # pass detect_anomaly=True to check gradients
        trainer = Trainer(logger = logger, accelerator = "cuda", num_nodes = 1, 
                          check_val_every_n_epoch = pm.valid_rate, num_sanity_val_steps = 1,
                          devices = pm.gpu_list, max_epochs = pm.num_epochs, 
                          deterministic=True, enable_progress_bar=True, enable_model_summary=True,
                          default_root_dir = pm.path_root, callbacks = [checkpoint_callback]
                          )

    else:
        logging.debug("Training with CPUs")
        trainer = Trainer(logger = logger, accelerator = "cpu", max_epochs = pm.num_epochs, 
                          num_sanity_val_steps = 0, default_root_dir = pm.path_results, 
                          check_val_every_n_epoch = pm.valid_rate, callbacks = [checkpoint_callback])

    # Train
   
    trainer.fit(model,data) # this calls train_step() and valid_step()
    
    trainer.test(model, dataloaders=[data.val_dataloader(),data.train_dataloader()]) # this calls model.test_step. 

    # Dump config
    yaml.dump(params, open(os.path.join(pm.path_root, f'{pm.path_results}/params.yaml'),'w'))

if __name__=="__main__":
    import yaml
    import torch
    import argparse
    import matplotlib.pyplot as plt
    from utils import parameter_manager
    from pytorch_lightning import seed_everything
    logging.basicConfig(level=logging.ERROR)
    parser = argparse.ArgumentParser()
    parser.add_argument("-config", help = "Experiment: Train and Eval LRN Network")
    args = parser.parse_args()
    if(args.config == None):
        logging.error("\nAttach Configuration File! Run experiment.py -h\n")
        exit()

    params = yaml.load(open(args.config), Loader = yaml.FullLoader)

    run(params)
