import os
import pathlib

# pylint: disable=too-many-statements


class Config:
    _config = None

    @classmethod
    def get(
        cls,
        root_dir=os.getenv(
            "KAGGLE_DATA_DIR", "/home/karajan/labzone/kaggle/common-lit-kaggle/data"
        ),
        input_dir=None,
        output_dir=None,
        sentence_transformer="sentence-transformers/all-MiniLM-L6-v2",
        zero_shot_model="facebook/bart-large-mnli",
        train_prompts=None,
        test_prompts=None,
        used_features=None,
        bart_model="facebook/bart-base",
        run_with_small_sample=False,
        num_train_epochs=50,
        batch_size=12,
        save_checkpoints=True,
        learning_rate=0.0000005,
        gradient_accumulation_steps=10,  # added this line
    ):
        if cls._config is None:
            Config._config = cls(
                root_dir,
                input_dir,
                output_dir,
                sentence_transformer,
                zero_shot_model,
                train_prompts,
                test_prompts,
                used_features,
                bart_model,
                run_with_small_sample,
                num_train_epochs,
                batch_size,
                save_checkpoints,
                learning_rate,
                gradient_accumulation_steps,  # and this line
            )

        return Config._config

    def __init__(
        self,
        root_dir,
        input_dir,
        output_dir,
        sentence_transformer,
        zero_shot_model,
        train_prompts,
        test_prompts,
        used_features,
        bart_model,
        run_with_small_sample,
        num_train_epochs,
        batch_size,
        save_checkpoints,
        learning_rate,
        gradient_accumulation_steps,  # and this line
    ) -> None:
        # Config parameters that end with _dir are automatically created by the 'main.py' script.
        self.data_root_dir = pathlib.Path(root_dir)

        if input_dir:
            self.data_input_dir = input_dir
        else:
            self.data_input_dir = pathlib.Path(self.data_root_dir / "input")

        self.data_intermediate_dir = pathlib.Path(self.data_root_dir / "intermediate")
        self.data_exploration_dir = pathlib.Path(self.data_root_dir / "exploration")
        self.data_train_dir = pathlib.Path(self.data_root_dir / "train")
        self.data_test_dir = pathlib.Path(self.data_root_dir / "test")
        self.plots_dir = pathlib.Path(self.data_root_dir / "plots")
        self.models_root_dir = pathlib.Path(self.data_root_dir / "models")
        self.checkpoints_dir = pathlib.Path(self.data_root_dir / "checkpoints")

        # Bart Base
        self.batch_size = batch_size
        self.bart_model = bart_model
        self.gradient_accumulation_steps = gradient_accumulation_steps  # and this line

        if "bart-base" in bart_model:
            self.string_truncation_length = (
                1500  # value set on trial and error, until it stopped issuing warnings
            )
            self.model_context_length = 768
        elif "bart-large" in bart_model:
            # Large bart
            self.model_context_length = 1024
            self.string_truncation_length = (
                2700  # value set on trial and error, until it stopped issuing warnings
            )
        else:
            raise ValueError(
                f"Unknown model: '{bart_model}'. Could not set preprocessing parameters."
            )

        # Shared bart parameters
        self.save_checkpoints = save_checkpoints
        self.num_train_epochs = num_train_epochs
        self.learning_rate = learning_rate
        self.num_of_labels = 2
        self.run_with_small_sample = run_with_small_sample
        self.small_sample_size = 10

        if output_dir:
            self.data_output_dir = output_dir
        else:
            self.data_output_dir = pathlib.Path(self.data_root_dir / "output")

        # Only used for basic_ml pipelines
        self.sentence_transformer = sentence_transformer
        self.distance_metric = "euclidean"
        self.distance_stategy = "minimum"

        self.used_features = [
            "text_length",
            "word_count",
            "sentence_count",
            "unique_words",
            "word_intersection",
            "prompt_length",
            "prompt_word_count",
            "prompt_sentence_count",
            "prompt_unique_words",
        ]

        if used_features:
            self.used_features = used_features

        self.zero_shot_model = zero_shot_model

        self.available_prompts = [
            "3b9047",
            "39c16e",
            "ebad26",
            "814d6b",
        ]

        # Default configuration locally, uses only one of the prompts for training
        self.train_prompts = ["3b9047", "39c16e"]
        self.test_prompts = [
            "ebad26",
            "814d6b",
        ]

        if train_prompts is not None:
            self.train_prompts = train_prompts

        if test_prompts is not None:
            self.test_prompts = test_prompts

        assert (
            len(self.train_prompts) > 0
        ), "At least one prompt must be used for training!"
        train = len(self.train_prompts)
        test = len(self.test_prompts)
        available = len(self.available_prompts)
        assert (
            train + test <= available
        ), f"Invalid prompt configuration! {train} + {test} > {available}"

        self.device = "cuda:0"
        self.random_state = 42
