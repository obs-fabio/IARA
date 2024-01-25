"""
Training Configuration Test Program

This script generates a sample training configuration for testing functionality.
In the future, this test script will be part of an application designed to create training
    configurations as described in the associated article.
"""
import iara.trainer
import iara.description
import iara.processing.analysis as iara_proc
import iara.processing.dataset as iara_data_proc


def main(override: bool = False, only_first_fold = True):
    """Main function for the test Training Configuration."""

    dp = iara_data_proc.DatasetProcessor(
        data_base_dir = "./data/raw_dataset",
        data_processed_base_dir = "./data/processed",
        normalization = iara_proc.Normalization.NORM_L2,
        analysis = iara_proc.SpectralAnalysis.LOFAR,
        n_pts = 640,
        n_overlap = 0,
        decimation_rate = 3,
    )

    config_dir = "./results/configs"
    config_name = "test_training"

    config = False
    if not override:
        try:
            config = iara.trainer.TrainingConfig.load(config_dir, config_name)

        except FileNotFoundError:
            pass

    if not config:
        # dataset = iara.description.CustomDataset(
        #                 dataset_type = iara.description.DatasetType.OS_CPA_IN,
        #                 target = iara.description.DatasetTarget(
        #                     column = 'TYPE',
        #                     values = ['Cargo', 'Tanker', 'Tug'], # , 'Passenger'
        #                     include_others = False
        #                 ),
        #                 only_sample=True
        #             )
        dataset = iara.description.CustomDataset(
                        dataset_type = iara.description.DatasetType.OS_CPA_IN,
                        target = iara.description.DatasetTarget(
                            column = 'DETAILED TYPE',
                            values = ['Bulk Carrier', 'Container Ship'],
                            include_others = True
                        ),
                        filters = [
                            iara.description.DatasetFilter(
                                column = 'Rain state',
                                values = ['No rain']),
                            iara.description.DatasetFilter(
                                column = 'TYPE',
                                values = ['Cargo']),
                        ]
                    )

        config = iara.trainer.TrainingConfig(
                        name = config_name,
                        dataset = dataset,
                        dataset_processor = dp,
                        output_base_dir = "./results/trainings",
                        n_folds=3)

        config.save(config_dir)

    print(config)

    trainer = iara.trainer.Trainer(config)
    trainer.run(only_first_fold = only_first_fold)


if __name__ == "__main__":
    main()
