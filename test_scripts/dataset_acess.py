import enum
import os
import pandas as pd
import itertools
import shutil

import iara.records
import iara.ml.experiment as iara_exp
import iara.ml.models.trainer as iara_trn
import iara.ml.metrics as iara_metrics
import iara.ml.dataset as iara_dataset
import iara.processing.analysis as iara_proc
import iara.processing.manager as iara_manager

import iara.default as iara_default
from iara.default import DEFAULT_DIRECTORIES


def get_shipsear_id(file:str) -> int:
    return int(file.split('_')[0])

class OtherCollections(enum.Enum):
    SHIPSEAR = 0
    DEEPSHIP = 1

    def __str__(self) -> str:
        return str(self.name).rsplit(".", maxsplit=1)[-1].lower()

    def _get_info_filename(self, only_sample: bool = False) -> str:
        return os.path.join("./training_scripts/dataset_info",
                            f"{str(self)}.csv" if not only_sample else f"{str(self)}_sample.csv")

    def to_df(self, only_sample: bool = False) -> pd.DataFrame:
        df = pd.read_csv(self._get_info_filename(only_sample=only_sample), na_values=[" - "])
        return df

# for collection in OtherCollections:
#     print(f'########## {collection} ##########')
#     print(collection.to_df())

print(OtherCollections.SHIPSEAR.to_df())


collection = iara.records.CustomCollection(
        collection = OtherCollections.SHIPSEAR,
        target = iara.records.LabelTarget(column='Class',
                                          values=['A', 'B', 'C', 'D', 'E'],
                                          include_others=False),
        only_sample=False
    )

print(collection.to_df())
print(collection.to_compiled_df())


config_name = f'shipsear'
output_base_dir = f"{DEFAULT_DIRECTORIES.training_dir}/data_acess"
data_base_dir = "./data/shipsear"
data_processed_base_dir = "./data/shipsear_processed"

if os.path.exists(data_processed_base_dir):
    shutil.rmtree(data_processed_base_dir)

dataset_processor = iara_manager.AudioFileProcessor(
        data_base_dir = data_base_dir,
        data_processed_base_dir = data_processed_base_dir,
        normalization = iara_proc.Normalization.MIN_MAX,
        analysis = iara_proc.SpectralAnalysis.LOG_MELGRAM,
        n_pts = 1024,
        n_overlap = 0,
        decimation_rate = 3,
        n_mels=256,
        integration_interval=0.512,
        extract_id = get_shipsear_id
    )

dataset_processor.plot(file_id=collection.to_df()['ID'].to_list(),
                       plot_type=iara_manager.PlotType.EXPORT_PLOT,
                       frequency_in_x_axis=True,
                       override=False)

config = iara_exp.Config(
            name = config_name,
            dataset = collection,
            dataset_processor = dataset_processor,
            output_base_dir = output_base_dir,
            input_type = iara_default.default_window_input(),
            exclusive_header=None)

trainers = iara_default.get_default_mel_trainers(config.dataset.target.get_n_targets())

manager = iara_exp.Manager(config, *trainers)

result_dict = manager.run()

result_grid = {}
for eval_subset, eval_strategy in itertools.product(iara_trn.Subset, iara_trn.EvalStrategy):
    result_grid[eval_subset, eval_strategy] = iara_metrics.GridCompiler()

for (eval_subset, eval_strategy), grid in result_grid.items():

    for trainer_id, results in result_dict[eval_subset, eval_strategy].items():

        for i_fold, result in enumerate(results):

            grid.add(params={'ID': trainer_id},
                        i_fold=i_fold,
                        target=result['Target'],
                        prediction=result['Prediction'])

for dataset_id, grid in result_grid.items():
    print(f'########## {dataset_id} ############')
    print(grid.print_cm())
    print(grid)
